# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（不依赖 Isaac Sim）
# 验证日期：2026-10-11
"""URDF → USD 转换的全部参数（6.1.2 起，6.1.7 从 convert_galbot.py 移到这里）。

放在不依赖 Kit 的模块里，是为了让 scripts/asset_manifest.py 不启动 Isaac Sim 也能拿"代码里现在的参数"
去和 generated/<变体>/MANIFEST.json 里记录的参数比对：参数改了而 USD 没重新生成，校验会报出来。
"""

URDF_FILES = {"fixed_base": "galbot_one_golf_fixed_base.urdf", "wheeled": "galbot_one_golf.urdf"}

# 驱动增益（N·m/rad 与 N·m·s/rad），只求能让机器人在重力下站住，细调见 6.1.5。
# 按正则写的字典在 URDF 转换器里按顺序应用，后面的键覆盖前面的：先通配，后特例。
# （Isaac Lab 的 ArticulationCfg.actuators 规则相反，键重叠会报错，见 6.1.6。）
STIFFNESS = {".*": 400.0, "leg_joint[1-3]": 4000.0, ".*_gripper_joint": 100.0}
DAMPING = {".*": 40.0, "leg_joint[1-3]": 400.0, ".*_gripper_joint": 10.0}

# 轮式 URDF 的 40 个全向轮被动滚子：零刚度 + 小阻尼，让滚子自由转动、只带一点阻尼（经验性选择）。
# 注意：这不是 NaN 的修复。固定根放在 z=0 且有地面时轮子压进地面，才是轮式版出现 NaN 的原因（D-026，见 6.1.2）。
PASSIVE_ROLLER = "wheel_.*_passive_.*"
PASSIVE_DAMPING = 0.1

# mimic 约束的"刚度"：URDF 导入器把关节驱动的 naturalFrequency / dampingRatio（默认 25 / 0.005）写进
# physxMimicJoint:*，约束很软，夹爪在重力下跟不住主动关节（6.1.2 实测）。转换后改成下面的值。
MIMIC_NATURAL_FREQUENCY = 1000.0
MIMIC_DAMPING_RATIO = 1.0

# 转换器的固定选项（含义见 6.1.2；convert_mimic_joints_to_normal_joints 的字段名与效果相反）
CONVERTER_OPTIONS = {
    "merge_fixed_joints": True,
    "convert_mimic_joints_to_normal_joints": True,
    "collider_type": "convex_hull",
    "self_collision": False,
    "drive_type": "force",
    "target_type": "position",
}


def variant_dir_name(variant: str, floating_base: bool) -> str:
    return f"galbot_{variant}" + ("_floating" if floating_base else "")


def gains(variant: str) -> tuple[dict, dict]:
    """按变体给出驱动增益字典（轮式版在最后加被动滚子的键，覆盖前面的通配值）。"""
    stiffness, damping = dict(STIFFNESS), dict(DAMPING)
    if variant == "wheeled":
        stiffness[PASSIVE_ROLLER] = 0.0
        damping[PASSIVE_ROLLER] = PASSIVE_DAMPING
    return stiffness, damping


def conversion_params(variant: str, floating_base: bool) -> dict:
    """一个变体的全部生成参数：转换器选项 + 转换后对 USD 的修改。写进清单，也用于校验。"""
    from .physics import SELF_COLLISION_FILTERED_PAIRS

    stiffness, damping = gains(variant)
    return {
        "variant": variant,
        "urdf": URDF_FILES[variant],
        "fix_base": not floating_base,
        "converter": dict(CONVERTER_OPTIONS),
        "stiffness": stiffness,
        "damping": damping,
        "post_processing": {
            "mimic_natural_frequency": MIMIC_NATURAL_FREQUENCY,  # 6.1.2
            "mimic_damping_ratio": MIMIC_DAMPING_RATIO,
            "self_collision_filtered_pairs": [list(p) for p in SELF_COLLISION_FILTERED_PAIRS],  # 6.1.4
        },
    }
