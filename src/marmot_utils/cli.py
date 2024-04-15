import click

from .functions import *


@click.group()
def main():
    pass


@main.command()
@click.argument("path_to_model", type=click.Path(exists=True))
def upload(path_to_model: str) -> None:
    """Uploads a model to the model store"""
    if validate_model(path_to_model, print=click.echo):
        upload_model(path_to_model, print=click.echo)

    click.echo(f"==> Done!")


@main.command()
@click.argument("path_to_model", type=click.Path(exists=True))
@click.option("--repo", type=str, default="")
def validate(path_to_model: str, repo: str) -> None:
    """Validate model"""
    validate_model(
        path_to_model, print=click.echo, local_repo=repo if repo != "" else None
    )
