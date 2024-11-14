import random
import click
import secrets

class Item:
    def __init__(self, id:str, name:str, description:str=None, pickup_descripton:str=None, weight:float=None, material:str=None, value:float=None, rarity:str=None, condition:str=None,
                 is_collectible:bool=True, is_hidden:bool=False, is_key:bool=False, is_usable:bool=False, use_effect:dict=None, is_equippable:bool=False, is_consumable:bool=False,
                 durability:int=None, modifiers:dict=None, location:str=None, owner:str=None, unique_id:str=None, history:list=None):
        self.id = id + "_" + secrets.token_hex(4)
        self.name = name
        self.description = description
        self.pickup_description = pickup_descripton
        self.weight = weight
        self.material = material
        self.value = value
        self.rarity = rarity
        self.condition = condition
        self.is_collectible = is_collectible
        self.is_key = is_key
        self.is_hidden = is_hidden
        self.is_usable = is_usable
        self.use_effect = use_effect if use_effect is not None else {}
        self.is_equippable = is_equippable
        self.is_consumable = is_consumable
        self.durability = durability if durability is not None else 100
        self.modifiers = modifiers if modifiers is not None else {}
        self.location = location
        self.owner = owner
        self.unique_id = unique_id
        self.history = history if history is not None else []

    def __str__(self):
        return f"{self.name}: {self.description}"
