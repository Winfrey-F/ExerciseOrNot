from app.scheduler.time_utils import generate_free_slots

def test_basic_case():
    calendar = [
        {"start": "09:00", "end": "11:00"},
        {"start": "13:00", "end": "15:00"}
    ]

    slots = generate_free_slots(calendar)

    print(slots)

if __name__ == "__main__":
    test_basic_case()