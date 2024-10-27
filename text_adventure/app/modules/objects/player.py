import random
import click
from modules.ai import locked_room_warning, direction_warning, item_not_found_warning, search_failure_warning, item_not_in_inventory_warning, useless_key_warning, item_not_usable_warning

class Player:
    def __init__(self, current_room:object):
        self.current_room = current_room
        self.stats = {
            "health": 100,
            "attack": 10,
            "defense": 5
        }
        self.inventory = {}

    def status(self):
        click.echo(click.style(f"\n--={self.current_room.name}=--  {self.current_room.location}", fg="yellow"))
        click.echo(click.style("=====================================", fg="yellow"))
        click.echo(f"{self.current_room.description}")

        if self.current_room.end_game:
            click.echo(click.style("\n-==THE END==-", fg="green"))

            while True:
                click.echo(click.style("\n\nTry again? (Y/N):", fg="yellow"))
                retry = input().lower().strip()

                if retry == "y":
                    return True
                elif retry == "n":
                    click.echo(click.style("\nThanks for playing!", fg="yellow"))
                    exit()
                else:
                    click.echo(click.style("\nInvalid input. Try again:", fg="red"))

        if self.current_room.enemy:
            click.echo(click.style(f"\nENEMY: {self.current_room.enemy}", fg="red"))

        if self.current_room.items:
            if len(self.current_room.items) == 1 and self.current_room.items[0].is_hidden:
                pass
            else:
                click.echo(click.style(f"\nITEMS: {', '.join(item.name for item in self.current_room.items if not item.is_hidden)}", fg="yellow"))

        print(f"\nEXITS: {', '.join(self.current_room.exits.keys())}")

    def move(self, direction, rooms):
        if direction not in self.current_room.exits:
            click.echo(click.style(f"\n{random.choice(direction_warning)}", fg="red"))
            input("\nContinue?")
            return

        if rooms[self.current_room.exits[direction]].locked:
            click.echo(click.style(f"\n{random.choice(locked_room_warning)}", fg="red"))
            input("\nContinue?")
            return

        self.current_room = rooms[self.current_room.exits[direction]]

    def take (self, item):

        if item in self.current_room.items and not item.is_hidden:
            self.inventory[f'{item.name}'] = item
            self.current_room.items.remove(item)
            click.echo(click.style(f"\nYou picked up the {item.name}.", fg="green"))
        else:
            click.echo(click.style(f"\n{random.choice(item_not_found_warning)}", fg="red"))

        input("\nContinue?")

    def search(self):
        if not self.current_room.items:
            click.echo(click.style(f"\n{random.choice(search_failure_warning)}", fg="red"))
            return

        for item in self.current_room.items:
            if item.is_hidden:
                item.is_hidden = False
                click.echo(click.style(f"\n{item.pickup_description}", fg="green"))
                self.current_room.description = self.current_room.new_description
                self.take(item)

    def use(self, item, rooms):
        if item not in self.inventory.keys():
            click.echo(click.style(f"\n{random.choice(item_not_in_inventory_warning)}", fg="red"))
            return

        item = self.inventory[item]

        if not item.is_usable:
            click.echo(click.style(f"\n{random.choice(item_not_usable_warning)}", fg="red"))
            return

        if item.is_usable and not item.is_key:
                item.use_effect(self)
                self.inventory.remove(item)

        if item.is_key:
            for room_id in self.current_room.exits.values():
                if rooms[room_id].locked:
                    rooms[room_id].locked = False
                    click.echo(click.style(f"\n{self.current_room.unlock_description}", fg="green"))
                    self.current_room.description = self.current_room.new_description
                    input("\nContinue?")
                    return
            else:
                click.echo(click.style(f"\n{random.choice(useless_key_warning)}", fg="red"))

        input("\nContinue?")
