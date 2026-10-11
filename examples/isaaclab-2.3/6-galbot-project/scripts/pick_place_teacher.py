# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
"""pick-place 的脚本化示教控制器（6.4.6），供 record_pick_place.py 与 sweep_physics.py（6.3.1）共用。

导入它之前要先启动 Kit（AppLauncher），因为它用到 isaaclab.utils.math。
"""

import math

import torch

import isaaclab.utils.math as math_utils

from galbot_academy.scenes.lift import CUBE_REST_Z
from galbot_academy.tasks.manager_based.pick_place.pick_place_env_cfg import RELEASE_MAX_Q


class PickPlaceTeacher:
    """分段控制器：接近 → 下探 → 合拢 → 举起 → 搬运 → 放下 → 张开 → 后撤。

    全部在机器人根坐标系里算：读观测里的 TCP 位姿、方块与放置点位置，输出"朝目标走一小步"的 IK 相对动作。
    抓取姿态固定：TCP 的 x 轴（接近方向）从竖直向下朝前（根 +x）倾斜 approach_deg，闭合轴（TCP y）沿根的 −y，
    让两指夹在方块的两个侧面上（6.4.6"抓取姿态"）。
    """

    PHASES = ["hover", "pre", "approach", "close", "lift", "carry", "lower", "open", "retreat", "done"]
    MAX_DP = 0.01  # m / 步（30 Hz 下 30 cm/s）
    MAX_DR = 0.05  # rad / 步
    PRE_DIST = 0.10  # 预抓点沿接近方向后退 10 cm
    LIFT_Z = 0.10  # 举起、搬运的高度：方块中心高出桌面静止高度 10 cm
    PHASE_LIMIT = {"hover": 240, "pre": 120, "approach": 120, "close": 90, "lift": 120, "carry": 400, "lower": 180, "open": 120, "retreat": 90}

    def __init__(self, device: str, approach_deg: float, gripper_close_q: float):
        th = math.radians(approach_deg)
        a = torch.tensor([math.sin(th), 0.0, -math.cos(th)], device=device)  # 接近方向
        c = torch.tensor([0.0, -1.0, 0.0], device=device)  # 闭合方向
        self.R_grasp = torch.stack([a, c, torch.linalg.cross(a, c)], dim=1)
        self.approach = a
        self.device = device
        self.close_q = gripper_close_q
        self.reset()

    def reset(self):
        self.phase, self.count, self.goal = "hover", 0, None
        self.hold, self.best = 0, (1e9, 0)

    def _next(self):
        self.phase = self.PHASES[self.PHASES.index(self.phase) + 1]
        self.count, self.goal, self.hold, self.best = 0, None, 0, (1e9, 0)

    def act(self, obs: dict) -> torch.Tensor:
        o = obs["policy"]
        p, q = o["eef_pos"][0], o["eef_quat"][0]
        R = math_utils.matrix_from_quat(q[None])[0]
        obj, tgt, grip = o["object_position"][0], o["target_position"][0], o["gripper_pos"][0, 0].item()
        up = torch.tensor([0.0, 0.0, 1.0], device=self.device)
        close = self.phase in ("close", "lift", "carry", "lower")
        # 各段的目标点（TCP）；到达判据：位置误差 < tol，或本段步数用完（超时由外层判失败）
        if self.phase == "hover":
            # 先到方块斜上方：沿接近方向后退 12 cm、再抬高 12 cm，避免从默认姿态直线过去时扫到方块
            goal, tol = obj - self.approach * 0.12 + up * 0.12, 0.02
        elif self.phase == "pre":
            goal, tol = obj - self.approach * self.PRE_DIST, 0.01
        elif self.phase == "approach":
            if self.goal is None:
                self.goal = obj.clone()  # 冻结：手碰到方块时不去追它
            goal, tol = self.goal, 0.006
        elif self.phase in ("close", "open"):
            if self.goal is None:
                self.goal = p.clone()  # 原地不动
            goal, tol = self.goal, None
        elif self.phase == "lift":
            if self.goal is None:
                self.goal = p + up * self.LIFT_Z
            goal, tol = self.goal, 0.01
        elif self.phase == "carry":
            # 方块随手移动：让方块中心（而不是 TCP）对准放置点上方。TCP 与方块的相对位置在合拢后固定
            goal = p + (torch.stack([tgt[0], tgt[1], obj.new_tensor(CUBE_REST_Z + self.LIFT_Z)]) - obj)
            tol = 0.008
        elif self.phase == "lower":
            goal = p + (torch.stack([tgt[0], tgt[1], obj.new_tensor(CUBE_REST_Z + 0.003)]) - obj)
            tol = 0.004
        elif self.phase == "retreat":
            if self.goal is None:
                self.goal = p - self.approach * self.PRE_DIST + up * 0.05
            goal, tol = self.goal, 0.01
        else:  # done：原地不动
            goal, tol = p, None

        # 段切换
        err = torch.linalg.norm(goal - p).item()
        self.last_err, self.last_obj = err, obj.clone()
        self.count += 1
        if self.phase == "close":
            # 夹爪测量位置停止增长（连续 5 步变化 < 0.002 rad）且已过 1.0 rad，认为夹住了
            self.hold = self.hold + 1 if (grip >= 1.0 and abs(grip - getattr(self, "_last_grip", grip)) < 0.002) else 0
            if self.hold >= 5:
                self._next()
        elif self.phase == "open":
            if grip <= RELEASE_MAX_Q - 0.05:
                self._next()
        elif tol is not None:
            # 到达：误差 < tol；或者误差 30 步没有再变小、且已 < 2 cm（IK 的残差，sweep 里常见 0.5–2 cm）
            if err < self.best[0] - 1e-4:
                self.best = (err, self.count)
            if err < tol or (err < 0.02 and self.count - self.best[1] > 30):
                self._next()
        self._last_grip = grip

        dp = (goal - p).clamp(-self.MAX_DP, self.MAX_DP)
        dr = math_utils.axis_angle_from_quat(math_utils.quat_from_matrix((self.R_grasp @ R.T)[None]))[0]
        n = torch.linalg.norm(dr)
        if n > self.MAX_DR:
            dr = dr / n * self.MAX_DR
        g = torch.tensor([-1.0 if close else 1.0], device=self.device)
        return torch.cat([dp, dr, g])[None]

    def timed_out(self) -> bool:
        return self.phase in self.PHASE_LIMIT and self.count > self.PHASE_LIMIT[self.phase]
