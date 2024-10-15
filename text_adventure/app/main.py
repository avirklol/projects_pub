class Room:
    def __init__(self, name, description, items, exits):
        self.name = name
        self.description = description
        self.items = items
        self.exits = exits

class Player:
    def __init__(self, current_room):
        self.current_room = current_room
        self.inventory = []

def show_status(player):
    room = player.current_room
    print(f"\nYou are in {room.name}")
    print(room.description)
    if room.items:
        print(f"Items here: {', '.join(room.items)}")
    print(f"Exits: {', '.join(room.exits.keys())}")

def move_player(player, direction):
    if direction in player.current_room.exits:
        player.current_room = player.current_room.exits[direction]
    else:
        print("You can't go that way!")

def main():
    # Define rooms
    outside = Room("Outside", "You are standing outside a dark cave.", [], {"north": None})
    cave = Room("Cave Entrance", "The cave is dark and damp. You hear distant noises.", ["torch"], {"south": outside})
    outside.exits["north"] = cave

    # Create player
    player = Player(outside)

    # Game loop
    while True:
        show_status(player)
        command = input("\nWhat do you want to do? ").lower().split()

        if len(command) == 0:
            print("Please enter a command.")
            continue

        if command[0] == "go":
            if len(command) > 1:
                move_player(player, command[1])
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
            print("I don't understand that command.")

if __name__ == "__main__":
    main()
