class UserHistory:
    def __init__(self, last_workout=None, streak=0, preference=None):
        self.last_workout = last_workout or {}
        self.streak = streak
        self.preference = preference

class UserState:
    def __init__(self, goal, energy, free_slots, preference, history: UserHistory):
        self.goal = goal                # fat_loss / muscle_gain / relax
        self.energy = energy            # low / medium / high
        self.free_slots = free_slots    # list of tuples [('11:15','12:45'),...]
        self.preference = preference    # morning / evening / None
        self.history = history