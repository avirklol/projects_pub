import click

class NPC:
    def __init__(self, name:str, description:str=None, location:str=None, inventory:list=None, is_hostile:bool=False, is_merchant:bool=False, is_quest_giver:bool=False, is_hidden:bool=False,
                 dialogue:dict=None, quests:dict=None, items:dict=None, stats:dict=None, modifiers:dict=None, unique_id:str=None, history:list=None):
        self.name = name
        self.description = description
        self.location = location
        self.inventory = inventory if inventory is not None else []
        self.is_hostile = is_hostile
        self.is_merchant = is_merchant
        self.is_quest_giver = is_quest_giver
        self.is_hidden = is_hidden
        self.dialogue = dialogue if dialogue is not None else {}
        self.quests = quests if quests is not None else {}
        self.items = items if items is not None else {}
        self.stats = stats if stats is not None else {}
        self.modifiers = modifiers if modifiers is not None else {}
        self.unique_id = unique_id
        self.history = history if history is not None else []

    def __str__(self):
        return f"{self.name}: {self.description}"
