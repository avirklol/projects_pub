import click

def status(player):
    room = player.current_room
    click.echo(click.style(f"\n--={room.name}=--  {room.location}", fg="yellow"))
    click.echo(click.style("---", fg="yellow"))
    click.echo(f"{room.description}")
    if room.enemy:
        click.echo(click.style(f"\nENEMY: {room.enemy}", fg="red"))
    if room.items:
        click.echo(click.style(f"\nITEMS: {', '.join(room.items)}", fg="yellow"))
    print(f"\nEXITS: {', '.join(room.exits.keys())}")
