from app.agent.decision import decide_workout
from app.models.state import UserState, UserHistory

def test_decision():
    state = UserState(
        goal="fat_loss",
        energy="medium",
        free_slots=[("11:15","12:45"), ("15:15","20:45")],
        preference="evening",
        history=UserHistory(last_workout={"intensity":"medium"}, streak=2)
    )

    decision = decide_workout(state)
    print(decision)

if __name__ == "__main__":
    test_decision()