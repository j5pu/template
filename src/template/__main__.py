"""Main module for the CLI."""
import typer

app = typer.Typer(no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})
app_click = typer.main.get_command(app)
