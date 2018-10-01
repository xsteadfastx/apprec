"""Client interface."""
import click

from apprec import core


def banner() -> None:
    """Print banner."""
    # pylint: disable=anomalous-backslash-in-string
    click.echo("\n")
    click.echo("     __,    _    _   ,_    _   __  ")
    click.echo("    /  |  |/ \_|/ \_/  |  |/  /    ")
    click.echo("    \_/|_/|__/ |__/    |_/|__/\___/")
    click.echo("         /|   /|                   ")
    click.echo("         \|   \|                   ")
    click.echo("\n")


@click.command()
@click.option("--audio-format", type=click.Choice(["wav"]), default="wav")
@click.argument("destination", type=click.Path())
def main(audio_format, destination):
    """Record pulseaudio stuff"""
    banner()
    inputs = core.get_inputs()
    if inputs:
        for index, audio_input in enumerate(inputs):
            click.echo(f"{index}: {audio_input[0]}")
        choosen_input = click.prompt("Choose input", type=int)
        core.main(audio_format, destination, inputs[choosen_input])
    else:
        click.echo("No inputs right now.")
        exit(1)
