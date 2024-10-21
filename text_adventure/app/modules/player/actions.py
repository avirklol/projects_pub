import click

def move(player, direction, rooms):
    if direction in player.current_room.exits:
        player.current_room = rooms[player.current_room.exits[direction]]
    else:
        click.echo(click.style("\nYou can't go that way!", fg="red"))
