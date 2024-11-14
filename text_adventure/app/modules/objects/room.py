import random
import click

class Room:

    """
    Room class for text adventure game.

    ATTRIBUTES:
        id (str): unique identifier for room
        location (tuple): coordinates for room location
        name (str): name of room
        description (str): description of room
        new_description (str): updated description of room, used if something can change in the room
        npc (object): NPC class in room
        items (list): list of Item classes in room
        exits (dict): dictionary of exits from room, referencing other Room class ids
        locked (bool): whether room is locked or not
        locked_door (bool): whether room has a locked door or not
        locked_door_data (dict): dictionary of data for locked door
        end_game (bool): whether the game ends in this room
    """

    def __init__(self, id:str, location:tuple, name:str, description:str, exits:dict, new_description:str=None, npc:object=None, items:list=None,
                 locked:bool=False, locked_door:bool=False, locked_door_data:dict=None, end_game:bool=False):
        self.id = id
        self.location = location
        self.name = name
        self.description = description
        self.new_description = new_description
        self.npc = npc
        self.items = items
        self.exits = exits
        self.locked = locked
        self.locked_door = locked_door
        self.locked_door_data = {
            "key_id": None,
            "exit": None,
            "description": None,
            "unlock_description": None,
        } if locked_door_data is None else locked_door_data
        self.end_game = end_game
