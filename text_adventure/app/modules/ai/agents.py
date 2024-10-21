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

# The template for the Room Constructor agent.
rc_template = [
    {
        "role": "system",
        "content": """
        You are the ROOM CONSTRUCTOR agent. You will do one of two things:
        1. If prompted 'ROOM' you will output JSON data that describes a room inside of a {setting}.
        2. If prompted 'ROOM + ENEMY' you will output JSON data that describes a room inside of a {setting} with the following enemy inside: {enemy}
        REQUIREMENTS:
        - The room must have a name and description.
        - The room must have an enemy if prompted.
        - If the room has an enemy, the enemy must be included in the room description.
        - The response cannot resemble a previous response (room names and descriptions must be unique).
        - Enemies may be repeated.
        """
    },
    {
        "role": "user",
        "content": "{prompt}"
    }
]

# The configuration for the Room Constructor agent, updated on each call to room_constructor().
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
    """An agent that will construct a room based on a setting and include an enemy if prompted.

    Args:
        instruction (str): The instrctions for the Room Ronctructor agent, passed from the instructions dictionary in modules.ai.config as instructions['rc'].
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
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "description": "The name of the room in respect to the setting.",
                            "type": "string"
                        },
                        "description": {
                            "description": "A description of the room at around 140 characters, including an enemy if enemy is not NONE.",
                            "type": "string"
                        },
                        "enemy": {
                            "description": "The enemy passed in the instructions if ENEMY is mentioned in the prompt. None if ENEMY is not mentioned or is None.",
                            "type": "string"
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
