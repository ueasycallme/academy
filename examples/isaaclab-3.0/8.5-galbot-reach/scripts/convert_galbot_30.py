# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0（URDF importer 3.0）；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
"""用 3.0 EA 自带的 URDF 转换器重新转换 Galbot（8.5），供 Newton 后端使用。

5.1 转换出的 USD 在 Newton 下用不了（8.5 实测：一处悬空引用；碰撞 API 加在 Xform 上，Newton 不认，随后崩溃）。
EA 文档 prepare_asset_for_newton.rst 的建议是用 3.0 的转换器重新导入，保留 run_asset_transformer 与
run_multi_physics_conversion（默认都为 True），生成中性物理、PhysX、MuJoCo 三份属性。

转换参数照搬 2.3 的 convert_galbot.py（6.1.2），差别：
- 碰撞近似字段改名为 collision_type（"Convex Hull"）；
- convert_mimic_joints_to_normal_joints 在 importer 3.0 中已弃用，不再设置；
- 转换后同样把 mimic 约束调硬、写入 7 对自碰撞过滤对（6.1.2、6.1.4），只改 PhysX 的属性。

    python scripts/convert_galbot_30.py
"""

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="用 3.0 的转换器转换 Galbot（固定底座）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = True
simulation_app = AppLauncher(args).app

from pxr import Usd  # noqa: E402

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg  # noqa: E402

from galbot_academy.assets import galbot_description_dir, generated_asset_dir  # noqa: E402
from galbot_academy.assets.physics import add_filtered_pairs  # noqa: E402

STIFFNESS = {".*": 400.0, "leg_joint[1-3]": 4000.0, ".*_gripper_joint": 100.0}
DAMPING = {".*": 40.0, "leg_joint[1-3]": 400.0, ".*_gripper_joint": 10.0}
MIMIC_NATURAL_FREQUENCY = 1000.0
MIMIC_DAMPING_RATIO = 1.0


def main() -> None:
    cfg = UrdfConverterCfg(
        asset_path=str(galbot_description_dir() / "urdf" / "galbot_one_golf_fixed_base.urdf"),
        usd_dir=str(generated_asset_dir() / "galbot_fixed_base_30"),
        usd_file_name="galbot.usd",
        force_usd_conversion=True,
        fix_base=True,
        merge_fixed_joints=True,
        collision_type="Convex Hull",
        self_collision=False,
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            drive_type="force",
            target_type="position",
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=STIFFNESS, damping=DAMPING),
        ),
    )
    converter = UrdfConverter(cfg)
    stage = Usd.Stage.Open(converter.usd_path)
    mimic = 0
    for prim in stage.Traverse():
        for attr in prim.GetAttributes():
            name = attr.GetName()
            if name.startswith("physxMimicJoint:") and name.endswith(":naturalFrequency"):
                attr.Set(MIMIC_NATURAL_FREQUENCY)
                prim.GetAttribute(name.replace(":naturalFrequency", ":dampingRatio")).Set(MIMIC_DAMPING_RATIO)
                mimic += 1
    pairs = add_filtered_pairs(stage, stage.GetDefaultPrim().GetPath().pathString)
    stage.GetRootLayer().Save()
    errors = len(Usd.Stage.Open(converter.usd_path).GetCompositionErrors())
    print(f"[8.5] 3.0 转换输出：{converter.usd_path}")
    print(f"[8.5] PhysX mimic 约束 {mimic} 个改为 naturalFrequency {MIMIC_NATURAL_FREQUENCY}；自碰撞过滤对 {pairs} 对；组合错误 {errors} 个")


if __name__ == "__main__":
    main()
    simulation_app.close()
