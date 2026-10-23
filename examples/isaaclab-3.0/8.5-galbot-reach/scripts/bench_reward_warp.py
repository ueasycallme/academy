# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0（commit e3f7d9ff1），warp-lang 1.17.0，rsl-rl-lib 5.5.1；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""TCP 位置误差奖励：torch 版与 Warp 内核版的逐步比对与计时（8.9）。

1. 比对：加载一个检查点，用策略推进 --compare_steps 步；每步在同一状态上分别调用两版，记最大绝对误差与最大相对误差。
2. 计时：在最后的状态上，两版各调用 --calls 次（每次前后 torch.cuda.synchronize），取中位数；
   再推进 --calls 步，记整个 env.step 的中位耗时，算两版各占一步的比例。

    python scripts/bench_reward_warp.py --checkpoint <运行>/model_199.pt --num_envs 1024 physics=newton_mjwarp
"""

import argparse
import statistics
import time

import gymnasium as gym
import torch
import warp as wp

from isaaclab.app import add_launcher_args, launch_simulation

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import resolve_task_config, setup_preset_cli

import galbot_academy  # noqa: F401
galbot_academy.register_tasks()

from galbot_academy.tasks.reach.mdp.rewards import tcp_position_error  # noqa: E402
from galbot_academy.tasks.reach.mdp.rewards_warp import tcp_position_error_warp  # noqa: E402

parser = argparse.ArgumentParser(description="奖励项 torch 版 vs Warp 版（8.9）")
parser.add_argument("--task", default="Galbot-Reach")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=1024)
parser.add_argument("--compare_steps", type=int, default=200)
parser.add_argument("--calls", type=int, default=200)
parser.add_argument("--seed", type=int, default=0)
add_launcher_args(parser)
args_cli, hydra_args = setup_preset_cli(parser)


def timed(fn, n: int) -> list[float]:
    out = []
    for _ in range(n):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        fn()
        torch.cuda.synchronize()
        out.append((time.perf_counter() - t0) * 1e3)
    return out


def main() -> None:
    from rsl_rl.runners import OnPolicyRunner

    import importlib.metadata as metadata

    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg

    env_cfg, agent_cfg = resolve_task_config(args_cli.task, "rsl_rl_cfg_entry_point", overrides=hydra_args)
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.seed = args_cli.seed
    # 与 isaaclab play 相同：按已装的 rsl_rl 版本改写配置（play_rsl_rl.py 也这样做），否则 5.x 的模型类不认旧字段
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, metadata.version("rsl-rl-lib"))
    with launch_simulation(env_cfg, args_cli):
        env = RslRlVecEnvWrapper(gym.make(args_cli.task, cfg=env_cfg))
        base = env.unwrapped
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=base.device)
        runner.load(args_cli.checkpoint)
        policy = runner.get_inference_policy(device=base.device)
        params = base.reward_manager.get_term_cfg("end_effector_position_tracking").params
        # 奖励管理器构造时已 resolve 并把索引移到设备上（3.0 正式版的 finalize）；再 resolve 一次会报 body_ids 不一致
        robot = base.scene[params["asset_cfg"].name]
        print(f"[8.9] {args_cli.num_envs} 个环境；数据类型：body_pos_w {robot.data.body_pos_w.warp.dtype.__name__} "
              f"{tuple(robot.data.body_pos_w.warp.shape)}，root_quat_w {robot.data.root_quat_w.warp.dtype.__name__}", flush=True)

        def f_torch():
            return tcp_position_error(base, **params)

        def f_warp():
            return tcp_position_error_warp(base, **params)

        # 第一次调用 Warp 版：包括编译 / 载入内核
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        f_warp()
        torch.cuda.synchronize()
        print(f"[8.9] Warp 版第一次调用（含内核编译或从缓存载入）{(time.perf_counter() - t0) * 1e3:.1f} ms", flush=True)

        obs = env.get_observations()
        max_abs = max_rel = 0.0
        exact = 0
        with torch.inference_mode():
            for _ in range(args_cli.compare_steps):
                obs, _, _, _ = env.step(policy(obs))
                a, b = f_torch(), f_warp()
                d = (a - b).abs()
                max_abs = max(max_abs, d.max().item())
                max_rel = max(max_rel, (d / a.abs().clamp_min(1e-6)).max().item())
                exact += int(torch.equal(a, b))
        print(f"[8.9] 比对 {args_cli.compare_steps} 步 × {args_cli.num_envs} 个环境：最大绝对误差 {max_abs:.3e} m，"
              f"最大相对误差 {max_rel:.3e}；逐位相同的步数 {exact}/{args_cli.compare_steps}", flush=True)

        # 坑：Warp 版返回的是固定输出缓冲的零拷贝视图，留到下一步再看，值已经被覆盖
        with torch.inference_mode():
            kept = f_warp()
            kept_copy = kept.clone()
            obs, _, _, _ = env.step(policy(obs))
            new = f_warp()
            print(f"[8.9] 留着上一步的 Warp 结果：与本步共用内存 {kept.data_ptr() == new.data_ptr()}，"
                  f"内容已变 {not torch.equal(kept, kept_copy)}", flush=True)

        with torch.inference_mode():
            t_torch = timed(f_torch, args_cli.calls)
            t_warp = timed(f_warp, args_cli.calls)
            step_times = []
            for _ in range(args_cli.calls):
                act = policy(obs)
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                obs, _, _, _ = env.step(act)
                torch.cuda.synchronize()
                step_times.append((time.perf_counter() - t0) * 1e3)
        mt, mw, ms = statistics.median(t_torch), statistics.median(t_warp), statistics.median(step_times)
        print(f"[8.9] 单次调用中位：torch {mt:.4f} ms（{min(t_torch):.4f}–{max(t_torch):.4f}），"
              f"Warp {mw:.4f} ms（{min(t_warp):.4f}–{max(t_warp):.4f}），各 {args_cli.calls} 次", flush=True)
        print(f"[8.9] env.step 中位 {ms:.3f} ms；这一项占一步：torch {mt / ms * 100:.2f}%，Warp {mw / ms * 100:.2f}%", flush=True)
        env.close()


if __name__ == "__main__":
    main()
