# app/agent/decision.py
"""运动决策逻辑：根据用户状态选择时段、时长、强度与类型。"""
from __future__ import annotations

from typing import Any, Optional

from app.models.state import UserState
from app.scheduler.time_utils import to_minutes, to_time_str

# --- 时段偏好：名称 -> (开始分钟, 结束分钟) ---
PREFERENCE_RANGES: dict[str, tuple[int, int]] = {
    "morning": (7 * 60, 12 * 60),    # 07:00 - 12:00
    "afternoon": (12 * 60, 17 * 60),  # 12:00 - 17:00
    "evening": (17 * 60, 21 * 60),    # 17:00 - 21:00
}

MIN_WORKOUT_DURATION = 30
MAX_CONSECUTIVE_DAYS = 3
DURATION_BUCKETS = (30, 45, 60)  # 可选时长（分钟）

GOAL_TO_WORKOUT_TYPE: dict[str, str] = {
    "fat_loss": "cardio",
    "muscle_gain": "strength",
    "relax": "stretch",
}


def select_slot(
    free_slots: list[tuple[str, str]],
    preference: Optional[str] = None,
    min_duration: int = MIN_WORKOUT_DURATION,
) -> Optional[tuple[int, int]]:
    """
    在空闲时段中选出最合适的一个。
    有偏好时优先选与偏好时段重叠最大的；无偏好时选最早时段。
    只保留长度 >= min_duration 的时段。
    """
    candidates: list[tuple[int, int]] = []
    for start_str, end_str in free_slots:
        start = to_minutes(start_str)
        end = to_minutes(end_str)
        if end - start >= min_duration:
            candidates.append((start, end))

    if not candidates:
        return None

    if preference and preference in PREFERENCE_RANGES:
        pref_start, pref_end = PREFERENCE_RANGES[preference]
        scored = [
            (max(0, min(e, pref_end) - max(s, pref_start)), (s, e))
            for s, e in candidates
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    return candidates[0]


def select_duration(slot: tuple[int, int]) -> int:
    """根据时段长度在 30/45/60 分钟档位中选取建议时长。"""
    start, end = slot
    slot_minutes = end - start
    d30, d45, d60 = DURATION_BUCKETS
    if slot_minutes < d45:
        return d30
    if slot_minutes < d60:
        return d45
    return min(d60, slot_minutes)


def select_intensity(
    energy: str,
    last_intensity: Optional[str] = None,
    streak: int = 0,
) -> str:
    """根据当前能量、上次强度、连续天数决定本次强度；避免连续高强度与过长连续。"""
    intensity = energy if energy in ("low", "medium", "high") else "medium"
    if last_intensity == "high" and intensity == "high":
        intensity = "medium"
    if streak >= MAX_CONSECUTIVE_DAYS:
        intensity = "low"
    return intensity


def goal_to_type(goal: str) -> str:
    """将用户目标映射为运动类型。"""
    return GOAL_TO_WORKOUT_TYPE.get(goal, "cardio")


def _rest(reason: str) -> dict[str, Any]:
    """构造休息决策结果。"""
    return {"decision": "rest", "reason": reason}


def _workout(
    slot: tuple[int, int],
    duration: int,
    intensity: str,
    type_: str,
) -> dict[str, Any]:
    """构造运动决策结果。"""
    start, _ = slot
    actual_end = start + duration
    return {
        "decision": "workout",
        "time": f"{to_time_str(start)}-{to_time_str(actual_end)}",
        "type": type_,
        "intensity": intensity,
        "duration": duration,
        "reason": f"selected slot {slot} with duration {duration} min, intensity {intensity}, type {type_}",
    }


def decide_workout(state: UserState) -> dict[str, Any]:
    """
    根据用户状态决定今日是否运动及具体安排。
    返回统一结构：decision（rest/workout）+ reason；若 workout 则含 time/type/intensity/duration。
    """
    if not state.free_slots:
        return _rest("no available time slots")

    last_intensity: Optional[str] = state.history.last_workout.get("intensity")
    streak = state.history.streak

    if state.energy == "low" and last_intensity:
        return _rest("low energy after previous workout")
    if streak >= MAX_CONSECUTIVE_DAYS:
        return _rest("too many consecutive workout days")

    slot = select_slot(
        state.free_slots,
        state.preference,
        min_duration=MIN_WORKOUT_DURATION,
    )
    if not slot:
        return _rest("no slot long enough for minimum workout")

    duration = select_duration(slot)
    intensity = select_intensity(state.energy, last_intensity, streak)
    type_ = goal_to_type(state.goal)

    return _workout(slot, duration, intensity, type_)