import random
import numpy as np
import json
import click
from modules import Room, Player
from modules.player import status, move
from modules.ai import room_constructor, settings, enemies

# grid generation
def create_grid():
    correct_input = True
    while True:
        if correct_input:
            grid_size = input("""Welcome to the MVP of the Text Adventure Game!
                            \nHow big of a map would like to play on? (Small, Medium, Large)
                            """).lower().strip()
        else:
            grid_size = input("So how big of a map? (Small, Medium, Large)").lower().strip()

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
    return grid

def create_map(grid, x, y, grid_shape):
    # Define possible directions (up, down, left, right)
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
    random.shuffle(directions)  # Randomize directions

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 < nx < grid_shape - 1 and 0 < ny < grid_shape - 1:
            if grid[nx][ny] == 0:
                # Remove wall between current cell and neighbor
                grid[(x + nx) // 2][(y + ny) // 2] = 1
                grid[nx][ny] = 1  # Mark neighbor as visited
                create_map(grid, nx, ny, grid_shape)

def print_map(grid):
    for row in grid:
        print(''.join([' ' if cell else '█' for cell in row]))

def load_rooms(grid, setting, enemy_group):
    rooms = {}
    n = grid.shape[0]

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


                # Create room with placeholder name, description, items and enemies:

                enemy_roll = random.randint(1, 6)

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
                    items=[],
                    exits=exits
                )
                rooms[room_id] = room
    return rooms

def main():
    # Define setting
    setting = random.choice(list(settings.values()))
    enemy_group = random.choice(list(enemies.values()))

    # Create grid
    grid = create_grid()

    # Starting positions
    x,y = random.sample(range(1, grid.shape[0]-1, 2), 2)
    starting_room = f"room_{x}_{y}"
    grid[x][y] = 1

    # Generate map
    create_map(grid, x, y, grid.shape[0])
    print_map(grid)

    # Generate rooms
    rooms = load_rooms(grid, setting, enemy_group)

    # Create player
    player = Player(rooms[starting_room])

    # Game loop
    while True:
        status(player)
        command = input("\nWhat do you want to do? ").lower().split()

        if len(command) == 0:
            print("Please enter a command (go, take, inventory, quit).")
            continue

        if command[0] == "go":
            if len(command) > 1:
                move(player, command[1], rooms)
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
