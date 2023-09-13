import rich.pretty
import rich.traceback

from huti.variables import CONSOLE

rich.pretty.install(CONSOLE, expand_all=True)
rich.traceback.install(show_locals=True)

