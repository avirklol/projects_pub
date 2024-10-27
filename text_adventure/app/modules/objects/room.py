import random
import click

class Room:
    def __init__(self, id:str, location:tuple, name:str, description:str, exits:dict, enemy:str=None, items:list=None, locked:bool=False):
        self.id = id
        self.location = location
        self.name = name
        self.description = description
        self.enemy = enemy
        self.items = items
        self.locked = locked
        self.new_description = None
        self.unlock_description = None
        self.exits = exits
        self.end_game = False
