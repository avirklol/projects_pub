import random
import numpy as np
import json
import click
from collections import deque
from modules import Room, Player, NPC, Item, settings, items, item_conditions, challenges, directions, alignments, sexes, npc_race, npc_class, npc_roles
from modules.ai import room_constructor, dm

# DYNAMIC TEXT ADVENTURE FRAMEWORK
# --------------------------
# This is a dynamic text adventure game framework that generates a random map, populates it with rooms, enemies, and items, and creates challenges for the player to solve.
# As this project progresses, the framework will be expanded to include more features, such as combat, puzzles, and a more complex narrative.
# The idea would be able to create a text adventure game by simply importing the framework and customizing the settings, enemies, items, and challenges.
# A database could be used to store the settings/session state, npcs, map daya, items, and challenges.
#



# --------------------------
# GAME OBJECTS ON LAUNCH
# --------------------------

# GAME SETTINGS:
chosen_setting = random.choice(list(settings.values())) # Randomly select a setting from the settings dictionary. Used in load_rooms().
dm_alignment = random.choice(list(alignments.values())) # Randomly select an alignment from the alignments dictionary. Used in create_challenges().
challenge = random.choices(challenges) # Randomly select two challenges from the challenges dictionary. Used in create_challenges().

# NPC OBJECTS:
enemy = None # Used to store the enemy object. Set in load_rooms().

# MAP OBJECTS:
grid = None # Used to store the grid. Used in create_map().
grid_size = None # Used to store the size of the grid. Used in create_grid().
grid_shape = None # Used to store the shape of the grid. Used in create_map().
rooms = {} # Used to store and modify the rooms.
start_x, start_y = None, None # Used to store the starting coordinates. Used in create_grid().
starting_room = None # Used to store the starting room. Set in create_grid(), used in create_challenges().

# ALL CHALLENGE OBJECTS:
last_room_id = None # Used to store the last room visited. Used in create_challenges().

# LOCKED ROOM CHALLENGE OBJECTS:
key_room_id = None # Used to store the room id of the room with the key. Used in create_challenges().
door_room_id = None # Used to store the room id of the room with the door. Used in create_challenges().
door_room_neighbors_id = None # Used to store the neighbors of the door room. Used in create_challenges().
door_direction = None # Used to store the direction of the door. Used in create_challenges().
key_room_data = None # Used to store the data of the key room. Used in create_challenges().
door_room_data = None # Used to store the data of the door room. Used in create_challenges().

# GAME RESET OPTION:
reset = False # Used to reset the game. Used in main().

# --------------------------
# RANDOM MAP GENERATION FUNCTIONS
# --------------------------


# GRID CREATION:
def create_grid():

    """
    Creates the grid, a square array of zeroes, for the map.
    SETS: grid, grid_size, grid_shape, start_x, start_y, starting_room
    """

    global grid, grid_size, grid_shape, start_x, start_y, starting_room

    correct_input = True
    while True:
        if correct_input and not reset:
            click.echo(click.style("""\n\nWelcome to the MVP of the Text Adventure Game!\n\nHow big of a map would like to play on? (Small, Medium, Large)
                  """, fg="yellow"))
            grid_size = input().lower().strip()
        else:
            click.echo(click.style("\nSo, how big of a map would you like to play on? (Small, Medium, Large)", fg="yellow"))
            grid_size = input().lower().strip()

        if grid_size == "small":
            grid_size = random.choice([7])
            break
        if grid_size == "medium":
            grid_size = random.choice([9, 11])
            break
        if grid_size == "large":
            grid_size = random.choice([13, 15])
            break
        else:
            click.echo(click.style("\nPlease enter a valid grid size.\n", fg="red"))
            correct_input = False


    grid = np.zeros((grid_size, grid_size), dtype=int) # Create a grid of zeros.
    grid_shape = grid.shape[0] # Get the shape of the grid.
    start_x, start_y = random.sample(range(1, grid.shape[0]-1, 2), 2) # Randomly select starting coordinates.
    starting_room = f"room_{start_x}_{start_y}" # Set the starting room id.
    grid[start_x][start_y] = 1 # Mark the starting room.

# MAP GENERATION:
def create_map(x, y):

    """
    Recursive backtracking algorithm to generate the map, carving a path of rooms for the player to navigate.
    ADJUSTS: grid

    ARGUMENTS:
        x (int): The x-coordinate of the first room.
        y (int): The y-coordinate of the first room.
    """

    global grid

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)] # Define possible directions (NORTH, SOUTH, WEST, EAST).
    random.shuffle(directions)  # Randomize directions.

    for dx, dy in directions:
        nx, ny = x + dx, y + dy # Declare neighboring room coordinates.

        if 0 < nx < grid_shape - 1 and 0 < ny < grid_shape - 1:
            if grid[nx][ny] == 0:
                grid[(x + nx) // 2][(y + ny) // 2] = 1 # Remove wall between current room and neighboring room.
                grid[nx][ny] = 1  # Mark neighboring room as visited.
                create_map(nx, ny)  # Recursively call create_map() with the neighboring room as the new starting room.

# PRINT MAP (VISUALIZATION):
def print_map():

    """
    Prints the map as a visualization for debugging purposes.
    """

    for row in grid:
        print(''.join([' ' if cell else '█' for cell in row]))

# ROOM GENERATION:
def load_rooms():

    """
    Loads rooms into the rooms global dictionary, creating a room object for each room in the grid via room_constructor() from the ai module.
    """

    global rooms, enemy

    n = grid_shape

    for x in range(1, n):
        for y in range(1, n):
            if grid[x][y] == 1:
                room_id = f"room_{x}_{y}"
                exits = {}
                # Directions: (dx, dy)
                directions = {
                    'north': (-1, 0),
                    'south': (1, 0),
                    'west': (0, -1),
                    'east': (0, 1)
                }
                for direction, (dx, dy) in directions.items():
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n - 1 and 0 <= ny < n - 1 and grid[nx][ny] == 1:
                        neighbor_id = f"room_{nx}_{ny}"
                        exits[direction] = neighbor_id

                if random.randint(1, 6) == 6: # Randomly generate a room with an enemy.
                    enemy_details = {
                        "sex": random.choice(sexes),
                        "role": "enemy",
                        "race": random.choice(npc_race),
                        'alignment': random.choice(alignments['evil']),
                        'class_': random.choice(npc_class),
                    }

                    ai_enemy = json.loads(dm(dm_alignment, "NPC", chosen_setting, npc=enemy_details))

                    enemy = NPC(**(enemy_details | ai_enemy), is_hostile=True)

                    ai_room = json.loads(room_constructor("ROOM + NPC", chosen_setting, enemy))

                    enemy.dead_description = ai_room['npc_dead_description']
                else:
                    ai_room = json.loads(room_constructor("ROOM", chosen_setting))


                room = Room(
                    id = room_id,
                    location = (x, y),
                    name = ai_room['room_name'],
                    description = ai_room['room_description'],
                    npc = enemy if enemy else None,
                    exits = exits
                )
                rooms[room_id] = room

                if enemy:
                    enemy.current_room = room

                enemy = None

    return rooms

# CHALLENGE GENERATION AND ITEM PLACEMENT:
def create_challenges(challenge_type:str):

    """
    Creates a challenge based on the passed challenge_type argument. Updates room data using the dm() function from the ai module.
    SETS: door_room_id, key_room_id, door_direction, key_room_data, door_room_data
    ADJUSTS: rooms

    ARGUMENTS:
        challenge_type (str): The type of challenge to create. Typically passed as a random choice from the challenges list imported from modules.
    """

    global rooms, key_room_id, door_room_id, last_room_id, door_direction, key_room_data, door_room_data

    visited = set()  # Set to track visited rooms.
    queue = deque([starting_room])  # Initialize BFS queue with starting room.
    visited.add(starting_room)

    while queue:
        current_room = rooms[queue.popleft()]  # Get the next room object from the rooms dictionary.

        # Process the current room (for example, print details)
        print(f"Currently in {current_room.name}, located at {current_room.location}")
        if current_room.npc:
            print(f"There's an {current_room.npc.role} here: {current_room.npc.race}")

        # Iterate over each exit in the room
        for neighbor_id in current_room.exits.values():
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(neighbor_id)  # Add unvisited neighboring rooms to the queue

        last_room_id = current_room.id

    if challenge_type == "LOCKED ROOM":

        door_room_id = list(rooms[last_room_id].exits.values())[0] # Get the first neighbor of the last room visited.
        door_room_neighbors_id = list(rooms[door_room_id].exits.values()) # Get the neighbors of the door room.
        visited.discard(starting_room)  # Remove the starting room from the visited set.
        visited.discard(last_room_id) # Remove the last room from the visited set.
        visited.discard(door_room_id) # Remove the door room from the visited set.
        for id in door_room_neighbors_id:
            visited.discard(id) # Remove the neighbors of the door room from the visited set.

        key_room_id = random.choice(list(visited)) # Randomly select a room to place the key in from what's left in the visited set.

        key = Item('key', random.choice(items['keys']), condition=random.choice(item_conditions['keys']),is_key=True, is_hidden=True, is_usable=True) # Create a key item.
        key.location = key_room_id # Set the location of the key to the key room.

        # --------------------------
        # AI OPERATION
        # --------------------------

        for direction, neighbor_id in rooms[door_room_id].exits.items():
            if neighbor_id == last_room_id:
                door_direction = direction # Get the direction of the door.

        key_room_data = json.loads(dm(dm_alignment, 'HIDDEN ITEM', chosen_setting, rooms[key_room_id].description, item=key.name))
        door_room_data = json.loads(dm(dm_alignment, 'LOCKED ROOM', chosen_setting, rooms[door_room_id].description, direction=door_direction))

        # --------------------------
        # END OF AI OPERATION
        # --------------------------

        # UPDATE KEY ITEM DATA:
        key.description = key_room_data['item_description'] # Update the description of the key.
        key.pickup_description = key_room_data['pickup_description'] # Update the pickup description of the key.
        key.weight = key_room_data['item_weight'] # Update the weight of the key.
        key.material = key_room_data['item_material'].lower() # Update the material of the key.

        # UPDATE KEY ROOM DATA:
        rooms[key_room_id].items = [key] # Place the key in the key room.
        rooms[key_room_id].description = key_room_data['updated_description'] # Update the description of the key room.
        rooms[key_room_id].new_description = key_room_data['empty_keyroom_description'] # Update the new description of the key room after the player picks up the key.

        # UPDATE DOOR ROOM DATA:
        rooms[door_room_id].description = door_room_data['updated_description'] # Update the description of the door room.
        rooms[door_room_id].locked_door = True # Set the door room as a locked door room.
        rooms[door_room_id].locked_door_data['unlock_description'] = door_room_data['unlock_description'] # Update the unlock description of the door room.
        rooms[door_room_id].locked_door_data['key_id'] = key.id # Update the key id of the door room.
        rooms[door_room_id].locked_door_data['exit'] = last_room_id # Update the exit of the door room.
        rooms[door_room_id].locked_door_data['description'] = door_room_data['door_description'] # Update the description of the door.
        rooms[door_room_id].new_description = door_room_data['unlocked_description'] # Update the new description of the door room.

        # UPDATE LAST ROOM DATA:
        rooms[last_room_id].locked = True # Lock the last room visited.
        rooms[last_room_id].end_game = True # Set the last room visited as the end game room.
        rooms[last_room_id].description = door_room_data['win_description'] # Update the description of the last room visited.

        # DEBUG PRINT STATEMENTS (COMMENT OUT TO DISABLE):
        print(f"=====================================\n{rooms[last_room_id].name} has been locked.")
        print(f"=====================================\n{rooms[key_room_id].name} located at {rooms[key_room_id].location} has the key.")


def generate_random_map():

    """
    Generates a random map for a text adventure game.

    FUNCTIONS:
        create_grid(): Creates the grid for the map.
        create_map(x, y): Creates the map using a recursive backtracking algorithm.
        print_map(): Prints the map as a visualization.
        load_rooms(): Loads rooms into the rooms dictionary.
        create_challenges(challenge_type:str): Creates a challenge based on the passed challenge_type argument.
    """
    create_grid()
    create_map(start_x, start_y)
    print_map() # Print the map. Comment out to disable visualization.
    load_rooms()
    create_challenges(challenge)

# --------------------------
# END OF RANDOM MAP GENERATION FUNCTIONS
# --------------------------

# --------------------------
# GAME LOOP
# --------------------------

def main():

    global reset

    # Create map
    generate_random_map()

    reset = False

    # Create player:
    player = Player(rooms[starting_room])

    # --------------------------
    # GAME LOOP
    # --------------------------

    while True:

        reset = player.status()

        if reset:
            main() # Reset the game.
        else:
            click.echo(click.style("\nWhat do you want to do?\n", fg="yellow"))
            command = input().lower().split()

        if len(command) == 0:
            click.echo(click.style("Please enter a command (go, take, search, inventory, quit).", fg="red"))
            continue

        if command[0] == "go":
            if len(command) > 1:
                if command[1] not in directions:
                    click.echo(click.style("\nGo where?", fg="red"))
                player.move(command[1], rooms)
            else:
                click.echo(click.style("\nGo where?", fg="red"))

        elif command[0] == "take":
            if len(command) > 1:
                player.take(command[1], rooms)
            else:
                click.echo(click.style("\nTake what?", fg="red"))

        elif command[0] == "inventory":
            inventory = json.loads(dm('INVENTORY', chosen_setting, inventory=player.inventory.keys()))["inventory_description"]
            click.echo(click.style(f"\n{inventory}", fg="yellow"))
            input("\nContinue?")

        elif command[0] == "search":
            player.search()

        elif command[0] == "use":
            item = ""
            if len(command) > 1:
                for word in command[1:]:
                    item += word + " "
                player.use(item.strip(), rooms)
            else:
                click.echo(click.style("\nUse what?", fg="red"))

        elif command[0] == "quit":
            click.echo(click.style("\nThanks for playing!", fg="yellow"))
            break

        else:
            click.echo(click.style("\nI don't understand that command.", fg="red"))
            click.echo(click.style("\nPlease enter a command (go, take, search, inventory, quit).", fg="red"))
            input("\nContinue?")

if __name__ == "__main__":
    main()
