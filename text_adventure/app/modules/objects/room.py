import random
import click

class Room:
    def __init__(self, id:str, location:tuple, name:str, description:str, exits:dict, enemy:str=None, items:list=[], locked:bool=False):
        self.id = id
        self.location = location
        self.name = name
        self.description = description
        self.enemy = enemy
        self.items = items
        self.locked = locked
        self.exits = exits
