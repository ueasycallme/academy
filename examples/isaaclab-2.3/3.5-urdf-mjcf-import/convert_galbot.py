# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用 Isaac Lab 的 UrdfConverter 把 Galbot One Golf 的 URDF 转成 USD，演示 convert_urdf.py 命令行没有暴露的选项。

与 scripts/tools/convert_urdf.py 相比，这里额外设置了：
- 被动滚子关节不加驱动（target_type="none"），其余关节用位置驱动；
- 保留 URDF 中的 mimic 关系（注意字段名与效果相反，见 3.5 页"常见坑"）。

用法::

    python convert_galbot.py --headless                        # 输出到 ./galbot_usd/galbot.usd
    python convert_galbot.py --headless --output /tmp/galbot/galbot.usd

URDF 取自本仓库 third_party/ 下的 Galbot 描述仓库：
https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description （Apache-2.0，commit 2d496b0）
"""

import argparse
import os
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_URDF = REPO_ROOT / "third_party/galbot_one_golf_description/urdf/galbot_one_golf.urdf"

parser = argparse.ArgumentParser(description="把 Galbot One Golf 的 URDF 转成 USD")
parser.add_argument("--urdf", default=str(DEFAULT_URDF), help="输入的 URDF 文件")
parser.add_argument("--output", default="galbot_usd/galbot.usd", help="输出的 USD 文件")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg


def main() -> None:
    output = os.path.abspath(args.output)
    cfg = UrdfConverterCfg(
        asset_path=os.path.abspath(args.urdf),
        usd_dir=os.path.dirname(output),
        usd_file_name=os.path.basename(output),
        fix_base=False,  # 轮式底盘，浮动基座
        merge_fixed_joints=True,  # 合并固定关节两侧的连杆
        convert_mimic_joints_to_normal_joints=True,  # v2.3.2 中为 True 时才保留 mimic 关系（见页面说明）
        force_usd_conversion=True,
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            # 按关节名正则分组。字典按顺序应用，后面的键会覆盖前面匹配到的关节，所以通配的 ".*" 要放在最前面。
            # 被动滚子设为 none：转换器会把它们的 stiffness、damping 置 0
            target_type={".*": "position", "wheel_.*_passive_.*": "none"},
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=100.0, damping=1.0),
        ),
    )
    converter = UrdfConverter(cfg)
    print(f"Generated USD file: {converter.usd_path}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
