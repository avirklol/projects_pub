import os
import math
import time
import tiktoken
import sys
import click
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()

client = OpenAI()

# --------------------------
# ROOM CONSTRUCTOR AGENT
# --------------------------

# The template for the Room Constructor agent:
rc_template = [
    {
        "role": "system",
        "content": """
        You are the ROOM CONSTRUCTOR agent. You will do one of many things:
        1. You will always output JSON according to provided json_schema.
        2. If prompted 'ROOM' you will output a description of a room inside of {setting}.
        3. If prompted 'ROOM + ENEMY' you will output the following:
            - a description of a room inside of {setting} with the following enemy inside: {enemy}
            - the enemy must be included in the room description
        REQUIREMENTS:
        - The room must have a name and description.
        - The room must have an enemy if prompted.
        - The response cannot resemble a previous response (room names and descriptions must be unique).
        - Enemies may be repeated.
        """
    },
    {
        "role": "user",
        "content": "{prompt}"
    }
]

# The configuration for the Room Constructor agent, updated on each call to room_constructor():
rc_config=[
    {
        "role": "system",
        "content": None
    },
    {
        "role": "user",
        "content": None
    }
]

def room_constructor(prompt:str, setting:str, enemy:str=None):

    # DOCSTRING
    """
    An agent that will construct a room based on a setting and include an enemy if prompted.

    Args:
        prompt (str): Either 'ROOM' or 'ROOM + ENEMY'.
        setting (str): The setting of the room; what kind of location it is.Passed from the settings dictionary in modeuls.ai.config.
        enemy (str, optional): The enemy that should be present in the room. Defaults to None.
    """

    global rc_config

    # Update the configuration with the formatted instructions and prompt while keeping the prevuous room data.
    rc_config[0]['content'] = rc_template[0]['content'].format(setting=setting, enemy=enemy)
    rc_config[-1]['content'] = rc_template[-1]['content'].format(prompt=prompt)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=rc_config,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "room",
                "description": "A room in a text adventure game.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "description": "The name of the room in respect to the setting.",
                            "type": "string"
                        },
                        "description": {
                            "description": "A description of the room at around 140 characters, including an enemy if 'ENEMY' is in prompt.",
                            "type": "string"
                        },
                        "enemy": {
                            "description": "The enemy passed in the instructions if ENEMY is mentioned in the prompt. None if ENEMY is not mentioned or is None.",
                            "type": ["string", "null"]
                        },
                        "additionalProperties": False
                    }
                }
            }
        }
    )

    rc_config.insert(1, {"role": "system", "content": "PREVIOUS ROOM: " + f"{response.choices[0].message.content}"})

    return response.choices[0].message.content

# --------------------------
# END ROOM CONSTRUCTOR AGENT
# --------------------------

# --------------------------
# DM AGENT
# --------------------------

# The template for the DM agent:
dm_template = [
    {
        "role": "system",
        "content": """
        You are the DUNGEON MASTER agent crafting a story with {setting}. You will do one of many things:
        1. You will always output JSON according to provided json_schema.
        2. If prompted 'LOCKED ROOM' you will do the following:
            - output a ~120 CHARACTER description of a locked door situated in the {direction} that will thematically fit the following: {description}
            - integrate the description of the locked door into the room description and output it as updated_description
            - create description of the door unlocking and output it as unlock_description
            - integrate the description of the unlocked door into the room description and output it as unlocked_description
            - create the description of the area beyond the door, this would be the final area (a successful end to the adventure), and output it as win_description
        3. If prompted 'HIDDEN ITEM' you will do the following:
            - output the ~120 CHARACTER description of an {item}
            - additionally output a SUBTLE hint of a hidden item that would encourage the player to search the area WITHOUT SUGGESTING THAT THEY SEARCH IT AND AVOIDING ADVERBS that thematically fits the following description: {description}
            - integrate the hint descriptoin into the room description and output it as updated_description
            - output the item's description as item_description
            - output the item's weight in lbs as item_weight
            - output the item's material as item_material
            - output the item's pickup description as pickup_description
            - output the room description after the item is picked up as empty_keyroom_description
        4. If prompted 'INVENTORY' you will output the player's inventory in a SHORT, descriptive manner. Here is the current inventory: {inventory}
        REQUIREMENTS:
        - The JSON must include an updated_description if 'LOCKED ROOM' or 'HIDDEN ITEM' are prompted else None.
        - The JSON must have an item_description if 'HIDDEN ITEM' is prompted else None.
        - The JSON must have an inventory_description if 'INVENTORY' is prompted else None.
        - The response in updated_description, item_discovery_description and item_description cannot resemble previous responses.
        - The response in inventory_description must resemble previous responses.
        """
    },
    {
        "role": "user",
        "content": "{prompt}"
    }
]

dm_config = [
    {
        "role": "system",
        "content": None
    },
    {
        "role": "user",
        "content": None
    }
]

def dm(prompt:str, setting:str, description:str=None, direction:str=None, item:str=None, inventory:list=None):

    # DOCSTRING
    """
    An agent that will update a room description based on a prompt.

    Args:
        prompt (str): Either 'LOCKED ROOM', 'HIDDEN ITEM', or 'INVENTORY'.
        setting (str): The setting of the room; what kind of location it is. Passed from the settings dictionary in modeuls.ai.config.
        direction (str): The direction of the locked door in the room.
        description (str): The description of the room.
        item (str, optional): The item that is hidden in the room. Defaults to None.
        inventory (str, optional): The player's inventory. Defaults to None.
    """

    global dm_config

    dm_config[0]['content'] = dm_template[0]['content'].format(setting=setting, direction=direction, description=description, item=item, inventory=inventory)
    dm_config[-1]['content'] = dm_template[-1]['content'].format(prompt=prompt)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=dm_config,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "dm_output",
                "description": "The output of the dungeon master.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "updated_description": {
                            "description": "The updated description containing the original description and the appended description of the room if prompted 'LOCKED ROOM' or 'HIDDEN ITEM'. None if not prompted.",
                            "type": ["string", "null"]
                        },
                        "unlock_description": {
                            "description": "The description of the door unlocking if prompted 'LOCKED ROOM'. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "unlocked_description": {
                            "description": "The description of the room after the door is unlocked if prompted 'LOCKED ROOM'; should be the same as the updated_description except you detail that the door is open. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "win_description": {
                            "description": "The description of the area beyond the door if prompted 'LOCKED ROOM'. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "pickup_description": {
                            "description": "The description of the item discovery if prompted 'HIDDEN ITEM', this will be shown when the player discovers the item, should align with the updated_description. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "empty_keyroom_description": {
                            "description": "The description of the room after the player has picked up the hidden item if prompted 'HIDDEN ITEM'. None if not prompted or is None.",
                        },
                        "item_description": {
                            "description": "The description of the item (just the item itself) if prompted 'HIDDEN ITEM'. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "item_weight": {
                            "description": "The weight of the item in lbs if prompted 'HIDDEN ITEM'. None if not prompted or is None.",
                            "type": ["number", "null"]
                        },
                        "item_material": {
                            "description": "The material of the item if prompted 'HIDDEN ITEM'. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "inventory_description": {
                            "description": "The player's inventory presented in a curt descriptive manner if prompted 'INVENTORY'. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "additionalProperties": False
                    }
                }
            }
        }
    )

    dm_config.insert(1, {"role": "system", "content": f"PREVIOUS {prompt}: " + f"{response.choices[0].message.content}"})

    return response.choices[0].message.content

# --------------------------
# END DM AGENT
# --------------------------

# --------------------------
# INPUT AGENT
# --------------------------

i_template = [
    {
        "role": "system",
        "content": """
        You are the INPUT agent. You will do one of many things:
        1. You will always output JSON according to provided json_schema.
        2. You will ingest a {prompt} and you will output input information in an array
        REQUIREMENTS:
        - The response must be a string.
        - The response must be unique.
        - The json_schema must have the following properties: response.
        """
    },
    {
        "role": "user",
        "content": "{prompt}"
    }
]

i_config = [
    {
        "role": "system",
        "content": None
    },
    {
        "role": "user",
        "content": None
    }
]
