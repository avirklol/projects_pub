import random
import click

class Player:
    def __init__(self, current_room:object):
        self.current_room = current_room
        self.stats = {
            "health": 100,
            "attack": 10,
            "defense": 5
        }
        self.inventory = []

    def status(self):
        click.echo(click.style(f"\n--={self.current_room.name}=--  {self.current_room.location}", fg="yellow"))
        click.echo(click.style("=====================================", fg="yellow"))
        click.echo(f"{self.current_room.description}")
        if self.current_room.enemy:
            click.echo(click.style(f"\nENEMY: {self.current_room.enemy}", fg="red"))
        if len(self.current_room.items) != 0:
            click.echo(click.style(f"\nITEMS: {', '.join(self.current_room.items)}", fg="yellow"))
        print(f"\nEXITS: {', '.join(self.current_room.exits.keys())}")

    def move(self, direction, rooms):
        if direction in self.current_room.exits:
            self.current_room = rooms[self.current_room.exits[direction]]
        else:
            click.echo(click.style("\nYou can't go that way!", fg="red"))

    def take (self, item):
        if item in self.current_room.items:
            self.inventory.append(item)
            self.current_room.items.remove(item)
            click.echo(click.style(f"\nYou picked up the {item}.", fg="green"))
        else:
            click.echo(click.style("\nThat item is not here.", fg="red"))
