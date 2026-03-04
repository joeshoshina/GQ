"""
TimeRule: Encapsulates the local time rule.
Supports conversions toLocal(world) and toWorld(local) so the rule can evolve
without changing event storage.
"""

from world_time import WorldTime


class TimeRule:
    def __init__(self, offset_minutes):
        self.offset_minutes = offset_minutes
    
    def to_local(self, world_time):
        return WorldTime(world_time.get_total_minutes() + self.offset_minutes)
    
    def to_world(self, local_time):
        return WorldTime(local_time.get_total_minutes() - self.offset_minutes)
    
    def get_offset_minutes(self):
        return self.offset_minutes
    
    def __str__(self):
        hours = self.offset_minutes // 60
        mins = abs(self.offset_minutes % 60)
        return f"UTC{hours:+d}:{mins:02d}"
