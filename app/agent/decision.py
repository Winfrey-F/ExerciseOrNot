# app/agent/decision.py
from app.models.state import UserState

PREFERENCE_RANGES = {
    "morning": (7 * 60, 12 * 60),
    "afternoon": (12 * 60, 17 * 60),
    "evening": (17 * 60, 21 * 60),
}

GOAL_TO_TYPE = {"fat_loss": "cardio", "muscle_gain": "strength", "relax": "stretch"}


def to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def to_time_str(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _rest(reason: str) -> dict:
    return {"decision": "rest", "reason": reason}


def select_slot(free_slots, preference=None, duration=30):
    """选择最合适的时间段：考虑用户偏好，尽量选刚好够的时长。"""
    candidates = []
    for s, e in free_slots:
        start, end = to_minutes(s), to_minutes(e)
        if end - start >= duration:
            candidates.append((start, end))
    if not candidates:
        return None

    if preference in PREFERENCE_RANGES:
        pref_start, pref_end = PREFERENCE_RANGES[preference]
        scored = [
            (max(0, min(e, pref_end) - max(s, pref_start)), (s, e))
            for s, e in candidates
        ]
        scored.sort(reverse=True)
        return scored[0][1]
    return candidates[0]


def select_duration(slot):
    start, end = slot
    span = end - start
    if span < 45:
        return 30
    if span < 60:
        return 45
    return min(60, span)


def select_intensity(energy, last_intensity=None, streak=0):
    intensity = energy if energy in ("low", "medium", "high") else "medium"
    if last_intensity == "high" and intensity == "high":
        intensity = "medium"
    if streak >= 3:
        intensity = "low"
    return intensity


def goal_to_type(goal):
    return GOAL_TO_TYPE.get(goal, "cardio")


def decide_workout(state: UserState):
    """输入 UserState，输出包含 decision / time / type / intensity / duration / reason 的 dict。"""
    if not state.free_slots:
        return _rest("no available time slots")

    last_intensity = state.history.last_workout.get("intensity")
    streak = state.history.streak

    # 低能量时不直接休息：强度降到 low；仅当上次强度已是 low 时才休息
    if state.energy == "low" and last_intensity == "low":
        return _rest("low energy after previous workout")
    if streak >= 3:
        return _rest("too many consecutive workout days")

    slot = select_slot(state.free_slots, state.preference, duration=30)
    if not slot:
        return _rest("no slot long enough for minimum workout")

    start, end = slot
    duration = select_duration(slot)
    time_range = f"{to_time_str(start)}-{to_time_str(start + duration)}"
    intensity = select_intensity(state.energy, last_intensity, streak)
    type_ = goal_to_type(state.goal)

    return {
        "decision": "workout",
        "time": time_range,
        "type": type_,
        "intensity": intensity,
        "duration": duration,
        "reason": f"selected {time_range}, duration {duration} min, intensity {intensity}, type {type_}",
    }