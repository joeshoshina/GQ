class AdventureContext:
    """
    Holds strategy objects used by a mini-adventure.

    This is the Context in the Strategy Pattern.
    It delegates behavior to the configured strategies.
    """

    def __init__(self, movement, win_condition, time_strategy=None):
        self.movement = movement
        self.win_condition = win_condition
        self.time_strategy = time_strategy

    def move_player(self, player, direction):
        return self.movement.move(self, player, direction)

    def check_win(self):
        return self.win_condition.check(self)

    def advance_time(self):
        if self.time_strategy:
            self.time_strategy.advance_time(self)