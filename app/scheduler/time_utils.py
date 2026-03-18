def to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def to_time_str(m: int) -> str:
    return f"{m//60:02d}:{m%60:02d}"


def generate_free_slots(calendar):
    DAY_START = 7 * 60
    DAY_END = 21 * 60
    BUFFER = 15

    events = sorted([
        (to_minutes(e["start"]), to_minutes(e["end"]))
        for e in calendar
    ])

    free_slots = []
    prev_end = DAY_START

    for start, end in events:
        if start > prev_end:

            free_start = prev_end
            free_end = start

            free_start += BUFFER
            free_end -= BUFFER

            if free_end - free_start >= 30:
                free_slots.append((free_start, free_end))

        prev_end = max(prev_end, end)

    if prev_end < DAY_END:
            free_start = prev_end + BUFFER
            free_end = DAY_END - BUFFER

            if free_end - free_start >= 30:
                free_slots.append((free_start, free_end))
    
    return [(to_time_str(s), to_time_str(e)) for s, e in free_slots]