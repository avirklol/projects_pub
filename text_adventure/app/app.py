import random
import numpy as np
import json
import click
from collections import deque
from modules import Room, Player, Item, settings, enemies, items, challenges, directions
from modules.ai import room_constructor, dm

# --------------------------
# GAME OBJECTS ON LAUNCH
# --------------------------

grid = None # Used to store the grid. Used in the create_map() function.
grid_size = None # Used to store the size of the grid. Used in the create_grid() function.
grid_shape = None # Used to store the shape of the grid. Used in the create_map() function.
chosen_setting = random.choice(list(settings.values())) # Randomly select a setting from the settings dictionary. Used in the load_rooms() and modify_rooms() function.
enemy_group = random.choice(list(enemies.values())) # Randomly select a group of enemies from the enemies dictionary. Used in the load_rooms() function.
rooms = {} # Used to store and modify the rooms.
start_x, start_y = None, None # Used to store the starting coordinates. Used in the create_grid() function.
starting_room = None # Used to store the starting room. Used in the create_map() function.

# LOCKED ROOM CHALLENGE OBJECTS:
key_room_id = None # Used to store the room id of the room with the key. Used in the create_challenges() function.
door_room_id = None # Used to store the room id of the room with the door. Used in the create_challenges() function.
door_room_neighbors_id = None # Used to store the neighbors of the door room. Used in the create_challenges() function.
door_direction = None # Used to store the direction of the door. Used in the create_challenges() function.
key_room_data = None # Used to store the data of the key room. Used in the create_challenges() function.
door_room_data = None # Used to store the data of the door room. Used in the create_challenges() function.

# GAME RESET OPTION:
reset = False # Used to reset the game. Used in the main() function.

# --------------------------
# MAP GENERATION FUNCTIONS
# --------------------------


# GRID CREATION:
def create_grid():

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


    grid = np.zeros((grid_size, grid_size), dtype=int)
    grid_shape = grid.shape[0]
    start_x, start_y = random.sample(range(1, grid.shape[0]-1, 2), 2)
    starting_room = f"room_{start_x}_{start_y}"

    return grid

# MAP GENERATION:
def create_map(x, y):

    global grid

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)] # Define possible directions (NORTH, SOUTH, WEST, EAST).
    random.shuffle(directions)  # Randomize directions.

    for dx, dy in directions:
        nx, ny = x + dx, y + dy # Declare neighboring room coordinates.

        if 0 < nx < grid_shape - 1 and 0 < ny < grid_shape - 1:
            if grid[nx][ny] == 0:
                grid[(x + nx) // 2][(y + ny) // 2] = 1 # Remove wall between current room and neighboring room.
                grid[nx][ny] = 1  # Mark neighboring room as visited.
                create_map(nx, ny)

    return grid

# PRINT MAP (VISUALIZATION):
def print_map():

    for row in grid:
        print(''.join([' ' if cell else '█' for cell in row]))

# ROOM GENERATION:
def load_rooms():

    global rooms

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
                    ai_room = json.loads(room_constructor("ROOM + ENEMY", chosen_setting, random.choice(enemy_group)))
                else:
                    ai_room = json.loads(room_constructor("ROOM", chosen_setting))

                room = Room(
                    id=room_id,
                    location=(x, y),
                    name= ai_room['name'],
                    description=ai_room['description'],
                    enemy=ai_room['enemy'],
                    exits=exits
                )
                rooms[room_id] = room

    return rooms

# CHALLENGE GENERATION AND ITEM PLACEMENT:
def create_challenges(challenge_type:str):

    global rooms, key_room_id, door_room_id, door_direction, key_room_data, door_room_data

    visited = set()  # Set to track visited rooms.
    queue = deque([starting_room])  # Initialize BFS queue with starting room.
    visited.add(starting_room)
    last_room_id = None

    while queue:
        current_room_id = queue.popleft()  # Get the next room from the queue
        current_room = rooms[current_room_id]

        # Process the current room (for example, print details)
        print(f"Currently in {current_room.name}, located at {current_room.location}")
        if current_room.enemy:
            print(f"There's an enemy here: {current_room.enemy}")

        # Iterate over each exit in the room
        for neighbor_id in current_room.exits.values():
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(neighbor_id)  # Add unvisited neighboring rooms to the queue

        last_room_id = current_room_id

    if challenge_type == "LOCKED ROOM":

        key = Item(random.choice(items['keys']), is_key=True, is_hidden=True, is_usable=True) # Create a key item.

        door_room_id = list(rooms[last_room_id].exits.values())[0] # Get the first neighbor of the last room visited.
        door_room_neighbors_id = list(rooms[door_room_id].exits.values()) # Get the neighbors of the door room.
        visited.discard(starting_room)  # Remove the starting room from the visited set.
        visited.discard(last_room_id) # Remove the last room from the visited set.
        visited.discard(door_room_id) # Remove the door room from the visited set.
        for id in door_room_neighbors_id:
            visited.discard(id) # Remove the neighbors of the door room from the visited set.

        key_room_id = random.choice(list(visited)) # Randomly select a room to place the key in.
        key.location = key_room_id # Set the location of the key to the key room.

        for direction, neighbor_id in rooms[door_room_id].exits.items():
            if neighbor_id == last_room_id:
                door_direction = direction

        key_room_data = json.loads(dm('HIDDEN ITEM', chosen_setting, rooms[key_room_id].description, item=key.name))
        door_room_data = json.loads(dm('LOCKED ROOM', chosen_setting, rooms[door_room_id].description, direction=door_direction))

        key.description = key_room_data['item_description'] # Update the description of the key.
        key.pickup_description = key_room_data['pickup_description'] # Update the pickup description of the key.
        key.weight = key_room_data['item_weight'] # Update the weight of the key.
        key.material = key_room_data['item_material'].lower()
        rooms[last_room_id].locked = True # Lock the last room visited.
        rooms[last_room_id].end_game = True # Set the last room visited as the end game room.
        rooms[last_room_id].description = door_room_data['win_description'] # Update the description of the last room visited.
        rooms[key_room_id].items = [key] # Place the key in the key room.
        rooms[key_room_id].description = key_room_data['updated_description'] # Update the description of the key room.
        rooms[key_room_id].new_description = key_room_data['empty_keyroom_description'] # Update the new description of the key room after the player picks up the key.
        rooms[door_room_id].description = door_room_data['updated_description'] # Update the description of the door room.
        rooms[door_room_id].unlock_description = door_room_data['unlock_description'] # Update the unlock description of the door room.
        rooms[door_room_id].new_description = door_room_data['unlocked_description'] # Update the new description of the door room.


        print(f"=====================================\n{rooms[last_room_id].name} has been locked.")
        print(f"=====================================\n{rooms[key_room_id].name} located at {rooms[key_room_id].location} has the key.")

    return rooms


def main():

    global reset

    # Create grid:
    create_grid()

    reset = False

    # Starting positions:
    grid[start_x][start_y] = 1

    # Generate map:
    create_map(start_x, start_y)

    # Print map (comment, if not needed):
    print_map()

    # Generate rooms:
    load_rooms()

    # Generate challenges:
    create_challenges(random.choice(challenges))

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
