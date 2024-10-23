import random
import click

class Item:
    def __init__(self, name:str, description:str=None, stats:dict=None, key:bool=False):
        self.name = name
        self.description = description
        self.stats = stats
        self.key = key

    def __str__(self):
        return f"{self.name}: {self.description}"
