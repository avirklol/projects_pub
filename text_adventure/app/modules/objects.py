class Room:
    def __init__(self, id:str, location:tuple, name:str, description:str, enemy:str, items:list, exits:dict):
        self.id = id
        self.location = location
        self.name = name
        self.description = description
        self.enemy = enemy
        self.items = items
        self.exits = exits

class Player:
    def __init__(self, current_room):
        self.current_room = current_room
        self.inventory = []
