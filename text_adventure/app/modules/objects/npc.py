import random
import click
import secrets
from modules.ai import client

class NPC:
    def __init__(self, role:str=None, sex:str=None, race:str=None, alignment:str=None, class_:str=None, traits:list=None, archetype:str=None,
                 name:str=None, description:str=None, dead_description:str=None, current_room:object=None, inventory:list=None, is_alive:bool=True,
                 is_defeated:bool=False, is_hostile:bool=False, is_merchant:bool=False, is_ally:bool=False, is_quest_giver:bool=False, is_hidden:bool=False,
                 dialogue:dict=None, quests:dict=None, items:dict=None, stats:dict=None, modifiers:dict=None, unique_id:str=None, history:list=None):
        self.role = role
        self.sex = sex
        self.race = race
        self.alignment = alignment
        self.class_ = class_
        self.traits = traits
        self.archetype = archetype
        self.name = name
        self.description = description
        self.dead_description = dead_description
        self.current_room = current_room
        self.inventory = inventory if inventory is not None else {}
        self.is_alive = is_alive
        self.is_hostile = is_hostile
        self.is_defeated = is_defeated
        self.is_merchant = is_merchant
        self.is_ally = is_ally
        self.is_quest_giver = is_quest_giver
        self.is_hidden = is_hidden
        self.dialogue_samples = dialogue if dialogue is not None else []
        self.quests = quests if quests is not None else {}
        self.items = items if items is not None else {}
        self.stats = stats if stats is not None else {}
        self.modifiers = modifiers if modifiers is not None else {}
        self.unique_id = unique_id
        self.history = history if history is not None else []

    def __str__(self):
        return f"{self.name}: {self.description}"
