# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0（commit e3f7d9ff1）+ Isaac Sim 6.2.0（PhysX）/ Newton 1.6.1；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""打印 Galbot reach 在当前物理后端下的关节 / 刚体顺序与策略观测的布局（8.10）。

Isaac Lab 3.0 的 ArticulationCfg 默认 joint_ordering = body_ordering = None，即"用后端自己的顺序"。
同一个检查点换后端前，先在两个后端各跑一次本脚本，把输出对照：观测向量里的关节量是否按同样的顺序排列。
输出一行 JSON（ORDER {...}），便于两份对比。

    python scripts/print_ordering.py physics=isaacsim_physx > order_physx.txt
    python scripts/print_ordering.py physics=newton_mjwarp  > order_newton.txt
"""

import argparse
import json
import sys

from isaaclab.app import add_launcher_args, launch_simulation
from isaaclab.utils.string import list_intersection

from isaaclab_rl.entrypoints.common import add_frontend_args, create_isaaclab_env

from isaaclab_tasks.utils import setup_preset_cli
from isaaclab_tasks.utils import resolve_task_config

import galbot_academy

parser = argparse.ArgumentParser(description="打印关节 / 刚体顺序（8.10）")
parser.add_argument("--task", default="Galbot-Reach-Play")
parser.add_argument("--agent", default="rsl_rl_cfg_entry_point")
add_launcher_args(parser)
add_frontend_args(parser)
args, remaining = setup_preset_cli(parser)
galbot_academy.register_tasks()
sys.argv = [sys.argv[0]] + list_intersection(remaining, None)


def main(env_cfg, agent_cfg) -> None:
    with launch_simulation(env_cfg, args):
        env_cfg.scene.num_envs = 2
        env = create_isaaclab_env(args.task, env_cfg, args, convert_marl_to_single_agent=False)
        base = env.unwrapped
        robot = base.scene["robot"]
        om = base.observation_manager
        layout = []
        for name, cfg in zip(om.active_terms["policy"], om._group_obs_term_cfgs["policy"]):
            ac = cfg.params.get("asset_cfg")
            joints = None
            if ac is not None and getattr(ac, "joint_ids", None) is not None and ac.joint_ids != slice(None):
                joints = [robot.joint_names[i] for i in ac.joint_ids]
            layout.append({"term": name, "joints": joints})
        out = {
            "physics": type(base.sim.cfg.physics).__name__,
            "joint_names": list(robot.joint_names),
            "backend_joint_names": list(getattr(robot, "backend_joint_names", robot.joint_names)),
            "body_names": list(robot.body_names),
            "joint_ordering": None if robot.joint_ordering is None else "permutation",
            "policy_obs": layout,
            "obs_dim": list(om.group_obs_dim["policy"]),
        }
        print("ORDER " + json.dumps(out, ensure_ascii=False), flush=True)
        env.close()


if __name__ == "__main__":
    # 3.0 正式版删除了 hydra_task_config 装饰器，改为显式解析（读 sys.argv 里的预设与覆盖项）
    main(*resolve_task_config(args.task, args.agent))
