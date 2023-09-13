"""
huti.cli.app Module
"""
import typer

app = typer.Typer(add_completion=False, context_settings=dict(help_option_names=['-h', '--help']),
                  name="sitec")
