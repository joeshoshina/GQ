"""
Realm: Represents a physical location with name, description, and map identity.
Converts between world time and local time using its TimeRule.
"""


class Realm:
    def __init__(self, name, description, map_identity, time_rule):
        self.name = name
        self.description = description
        self.map_identity = map_identity
        self.time_rule = time_rule
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_description(self):
        return self.description
    
    def set_description(self, description):
        self.description = description
    
    def get_map_identity(self):
        return self.map_identity
    
    def get_time_rule(self):
        return self.time_rule
    
    def set_time_rule(self, time_rule):
        self.time_rule = time_rule
    
    def to_local_time(self, world_time):
        return self.time_rule.to_local(world_time)
    
    def to_world_time(self, local_time):
        return self.time_rule.to_world(local_time)
    
    def __str__(self):
        return f"{self.name} ({self.time_rule})"
