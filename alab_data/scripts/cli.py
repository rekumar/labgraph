"""
Useful CLI tools for the alab_management package.
"""

import click

from .launch_client import launch_client, launch_dashboard
from alab_data.metadata import __version__

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group("cli", context_settings=CONTEXT_SETTINGS)
def cli():
    """ALab Data CLI tools"""
    click.echo(rf"""---  Alab Data v{__version__}  ----""")


# @cli.command("init", short_help="Init definition folder with default configuration")
# def init_cli():
#     if init_project():
#         click.echo("Done")
#     else:
#         click.echo("Stopped")


# @cli.command("setup", short_help="Read and write definitions to database")
# def setup_lab_cli():
#     if setup_lab():
#         click.echo("Done")
#     else:
#         click.echo("Stopped")


@cli.command("launch", short_help="Start to run the alab data GUI client + API")
@click.option(
    "--host",
    default="127.0.0.1",
)
@click.option("-p", "--port", default="8895", type=int)
@click.option("--debug", default=False, is_flag=True)
def launch_client_cli(host, port, debug):
    click.echo(f"The client will be served on http://{host}:{port}")
    launch_dashboard(host, port, debug)
