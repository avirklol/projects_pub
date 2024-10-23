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
        3. If prompted 'ROOM + ENEMY' you will output a description of a room inside of {setting} with the following enemy inside: {enemy}
        REQUIREMENTS:
        - The room must have a name and description.
        - The room must have an enemy if prompted.
        - If the room has an enemy, the enemy must be included in the room description.
        - The response cannot resemble a previous response (room names and descriptions must be unique).
        - Enemies may be repeated.
        - The json_schema must have the following properties: name, description, enemy.
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
        2. If prompted 'LOCKED ROOM' you will append a short description of a locked door situated in the {direction} to the following room details: {description}
        3. If prompted 'HIDDEN ITEM' you will output the short description of an {item} and append a subtle hint to the following room details: {description}
        4. If prompted 'INVENTORY' you will output the player's inventory in a short, descriptive manner. Here is the current inventory: {inventory}
        REQUIREMENTS:
        - The JSON must include an updated_description if 'LOCKED ROOM' or 'HIDDEN ITEM' are prompted else None.
        - The JSON must have an item_description if 'HIDDEN ITEM' is prompted else None.
        - The JSON must have an inventory_description if 'INVENTORY' is prompted else None.
        - The response in updated_description CANNOT replace the provided description in step 2.
        - The response in updated_description and item_description cannot resemble previous responses.
        - The response in inventory_description must resemble previous responses.
        - The json_schema must have the following properties: updated_description, item_description, inventory_description.
        """
    },
    {
        "role": "user",
        "content": "{prompt}"
    }
]

# The configuration for the DM agent, updated on each call to dm():
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

def dm(prompt:str, setting:str, description:str, direction:str=None, item:str=None, inventory:list=None):

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
                            "description": "The updated description of the room if prompted 'LOCKED ROOM' or 'HIDDEN ITEM'. None if not prompted.",
                            "type": ["string", "null"]
                        },
                        "item_description": {
                            "description": "The description of the item if prompted 'HIDDEN ITEM'. None if not prompted or is None.",
                            "type": ["string", "null"]
                        },
                        "inventory_description": {
                            "description": "The player's inventory if prompted 'INVENTORY'. None if not prompted or is None.",
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
