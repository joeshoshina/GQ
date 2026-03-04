"""
WorldTime: Stores the canonical timestamp for events using totalMinutes.
Supports days/hours/minutes via conversion. 
"""

class WorldTime:
    def __init__(self, *args):
        if len(args) == 1:
            self.total_minutes = args[0]
        elif len(args) == 3:
            days, hours, minutes = args
            self.total_minutes = (days * 24 * 60) + (hours * 60) + minutes
        else:
            raise ValueError("WorldTime requires either 1 or 3 arguments")
    
    def get_total_minutes(self):
        return self.total_minutes
    
    def get_days(self):
        return self.total_minutes // (24 * 60)
    
    def get_hours(self):
        return (self.total_minutes % (24 * 60)) // 60
    
    def get_minutes(self):
        return self.total_minutes % 60
    
    def add(self, minutes):
        return WorldTime(self.total_minutes + minutes)
    
    def subtract(self, minutes):
        return WorldTime(self.total_minutes - minutes)
    
    def difference(self, other):
        return self.total_minutes - other.total_minutes
    
    def __lt__(self, other):
        return self.total_minutes < other.total_minutes
    
    def __le__(self, other):
        return self.total_minutes <= other.total_minutes
    
    def __gt__(self, other):
        return self.total_minutes > other.total_minutes
    
    def __ge__(self, other):
        return self.total_minutes >= other.total_minutes
    
    def __eq__(self, other):
        if not isinstance(other, WorldTime):
            return False
        return self.total_minutes == other.total_minutes
    
    def __hash__(self):
        return hash(self.total_minutes)
    
    def __str__(self):
        return f"Day {self.get_days()}, {self.get_hours():02d}:{self.get_minutes():02d}"
    
    def __repr__(self):
        return f"WorldTime({self.total_minutes})"
