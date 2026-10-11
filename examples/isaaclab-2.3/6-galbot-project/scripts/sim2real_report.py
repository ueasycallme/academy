# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11 标准库（给 --traj 时另需 numpy）；读 6.7.1 生成的 policy_spec.json 与 Galbot 描述仓库（commit 2d496b0）的 URDF；不需要 Isaac Sim
# 验证日期：2026-10-11（越限计数同日加）
"""打印 reach 策略交给机器人侧时要核对的接口常量（6.7.3）：关节名序、URDF 限位、动作换算、控制频率、超时策略。

关节目标 = offset + scale × 动作。策略输出没有裁剪（6.7.1），所以这里按评估轨迹里出现过的动作范围，
算出目标会不会越过 URDF 的位置限位，给"安全"一组清单项用。

    python scripts/sim2real_report.py --spec logs/rsl_rl/galbot_reach/<运行>/deploy/policy_spec.json \
        --urdf third_party/galbot_one_golf_description/urdf/galbot_one_golf_fixed_base.urdf [--traj traj.npz]
    # traj.npz：eval_reach.py --num_envs 256 --record_obs traj.npz --record_envs 256（6.7.1）
"""

import argparse
import json
import xml.etree.ElementTree as ET

TIMEOUT_S = 1.0  # scripts/run_ros2_sim.py --timeout 的默认值：等一个动作的墙上时间上限，超时保持上一步动作（6.7.2）


def main() -> None:
    parser = argparse.ArgumentParser(description="打印 sim2real 要核对的接口常量")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--urdf", required=True)
    parser.add_argument("--traj", default=None, help="eval_reach.py --record_obs 存下的 .npz：用其中的动作估计关节目标范围")
    args = parser.parse_args()

    spec = json.load(open(args.spec))
    joints = {j.get("name"): j for j in ET.parse(args.urdf).getroot().iter("joint")}
    act = spec["action"]
    print(f"[sim2real] 控制：{spec['control']['frequency_hz']} Hz（物理步 {spec['control']['physics_dt']:.5f} s × decimation "
          f"{spec['control']['decimation']}）；观测 {spec['observation']['dim']} 维，归一化在模型里：{spec['model']['obs_normalization_in_model']}")
    print(f"[sim2real] 动作：{act['formula']}，scale {act['scale']}，裁剪 {act['clip']}；超时 {TIMEOUT_S} s 后保持上一步动作")
    a_lo = a_hi = None
    if args.traj:
        import numpy as np

        acts = np.load(args.traj)["actions"]  # (步数, 环境数, 7)
        a = acts.reshape(-1, act["dim"])
        a_lo, a_hi = a.min(axis=0), a.max(axis=0)
    print("[sim2real] 关节                 默认      URDF 下限  URDF 上限  速度上限   力矩上限" + ("  轨迹中的目标范围" if args.traj else ""))
    for i, name in enumerate(act["joint_names"]):
        lim = joints[name].find("limit")
        lo, hi = float(lim.get("lower")), float(lim.get("upper"))
        line = (f"  {name:18s} {act['offset'][i]:+8.3f}  {lo:+9.3f}  {hi:+9.3f}  {float(lim.get('velocity')):8.2f}  "
                f"{float(lim.get('effort')):8.1f}")
        if a_lo is not None:
            t_lo, t_hi = act["offset"][i] + act["scale"] * a_lo[i], act["offset"][i] + act["scale"] * a_hi[i]
            flag = "  越限" if t_lo < lo or t_hi > hi else ""
            line += f"  [{t_lo:+.3f}, {t_hi:+.3f}]{flag}"
        print(line)
    if args.traj:
        # 越限统计：按步（环境步）、按环境、按关节
        lo = np.array([float(joints[n].find("limit").get("lower")) for n in act["joint_names"]])
        hi = np.array([float(joints[n].find("limit").get("upper")) for n in act["joint_names"]])
        target = np.asarray(act["offset"]) + act["scale"] * acts  # (步数, 环境数, 7)
        excess = np.maximum(lo - target, target - hi)  # > 0 表示越限的量（rad）
        over = excess > 0
        any_j = over.any(axis=2)  # (步数, 环境数)
        T, N = any_j.shape
        frac = any_j.mean(axis=0)
        print(f"[sim2real] 越限（{N} 个环境 × {T} 步）：按步 {any_j.sum()} / {T * N}（{any_j.mean() * 100:.1f}%）；"
              f"按环境 {int((frac > 0).sum())} / {N}（{(frac > 0).mean() * 100:.1f}%）至少有一步越限；"
              f"每个环境的越限步占比 中位 {np.median(frac) * 100:.1f}%、90% 分位 {np.quantile(frac, 0.9) * 100:.1f}%、最大 {frac.max() * 100:.1f}%")
        for i, name in enumerate(act["joint_names"]):
            if over[:, :, i].any():
                print(f"  {name}：越限 {int(over[:, :, i].sum())} 个环境步、{int(over[:, :, i].any(axis=0).sum())} 个环境，最大超出 {excess[:, :, i].max():.3f} rad")


if __name__ == "__main__":
    main()
