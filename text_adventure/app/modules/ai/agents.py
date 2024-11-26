import os
import math
import time
from turtle import update
from matplotlib import rc
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
rc_settings = {
    "SYSTEM": """
    You are the ROOM CONSTRUCTOR agent. You will do one of many things:
        1. You will always output JSON according to provided json_schema.
        2. {config}
    """,
    "ROOM": {
        "instructions":"""
        If prompted 'ROOM' you will output a description of a room inside of {setting}:
            - output a name for the room to room_name
            - output a description of the room to room_description
            - ensure that all rooms are unique and do not resemble previous responses
        """,
        "outputs": {
            "room_name": {
                "description": "The name of the room in respect to the setting.",
                "type": "string"
            },
            "room_description": {
                "description": "A description of the room at around 140 characters.",
                "type": "string"
            }
        }
        },
    "ROOM + NPC": {
        "instructions":"""
        If prompted 'ROOM + NPC' you will output the following:
            - a description of a room inside of {setting} with the following kind of enemy inside: {npc_race}
            - consider the NPC's sex: {npc_sex}
            - consider the NPC's alignment: {npc_alignment}
            - consider the NPC's class: {npc_class}
            - consider the NPC's description: {npc_description}
            - consider the NPC's role: {npc_role} (very important)
            - the NPC must be incorporated into the room description in a manner that fits the setting and their role
            - output the description of the dead enemy to npc_dead_description
            - output the description of the room to room_description
            - output the name of the room to room_name
            - ensure that all rooms are unique and do not resemble previous responses
        """,
        "outputs": {
            "room_name": {
                "description": "The name of the room in respect to the setting.",
                "type": "string"
            },
            "room_description": {
                "description": "A description of the room at around 140 characters, incorporating the description of an NPC present in the room if prompted 'ROOM + NPC'.",
                "type": "string"
            },
            "npc_dead_description": {
                "description": "A description of the dead NPC if prompted 'ROOM + NPC'.",
                "type": "string"
            },
        }
    }
}

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

def room_constructor(prompt:str, setting:str, npc:object=None):

    """
    An agent that will construct a room based on a setting and include an enemy if prompted.

    ARGUMENTS:
        prompt (str): Either 'ROOM' or 'ROOM + ENEMY'.
        setting (str): The setting of the room; what kind of location it is.Passed from the settings dictionary in modeuls.ai.config.
        npc (str, optional): The enemy that should be present in the room. Defaults to None.
    """

    global rc_config

    prompt_params = {
        "ROOM": {
            "setting": setting
        },
        "ROOM + NPC": {
            "setting": setting,
            "npc_race": npc.race if npc else None,
            "npc_sex": npc.sex if npc else None,
            "npc_alignment": npc.alignment if npc else None,
            "npc_class": npc.class_ if npc else None,
            "npc_description": npc.description if npc else None,
            "npc_role": npc.role if npc else None,
        },
    }

    # Update the configuration with the formatted instructions and prompt while keeping the prevuous room data.
    if prompt in prompt_params.keys():
        rc_config[0]['content'] = rc_settings['SYSTEM'].format(config=rc_settings[prompt]['instructions'].format(**prompt_params[prompt]))

    rc_config[-1]['content'] = prompt

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=rc_config,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "rc_output",
                "description": "The output of the room constructor.",
                "schema": {
                    "type": "object",
                    "properties": rc_settings[prompt]['outputs'],
                        "additionalProperties": False
                    }
                }
            }
    )

    rc_config.insert(1, {"role": "system", "content": f"PREVIOUS {prompt}: " + f"{response.choices[0].message.content}"})

    return response.choices[0].message.content

# --------------------------
# END ROOM CONSTRUCTOR AGENT
# --------------------------

# --------------------------
# DM AGENT
# --------------------------

# The settings for the DM agent:
dm_settings = {
    "SYSTEM": """
    You are the DUNGEON MASTER agent crafting a story with {setting}. You will do many things:
        1. You will always output JSON according to provided json_schema.
        2. You will adopt the following alignment and apply it where necessary: {dm_alignment}
        2. {config}
    """,
    "LOCKED ROOM": {
        "instructions":"""
        If prompted 'LOCKED ROOM' you will do the following:
            - a ~120 CHARACTER description of a locked door situated in the {direction} that will thematically fit the following room description: {description}
            - a description of the door to door_description
            - integrate the description of the locked door into the room description and output it as updated_description
            - create a description of the door unlocking and output it as unlock_description
            - integrate the description of the unlocked door into the room description and output it as unlocked_description
            - create the description of the area beyond the door, this would be the final area (a successful end to the adventure) where you detail the end of the journey and output it as win_description
            - outputs must be unique and not resemble previous responses
        """,
        "outputs": {
            "updated_description": {
                "description": "The updated description containing the original description and the appended description of the room if prompted 'LOCKED ROOM'.",
                "type": "string"
            },
            "door_description": {
                "description": "The description of the door if prompted 'LOCKED ROOM'.",
                "type": "string"
            },
            "unlock_description": {
                "description": "The description of the door unlocking if prompted 'LOCKED ROOM'.",
                "type": "string"
            },
            "unlocked_description": {
                "description": "The description of the room after the door is unlocked if prompted 'LOCKED ROOM'; should be the same as the updated_description except you detail that the door is open.",
                "type": "string"
            },
            "win_description": {
                "description": "The description of the area beyond the door if prompted 'LOCKED ROOM'.",
                "type": "string"
            }
        },
    },
    "HIDDEN ITEM":{
        "instructions":"""
        If prompted 'HIDDEN ITEM' you will do the following:
            - a ~120 CHARACTER description of the following item: {item}
            - a VERY SUBTLE hint of a hidden item that would encourage the player to search the area that thematically fits the following room description: {description}
            - DO NOT SUGGEST THAT THEY SEARCH IT OR HINT AT A MYSTERY, AND AVOID ADVERBS LIKE "SUSPICIOUSLY" OR "MYSTERIOUSLY"
            - AVOID USING TERMS LIKE "HIDDEN" OR "SECRET" OR "SOMETHING SEEMS..."
            - DESCRIBE THE ROOM AND AN ELEMENT OF IT IN A WAY THAT HINTS AT MYSTERY WITHOUT SUGGESTING A MYSTERY
            - integrate the hint description into the description and output it as updated_description
            - output the item's description as item_description
            - output the item's weight in lbs as item_weight
            - output the item's material as item_material
            - output the item's pickup description as pickup_description
            - output the room description after the item is picked up as empty_keyroom_description
            - outputs for updated_description, pickup_description, and item_description must be unique and not resemble previous responses
        """,
        "outputs": {
            "updated_description": {
                "description": "The updated description containing the original description and the appended description of the room if prompted 'HIDDEN ITEM'.",
                "type": "string"
            },
            "item_description": {
                "description": "The description of the item (just the item itself) if prompted 'HIDDEN ITEM'.",
                "type": "string"
            },
            "item_weight": {
                "description": "The weight of the item in lbs if prompted 'HIDDEN ITEM'.",
                "type": "number"
            },
            "item_material": {
                "description": "The material of the item if prompted 'HIDDEN ITEM'.",
                "type": "string"
            },
            "pickup_description": {
                "description": "The description of the item discovery if prompted 'HIDDEN ITEM', this will be shown when the player discovers the item, should align with the updated_description.",
                "type": "string"
            },
            "empty_keyroom_description": {
                "description": "The description of the room after the player has picked up the hidden item if prompted 'HIDDEN ITEM'.",
                "type": "string"
            }
        }
    },
    "NPC": {
        "instructions":"""
        If prompted 'NPC' you will do the following:
            - consider the NPC's sex: {sex}
            - consider the NPC's race: {race}
            - consider the NPC's alignment: {alignment}
            - consider the NPC's role: {role}
            - consider the NPC's class: {class}
            - output a first name for the NPC to npc_name that fits their race unrelated to any existing characters in other lore
            - output a ~180 CHARACTER description of the NPC to "description" that fits the setting, incorporating their race, alignment, role and class in a more abstract manner; avoid repeating words, terms and explicitly mentioning their alignment and role
            - output a single archetype for the NPC to "archetype" that fits their class, role and alignment
            - output an array of no more than 5 succinct traits for the NPC to "traits" that fits their race, alignment, class and role
            - output an array of no more than 5 dialogue examples for the NPC to "dialogue" that fits the setting, alignment, race, and role
            - outputs must be unique and not resemble previous responses
        """,
        "outputs": {
            "name": {
                "description": "The name of the NPC if prompted 'NPC'.",
                "type": "string"
            },
            "description": {
                "description": "The ~120 CHARACTER description of the NPC if prompted 'NPC'.",
                "type": "string"
            },
            "archetype": {
                "description": "A single archetype for the NPC if prompted 'NPC'.",
                "type": "string"
            },
            "traits": {
                "description": "An array of no more than 5 succinct traits for the NPC if prompted 'NPC'.",
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "dialogue": {
                "description": "An array of no more than 5 dialogue succinct examples for the NPC if prompted 'NPC'.",
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    },
    "INVENTORY": {
        "instructions":"""
        If prompted 'INVENTORY' you will do the following:
            - consider the player's inventory: {inventory}
            - output the inventory in a SHORT, descriptive manner to inventory_description
            - outputs must resemble previous responses
        """,
        "outputs": {
            "inventory_description": {
                "description": "The player's inventory presented in a curt descriptive manner if prompted 'INVENTORY'.",
                "type": "string"
            },
        }
    },
}

# Cofiguration for the DM agent, updated on each call to dm():
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

def dm(dm_alignment:str, prompt:str, setting:str, description:str=None, direction:str=None, item:str=None, inventory:list=None, npc:dict=None):

    """
    An agent that will update a room description based on a prompt.

    ARGUMENTS:
        dm_alignment (str): The alignment of the dungeon master. Passed from the alignments dictionary in modules.objects.config.
        prompt (str): Either 'LOCKED ROOM', 'HIDDEN ITEM', 'INVENTORY', or 'NPC'.
        setting (str): The setting of the room; what kind of location it is. Passed from the settings dictionary in modules.objects.config.
        description (str, optional): The description of the room.
        direction (str, optional): The direction of the locked door in the room.
        item (str, optional): The item that is hidden in the room. Defaults to None.
        inventory (list, optional): The player's inventory. Defaults to None.
        npc (dict, optional): The NPC that is in the room. Defaults to None.
    """

    global dm_config

    prompt_params = {
        'LOCKED ROOM': {
            'direction': direction,
            'description': description
        },
        'HIDDEN ITEM': {
            'description': description,
            'item': item
        },
        'INVENTORY': {
            'inventory': inventory
        },
        'NPC': {
            'sex': npc['sex'] if npc else None,
            'role': npc['role'] if npc else None,
            'race': npc['race'] if npc else None,
            'alignment': npc['alignment'] if npc else None,
            'class': npc['class_'] if npc else None,
        },
    }

    if prompt in prompt_params.keys():
        dm_config[0]['content'] = dm_settings['SYSTEM'].format(dm_alignment=dm_alignment, setting=setting, config=dm_settings[prompt]['instructions']).format(**prompt_params[prompt])

    dm_config[-1]['content'] = prompt

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
                    "properties": dm_settings[prompt]['outputs'],
                        "additionalProperties": False
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
# NPC CONVERSATION AGENT
# --------------------------

npc_settings = {
    "SYSTEM": """
    You are the NPC CONVERSATION agent. You will do one of many things:
        1. You will always output JSON according to provided json_schema.
        2. {config}
    """,
    "PLAYER": {
        "instructions":"""
        If prompted 'CONVERSATION' you will do the following:
            - consider the NPC's role: {role}
            - consider the NPC's class: {class}
            - consider the NPC's alignment: {alignment}
            - consider the NPC's archetype: {archetype}
            - consider the NPC's traits: {traits}
            - consider the NPC's dialogue samples: {dialogue}
            - consider the system and user messages that follow these intructions
            - output a response to the player's input to "response"
            - output must fit thematically with the dialogue samples
            - if the player repeats themselves, respond with a response similar to the one you output previously in response to the same input
            - if the player continues to repeat themselves, remind them that they're repeating themselves, then respond with a response similar to the one you output previously in response to the same input
        """,
        "outputs": {
            "response": {
                "description": "The response to the player's input.",
                "type": "string"
            }
        }
    }
}

npc_config = [
    {
        "role": "system",
        "content": None
    },
    {
        "role": "user",
        "content": None
    }
]
# --------------------------
# INPUT AGENT
# --------------------------

input_template = [
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

input_config = [
    {
        "role": "system",
        "content": None
    },
    {
        "role": "user",
        "content": None
    }
]

# --------------------------
# END INPUT AGENT
# --------------------------
