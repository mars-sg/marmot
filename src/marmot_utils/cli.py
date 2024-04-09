import click

from .functions import *


@click.group()
def main():
    pass


@main.command()
@click.argument("path_to_model", type=click.Path(exists=True))
def upload(path_to_model: str) -> None:
    """Uploads a model to the model store"""
    validate_model(path_to_model, print=click.echo)
