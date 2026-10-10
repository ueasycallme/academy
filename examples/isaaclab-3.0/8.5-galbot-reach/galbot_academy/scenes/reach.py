# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""reach 的场景（6.2.1）。

- GalbotReachSceneCfg：地面、灯光（全局路径，所有环境共用）+ 机器人（每个环境一份）。reach 用它。
- GalbotReachTableSceneCfg：再加一张静态桌面作参照。它会与手臂发生碰撞，reach 不用；lift（6.4.3）从这里扩展。
"""

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_CFG

# 桌面：长方体，放在机器人前方；尺寸与位置见 6.2.1 的工作空间统计
TABLE_SIZE = (0.6, 1.0, 0.04)  # x（前后）、y（左右）、厚度，m
TABLE_TOP_Z = 0.95  # 桌面上表面高度，m
TABLE_CENTER_XY = (0.65, -0.25)  # 桌面中心相对机器人根的位置，m


@configclass
class GalbotReachSceneCfg(InteractiveSceneCfg):
    """reach 的最小场景。num_envs / env_spacing 由使用方给出，6.2.1 建议 env_spacing = 2.5。"""

    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(
        prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2000.0, color=(0.9, 0.9, 0.9))
    )
    robot: ArticulationCfg = GALBOT_ONE_GOLF_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


@configclass
class GalbotReachTableSceneCfg(GalbotReachSceneCfg):
    """加一张静态桌面。桌面有碰撞体（kinematic 刚体），手臂碰到会被挡住。"""

    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table",
        spawn=sim_utils.CuboidCfg(
            size=TABLE_SIZE,
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.55, 0.45, 0.35)),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(*TABLE_CENTER_XY, TABLE_TOP_Z - TABLE_SIZE[2] / 2)),
    )
