import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['LANGCHAIN_TRACING_V2']='true'
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

locations = {
    'prison_cell': {
        'description': """
        A dank, dark cell with a single barred window in the south, a straw mattress underneath it, and a bucket in the south east corner.
        The only exit is a heavy iron door to the north, looking out into a dimly lit hallway; it remains locked unless the player can find a way to open it.
        """,
        'objects': {
            'straw mattress':{
                'description': 'A thin mattress made of straw. It looks uncomfortable.',
                'actions': {
                    'sleep on': """
                    The player can sleep on the matress, and will wake up after a reasonable time you see fit.
                    If the player chooses to sleep, they'll always sleep on the mattress, unless it has been destroyed.
                    """,
                    'search': """
                    The player can search the mattress and find a '2-inch rusted blade' inside,
                    which they can add to their inventory.
                    """,
                    'destroy': """
                    The player can destroy the mattress, and it will be removed from the game.
                    Revealing a '2-inch rusted blade' underneath, which they can add to their inventory.
                    They will have to sleep on the floor from then on.
                    """
                    }
            },
            'bucket':{
                'description': 'A metal bucket with a handle. It smells terrible and contains bodily waste.',
                'actions': {
                    'search': """
                    If the player searches the bucket, they will find a bodily waste inside.
                    """,
                    'empty': """
                    The player can empty the bucket, the bodily waste will line the south eastern floor of the cell.
                    """,
                    'throw': """
                    The player can throw the bucket in any direction, emptying its contents in that direction.
                    """
                    }
            },
            '2-inch rusted blade':{
                'description': """
                A small, rusted blade that looks like it could be used as a weapon.
                Can only be found by searching or destroying the straw mattress.
                """,
                'actions': {
                    'pick up': """
                    The player can pick up the blade and add it to their inventory.
                    """,
                    'stab': """
                    The player can stab with it.
                    """,
                    'slice': """
                    The player can slice with it.
                    """,
                    'throw': """
                    They player can throw it.
                    """
""                }
            }
    },
        'connected_locations': {
            'north': 'hallway'
        }
},
    'blackgate_prison': {
        'description': """
        A small, but imposing prison with a high, stone wall surrounding it.
        This is where the player is being held captive.
        The prison is empty, save for the player and a guard named Grum.
        It was built to hold the most dangerous criminals in the kingdom.
        """
},
    'Ardenia':{
        'description': """
        The kingdom of Ardenia is a vast, grim land, ruled by King Alaric, who hordes his wealth and power.
        The kingdom is known for its harsh laws and brutal punishments.
        The people of Ardenia are poor and oppressed, living in fear of the king's wrath.
        The setting is dark and foreboding, with a sense of danger lurking around every corner.
        This is a low-fantasy setting, with magic being rare and dangerous.
        Only humans and realistic animals exist in this setting.
        """
    }
}

guard = {
    'description': """
    His name is Liam, a royal guard who has been assigned to watch over the player.
    If called upon he will talk to the player, but only until he feels the player is wasting his time.
    You can make up a believable backstory for him if the player asks for one.
    """,
    "memory": ['saw the player being brought in',
               'has been assigned to watch over the player',
               'knows that the player was brought in for a crime against the king, but does not know the specifics of the crime',
               ]
}

player_actions = ['jailed for attempted theft of the royal seal']

rules = {}


dm = OpenAI(model='gpt-3.5-turbo-instruct')
setting = PromptTemplate(
    template="""
    You are the dungeon master of a text adventure game; responsible for the following:
    - Remembering the states of the game's {locations} and the {player_actions} by adding to/removing from them in the format that they're stored in
    - Playing the role of a single non-player character known as the {guard} and managing his memory, which is located in a list within the {guard} object
    - Describing the lore derived from {locations} to the player
    - Reacting to the {player_actions}
    - Adjudicating the {rules} of the game
    - Managing the player's {inventory}
    - At any point, you can give the player a chronological summary of their actions; weave it into the narrative.
""",
input_variables=['locations', 'player_actions', 'guard', 'rules', 'inventory']
)
