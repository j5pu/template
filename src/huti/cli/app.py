"""
huti.cli.app Module
"""
import typer

import huti.functions

app = typer.Typer(add_completion=False, context_settings={'help_option_names': ['-h', '--help']},
                  name="sitec")


@app.command()
def version():
    """
    Show huti version
    """
    print(huti.functions.version("huti"))
