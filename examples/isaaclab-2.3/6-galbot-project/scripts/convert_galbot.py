# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30（参数移到 assets/conversion.py、末尾写资产清单为 6.1.7 所改，验证日期 2026-10-11；轮式版写滚子过滤对为 6.4.5 所加，验证日期 2026-10-11）
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""把 Galbot One Golf 的 URDF 转成 USD（6.1.2）。

默认转换固定底座版 URDF，输出到 <GALBOT_GENERATED_DIR>/galbot_fixed_base/galbot.usd。

用法（项目根目录）::

    python scripts/convert_galbot.py --headless
    python scripts/convert_galbot.py --headless --variant wheeled     # 对照：轮式 URDF + fix_base
    python scripts/convert_galbot.py --headless --variant wheeled --floating_base   # 移动底盘用：根不固定（6.1.6）
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="把 Galbot One Golf 的 URDF 转成 USD")
parser.add_argument("--variant", choices=["fixed_base", "wheeled"], default="fixed_base", help="用哪个预置 URDF")
parser.add_argument("--floating_base", action="store_true", help="根不固定到世界，输出到 galbot_<variant>_floating（6.1.6）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg

from galbot_academy.assets import galbot_description_dir, generated_asset_dir
from galbot_academy.assets.conversion import (  # 参数集中在这里，资产清单（6.1.7）不启动 Isaac Sim 也能读
    CONVERTER_OPTIONS,
    MIMIC_DAMPING_RATIO,
    MIMIC_NATURAL_FREQUENCY,
    URDF_FILES,
    gains,
    variant_dir_name,
)
from galbot_academy.assets.manifest import write_manifest



def make_cfg() -> UrdfConverterCfg:
    out_dir = generated_asset_dir() / variant_dir_name(args.variant, args.floating_base)
    # 字典里的每个正则键都必须匹配到至少一个关节，否则转换器抛 ValueError（而进程返回码仍为 0）。
    # 固定底座版 URDF 没有被动滚子，所以只在轮式版里加滚子的键（conversion.gains）。
    stiffness, damping = gains(args.variant)
    opt = CONVERTER_OPTIONS
    return UrdfConverterCfg(
        asset_path=str(galbot_description_dir() / "urdf" / URDF_FILES[args.variant]),
        usd_dir=str(out_dir),
        usd_file_name="galbot.usd",
        force_usd_conversion=True,
        fix_base=not args.floating_base,  # reach 任务用固定底座：把根连杆 base_link 固定到世界
        merge_fixed_joints=opt["merge_fixed_joints"],  # 合并固定关节两侧的连杆（会有 26–30 条弃用警告，属预期）
        # 字段名与效果相反：v2.3.2 中为 True 时才保留 URDF 的 mimic 关系（6.1.2"常见坑"）
        convert_mimic_joints_to_normal_joints=opt["convert_mimic_joints_to_normal_joints"],
        collider_type=opt["collider_type"],
        self_collision=opt["self_collision"],  # 先关闭，需要时在 ArticulationCfg 里再开
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            drive_type=opt["drive_type"],
            target_type=opt["target_type"],  # mimic 跟随关节由 mimic 约束带动，转换器不会给它们加驱动
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=stiffness, damping=damping),
        ),
    )


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


def filter_self_collision_pairs(usd_path: str) -> int:
    """把 6.1.4 的自碰撞过滤对写入入口 USD 的根层；轮式版另加同一轮内滚子之间的过滤对（6.4.5）。返回写入的对数。
    自碰撞本身仍关闭，由 ArticulationCfg 决定开不开。"""
    from pxr import Usd

    from galbot_academy.assets.physics import ROLLER_FILTERED_PAIRS, add_filtered_pairs

    stage = Usd.Stage.Open(usd_path)
    root = stage.GetDefaultPrim().GetPath().pathString
    count = add_filtered_pairs(stage, root)
    if args.variant == "wheeled":
        count += add_filtered_pairs(stage, root, ROLLER_FILTERED_PAIRS)
    stage.GetRootLayer().Save()
    return count


def main() -> None:
    converter = UrdfConverter(make_cfg())
    count = stiffen_mimic_joints(converter.usd_path)
    pairs = filter_self_collision_pairs(converter.usd_path)  # 6.1.4 加入
    print(f"Generated USD file: {converter.usd_path}")
    print(f"mimic 关节 {count} 个：naturalFrequency = {MIMIC_NATURAL_FREQUENCY}，dampingRatio = {MIMIC_DAMPING_RATIO}")
    print(f"自碰撞过滤对 {pairs} 对")
    path = write_manifest(args.variant, args.floating_base)  # 6.1.7：来源、工具链、参数、输出文件的 sha256
    print(f"资产清单：{path}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
