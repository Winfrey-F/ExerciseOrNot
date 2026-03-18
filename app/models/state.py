"""用户状态与历史模型，供决策与调度使用。"""
from __future__ import annotations

from typing import Any, Optional


class UserHistory:
    """用户运动历史：最近一次运动、连续天数等。"""

    def __init__(
        self,
        last_workout: Optional[dict[str, Any]] = None,
        streak: int = 0,
        preference: Optional[str] = None,
    ):
        self.last_workout = last_workout or {}
        self.streak = streak
        self.preference = preference


class UserState:
    """单次决策的输入：目标、能量、空闲时段、偏好与历史。"""

    def __init__(
        self,
        goal: str,
        energy: str,
        free_slots: list[tuple[str, str]],
        preference: Optional[str],
        history: UserHistory,
    ):
        self.goal = goal
        self.energy = energy
        self.free_slots = free_slots
        self.preference = preference
        self.history = history