# app/agent/parser.py
from app.models.state import UserState, UserHistory
from app.scheduler.time_utils import generate_free_slots

def parse_input(text: str, calendar: list, history_dict: dict):
    # --- 解析文本 (可以先简单规则匹配) ---
    goal = "fat_loss" if "减脂" in text else "relax"  # 简单示例
    energy = "low" if "累" in text else "medium"
    preference = None
    for p in ["morning","afternoon","evening"]:
        if p in text:
            preference = p

    # --- 生成 free slots ---
    free_slots = generate_free_slots(calendar)

    # --- 构建历史对象 ---
    history = UserHistory(
        last_workout=history_dict.get("last_workout", {}),
        streak=history_dict.get("streak", 0),
        preference=history_dict.get("preference")
    )

    # --- 构建状态对象 ---
    state = UserState(goal, energy, free_slots, preference, history)
    return state