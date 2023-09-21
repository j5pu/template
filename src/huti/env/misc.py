"""
System Environment Variables
"""
__all__ = (
  "FORCE_COLOR",
  "COLORIZE"
)

from .main import environment

COLORIZE: bool
"""
Forces showing or hiding colors and other styles colorized output.
To force hiding colors/styles in :class:`shrc.Color` and :class:`shrc.Symbol`, set this to either "False", "0", "off".
To force showing colors/styles in :class:`shrc.Color` and :class:`shrc.Symbol`, set this to either "True", "1", "on".
By default, click will remove color if the output does not look like an interactive terminal (default: variable unset)
"""
EXPAND_ALL: bool
"""rich.pretty.install(expand_all=os.environ.get("EXPAND_ALL", EXPAND_ALL_DEFAULT))"""
SHOW_LOCALS: bool
"""rich.traceback.install(show_locals=os.environ.get("SHOW_LOCALS", SHOW_LOCALS_DEFAULT))"""
FORCE_COLOR: bool
"""used by rich.console.Console.is_terminal"""
GITHUB_ACTION: str

environment()
