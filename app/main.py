# app/main.py
from app.agent.parser import parse_input
from app.agent.decision import decide_workout

def run_agent(text, calendar, history):
    state = parse_input(text, calendar, history)
    decision = decide_workout(state)

    # 可选自然语言输出
    if decision["decision"] == "workout":
        decision["nl"] = f"建议你在 {decision['time']} 进行 {decision['duration']} 分钟 {decision['intensity']} 强度 {decision['type']} 训练"
    else:
        decision["nl"] = f"今天休息：{decision['reason']}"

    return decision

if __name__ == "__main__":
    text = "我今天有点累，晚上有空，想减脂"
    calendar = [{"start":"09:00","end":"11:00"}, {"start":"13:00","end":"15:00"}]
    history = {"last_workout":{"intensity":"medium"}, "streak":2, "preference":"evening"}

    result = run_agent(text, calendar, history)
    print(result)