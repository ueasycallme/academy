# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""把 Galbot One Golf 的 URDF 转成 USD（6.1.2）。

默认转换固定底座版 URDF，输出到 <GALBOT_GENERATED_DIR>/galbot_fixed_base/galbot.usd。

用法（项目根目录）::

    python scripts/convert_galbot.py --headless
    python scripts/convert_galbot.py --headless --variant wheeled     # 对照：轮式 URDF + fix_base
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="把 Galbot One Golf 的 URDF 转成 USD")
parser.add_argument("--variant", choices=["fixed_base", "wheeled"], default="fixed_base", help="用哪个预置 URDF")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg

from galbot_academy.assets import galbot_description_dir, generated_asset_dir

URDF_FILES = {"fixed_base": "galbot_one_golf_fixed_base.urdf", "wheeled": "galbot_one_golf.urdf"}

# 驱动增益（N·m/rad 与 N·m·s/rad），只求能让机器人在重力下站住，细调见 6.1.5。
# 按正则写的字典在 URDF 转换器里按顺序应用，后面的键覆盖前面的：先通配，后特例。
# （Isaac Lab 的 ArticulationCfg.actuators 规则相反，键重叠会报错，见 6.1.6。）
STIFFNESS = {".*": 400.0, "leg_joint[1-3]": 4000.0, ".*_gripper_joint": 100.0}
DAMPING = {".*": 40.0, "leg_joint[1-3]": 400.0, ".*_gripper_joint": 10.0}


def make_cfg() -> UrdfConverterCfg:
    out_dir = generated_asset_dir() / f"galbot_{args.variant}"
    # 字典里的每个正则键都必须匹配到至少一个关节，否则转换器抛 ValueError（而进程返回码仍为 0）。
    # 固定底座版 URDF 没有被动滚子，所以只在轮式版里加这一项；被动滚子不加驱动。
    target_type = {".*": "position"}
    if args.variant == "wheeled":
        target_type["wheel_.*_passive_.*"] = "none"
    return UrdfConverterCfg(
        asset_path=str(galbot_description_dir() / "urdf" / URDF_FILES[args.variant]),
        usd_dir=str(out_dir),
        usd_file_name="galbot.usd",
        force_usd_conversion=True,
        fix_base=True,  # reach 任务用固定底座：把根连杆 base_link 固定到世界
        merge_fixed_joints=True,  # 合并固定关节两侧的连杆（会有 26–30 条弃用警告，属预期）
        # 字段名与效果相反：v2.3.2 中为 True 时才保留 URDF 的 mimic 关系（6.1.2"常见坑"）
        convert_mimic_joints_to_normal_joints=True,
        collider_type="convex_hull",
        self_collision=False,  # 先关闭，需要时在 ArticulationCfg 里再开
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            drive_type="force",
            target_type=target_type,  # mimic 跟随关节由 mimic 约束带动，转换器不会给它们加驱动
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=STIFFNESS, damping=DAMPING),
        ),
    )


# mimic 约束的"刚度"：URDF 导入器把关节驱动的 naturalFrequency / dampingRatio（默认 25 / 0.005）写进
# physxMimicJoint:*，约束很软，夹爪在重力下跟不住主动关节（6.1.2 实测）。转换后改成下面的值。
MIMIC_NATURAL_FREQUENCY = 1000.0
MIMIC_DAMPING_RATIO = 1.0


def stiffen_mimic_joints(usd_path: str) -> int:
    """把所有 mimic 约束的 naturalFrequency / dampingRatio 改为上面的值，写入入口 USD 的根层；返回修改的关节数。"""
    from pxr import Usd

    stage = Usd.Stage.Open(usd_path)
    count = 0
    for prim in stage.Traverse():
        for attr in prim.GetAttributes():
            name = attr.GetName()
            if name.startswith("physxMimicJoint:") and name.endswith(":naturalFrequency"):
                attr.Set(MIMIC_NATURAL_FREQUENCY)
                prim.GetAttribute(name.replace(":naturalFrequency", ":dampingRatio")).Set(MIMIC_DAMPING_RATIO)
                count += 1
    stage.GetRootLayer().Save()
    return count


def main() -> None:
    converter = UrdfConverter(make_cfg())
    count = stiffen_mimic_joints(converter.usd_path)
    print(f"Generated USD file: {converter.usd_path}")
    print(f"mimic 关节 {count} 个：naturalFrequency = {MIMIC_NATURAL_FREQUENCY}，dampingRatio = {MIMIC_DAMPING_RATIO}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
