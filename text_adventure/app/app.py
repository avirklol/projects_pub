import random
import numpy as np
import json
import click
from collections import deque
from modules import Room, Player, Item
from modules.ai import room_constructor, dm, settings, enemies, items, challenges

# --------------------------
# GAME OBJECTS ON LAUNCH
# --------------------------

grid = None # Used to store the grid. Used in the create_map() function.
grid_size = None # Used to store the size of the grid. Used in the create_grid() function.
grid_shape = None # Used to store the shape of the grid. Used in the create_map() function.
setting = random.choice(list(settings.values())) # Randomly select a setting from the settings dictionary. Used in the load_rooms() and modify_rooms() function.
enemy_group = random.choice(list(enemies.values())) # Randomly select a group of enemies from the enemies dictionary. Used in the load_rooms() function.
rooms = {} # Used to store and modify the rooms.
start_x, start_y = None, None
starting_room = None

# --------------------------
# MAP GENERATION FUNCTIONS
# --------------------------


# GRID CREATION:
def create_grid():

    global grid, grid_size, grid_shape, start_x, start_y, starting_room

    correct_input = True
    while True:
        if correct_input:
            grid_size = input("""Welcome to the MVP of the Text Adventure Game!
                            \nHow big of a map would like to play on? (Small, Medium, Large)\n
                            """).lower().strip()
        else:
            grid_size = input("\nSo how big of a map? (Small, Medium, Large)\n").lower().strip()

        if grid_size == "small":
            grid_size = random.choice([5, 7])
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

                enemy_roll = random.randint(1, 6) # Randomly determine if the room will have an enemy.

                if enemy_roll == 6:
                    ai_room = json.loads(room_constructor("ROOM + ENEMY", setting, random.choice(enemy_group)))
                else:
                    ai_room = json.loads(room_constructor("ROOM", setting))

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

    global rooms

    visited = set()  # Set to track visited rooms.
    queue = deque([starting_room])  # Initialize BFS queue with starting room.
    visited.add(starting_room)
    last_room_id = starting_room

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

        visited.remove(last_room_id)
        key_room_id = random.choice(list(visited))
        door_room_id = list(rooms[last_room_id].exits.values())[0]
        door_direction = None

        for direction, neighbor_id in rooms[door_room_id].exits.items():
            if neighbor_id == last_room_id:
                door_direction = direction

        key = Item(random.choice(items['keys']), key=True)

        key_room_data = json.loads(dm('HIDDEN ITEM', setting, rooms[key_room_id].description, item=key))
        door_room_data = json.loads(dm('LOCKED ROOM', setting, rooms[door_room_id].description, direction=door_direction))

        key.description = key_room_data['item_description']
        rooms[key_room_id].items.append(key)
        rooms[key_room_id].description = key_room_data['updated_description']
        rooms[door_room_id].description = door_room_data['updated_description']

        rooms[last_room_id].locked = True

        print(f"=====================================\n{rooms[last_room_id].name} has been locked.")
        print(f"=====================================\n{rooms[key_room_id].name} located at {rooms[key_room_id].location} has the key.")

    return rooms


def main():

    # Create grid:
    create_grid()

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

    # Create player
    player = Player(rooms[starting_room])

    # Game loop
    while True:
        player.status()
        command = input("\nWhat do you want to do? ").lower().split()

        if len(command) == 0:
            print("Please enter a command (go, take, inventory, quit).")
            continue

        if command[0] == "go":
            if len(command) > 1:
                player.move(command[1], rooms)
            else:
                print("Go where?")
        elif command[0] == "take":
            if len(command) > 1 and command[1] in player.current_room.items:
                player.inventory.append(command[1])
                player.current_room.items.remove(command[1])
                print(f"You took the {command[1]}.")
            else:
                print("Take what?")
        elif command[0] == "inventory":
            print(f"You are carrying: {', '.join(player.inventory) if player.inventory else 'nothing'}")
        elif command[0] == "quit":
            print("Thanks for playing!")
            break
        else:
            print("\nI don't understand that command.")

if __name__ == "__main__":
    main()
