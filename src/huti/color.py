"""
Huti Color Module
"""
__all__ = (
    "Color",
    "SYMBOL",
    "Symbol"
)
import enum
from pathlib import Path
from typing import IO, Any, Optional, cast

import click
import typer

from huti.enums import EnumLower


class _Color(EnumLower):
    # noinspection PyShadowingBuiltins
    def __call__(self,
                 message: Any = "",
                 exit: int | None = None,
                 stderr: bool = True,
                 file: Optional[IO[Any] | str] = None,
                 newline: bool = True,
                 bg: Optional[str | int | tuple[int, int, int]] = None,
                 bold: bool | None = None,
                 dim: bool | None = None,
                 underline: bool | None = None,
                 overline: bool | None = None,
                 italic: bool | None = None,
                 blink: bool | None = None,
                 reverse: bool | None = None,
                 strikethrough: bool | None = None,
                 reset: bool = True,
                 colorize: bool | None = None) -> None:
        """
        Wrapper for :func:`click.secho` getting the `fg` color from the enum.

        To force showing or hiding colors and other styles colorized output use ``COLORIZE`` environment variable,
        or set `colorize` to True or False respectively.

        This function combines echo and style into one call. As such the following two calls are the same:

            - click.secho('Hello World!', fg='green')
            - click.echo(click.style('Hello World!', fg='green'))

        All keyword arguments are forwarded to the underlying functions depending on which one they go with.

        Non-string types will be converted to str. However, bytes are passed directly to echo without applying style.
        If you want to style bytes that represent text, call `bytes.decode` first

        See `click.secho <https://click.palletsprojects.com/en/8.0.x/api/#click.secho>`_ for more information.

        Examples:
            >>> from huti.color import Color
            >>> Color.GREEN('Hello World!',)

        Arguments:
            message: Text to append to symbol (default: "")
            exit: Exit code, will exit if not None (default: None)
            stderr: Write to ``stderr`` instead of ``stdout`` (default: True)
            file: The file to write to. (default: ``stdout``)
            newline: Output new line (default: False)
            bg: Background color (default: None)
            bold: Bold text (default: None)
            dim: Dim (default: None)
            underline: Underline (default: None)
            overline: Overline (default: None)
            italic: Italic (default: None)
            blink: Blink (default: None)
            reverse: Reverse (default: None)
            strikethrough: Strikethrough (default: None)
            reset: Reset (default: True)
            colorize: Force showing or hiding colors and other styles. By default, click will remove color
                if the output does not look like an interactive terminal (default: ``COLORIZE`` environment variable)

        Returns
            None
        """
        from .env import COLORIZE

        click.secho(message, err=stderr, file=file, nl=newline, color=colorize or COLORIZE,
                    fg=self.value, bg=bg, bold=bold, dim=dim, underline=underline,
                    overline=overline, italic=italic, blink=blink, reverse=reverse,
                    strikethrough=strikethrough, reset=reset)
        if exit is not None:
            raise typer.Exit(exit)


class _ColorAuto:
    """
    Instances are replaced with an appropriate value in Enum class suites.
    """
    value = enum._auto_null


class Color(_Color):
    """:func:`click.secho` and :func:`click.style` foreground color wrapper class."""
    BLACK = enum.auto()
    """might be a gray"""
    BLUE = enum.auto()
    CYAN = enum.auto()
    GREEN = enum.auto()
    MAGENTA = enum.auto()
    RED = enum.auto()
    WHITE = enum.auto()
    """might be an grey"""
    YELLOW = enum.auto()
    """might be an orange"""
    BRIGHT_BLACK = enum.auto()
    BRIGHT_BLUE = enum.auto()
    BRIGHT_CYAN = enum.auto()
    BRIGHT_GREEN = enum.auto()
    BRIGHT_MAGENTA = enum.auto()
    BRIGHT_RED = enum.auto()
    BRIGHT_WHITE = enum.auto()
    BRIGHT_YELLOW = enum.auto()
    RESET = enum.auto()
    """reset the color only, not styles: bold, underline, etc."""

    def style(self, text: Any,
              bg: Optional[str | int | tuple[int, int, int]] = None,
              bold: bool | None = None,
              dim: bool | None = None,
              underline: bool | None = None,
              overline: bool | None = None,
              italic: bool | None = None,
              blink: bool | None = None,
              reverse: bool | None = None,
              strikethrough: bool | None = None,
              reset: bool = True) -> str:
        """
        Wrapper for :func:`click.style` getting the `fg` color from the enum.

        Styles a text with ANSI styles and returns the new string.

        By default, the styling is self-contained which means that at the end of the string a
            reset code is issued (this can be prevented by passing reset=False.

        If the terminal supports it, color may also be specified as:

            - An integer in the interval [0, 255]. The terminal must support 8-bit/256-color mode.
            - An RGB tuple of three integers in [0, 255]. The terminal must support 24-bit/true-color mode

        See `click.style <https://click.palletsprojects.com/en/8.0.x/api/#click.style>`_ for more information.

        Arguments:
          text: Text to apply style
          bg: Background color (default: None)
          bold: Bold text (default: None)
          dim: Dim (default: None)
          underline: Underline (default: None)
          overline: Overline (default: None)
          italic: Italic (default: None)
          blink: Blink (default: None)
          reverse: Reverse (default: None)
          strikethrough: Strikethrough (default: None)
          reset: Reset (default: True)

        Returns:
            Formatted text
        """
        return click.style(text,
                           fg=self.BLACK.value, bg=bg, bold=bold, dim=dim, underline=underline,
                           overline=overline, italic=italic, blink=blink, reverse=reverse,
                           strikethrough=strikethrough, reset=reset)


COLOR_FIRST_OTHER = {
    "first": {"bold": True, "italic": False, },
    "other": {"bold": False, "italic": True, },
}
"""Print format for the `first` part of text and the `other` part when calling :class:`Symbol`."""

SYMBOL = {
    "CRITICAL": {"text": "✘", "fg": Color.RED, "blink": True, },
    "ERROR": {"text": "✘", "fg": Color.RED, },
    "OK": {"text": "✔", "fg": Color.GREEN, },
    "NOTICE": {"text": "‼", "fg": Color.CYAN, },
    "SUCCESS": {"text": "◉", "fg": Color.BLUE, },
    "VERBOSE": {"text": "＋", "fg": Color.MAGENTA, },
    "WARNING": {"text": "！", "fg": Color.YELLOW, },
    "MINUS": {"text": "－", "fg": Color.RED, },
    "MORE": {"text": ">", "fg": Color.MAGENTA, },
    "MULTIPLY": {"text": "×", "fg": Color.BLUE, },
    "PLUS": {"text": "+", "fg": Color.RED, },
    "WAIT": {"text": "…", "fg": Color.YELLOW, },
}


class _Symbol(enum.Enum):
    def _generate_next_value_(self, start, count, last_values):
        return click.style(self, fg=cast(str, SYMBOL[self]["fg"].value), blink=SYMBOL[self].get("blink"), bold=True)

    # noinspection PyShadowingBuiltins
    def __call__(self,
                 first: Any = "",
                 other: Any = "",
                 separator: str = ":",
                 exit: int | None = None,
                 stderr: bool = True,
                 file: IO[Any] | str | None = None,
                 newline: bool = True,
                 colorize: bool | None = None) -> None:
        """
        Print symbol from :obj:`SYMBOL`, with text in `first` and `other` according to :obj:`FIRST_OTHER` format.

        Wrapper for :func:`click.echo` getting the `fg` color for the symbol from the :obj:`SYMBOL["fg"]`.

        If `other` is specified will be appended to `first` text in :obj:`FIRST_OTHER["other"]` format with `separator`.

        To force showing or hiding colors and other styles colorized output use ``COLORIZE`` environment variable,
        or set `colorize` to True or False respectively.

        Print a message and newline to stdout or a file. This should be used instead of print because it
        provides better support for different data, files, and environments.

        Compared to print, this does the following:

            - Ensures that the output encoding is not misconfiguration on Linux.
            - Supports Unicode in the Windows console.
            - Supports writing to binary outputs, and supports writing bytes to text outputs.
            - Supports colors and styles on Windows.
            - Removes ANSI color and style codes if the output does not look like an interactive terminal.
            - Always flushes the output.

        Arguments:
            first: First part of the text to append to :obj:`SYMBOL["text"]`
                in :obj:`FIRST_OTHER["first"]` format (default: "")
            other: Other parts to append to the `first` text in italic with `separator`
                in :obj:`FIRST_OTHER["other"]` format (default: "None")
            separator: Separator between `first` and `after` (default: ":")
            exit: Exit code, will exit if not None (default: None)
            stderr: Write to ``stderr`` instead of ``stdout`` (default: True)
            file: The file to write to. (default: ``stdout``)
            newline: Output new line (default: False)
            colorize: Force showing or hiding colors and other styles. By default, click will remove color
                if the output does not look like an interactive terminal (default: ``COLORIZE`` environment variable)
        """
        from .env import COLORIZE

        click.echo(
            " ".join([
                self.value,
                click.style(f"{first}{separator if other else ''}", **COLOR_FIRST_OTHER["first"]),
                click.style(other, **COLOR_FIRST_OTHER["other"]),
            ]),
            err=stderr, file=Path(file) if file else file, nl=newline, color=colorize or COLORIZE
        )
        if exit is not None:
            raise typer.Exit(exit)


class _SymbolAuto:
    """
    Instances are replaced with an appropriate value in Enum class suites.
    """
    value = enum._auto_null


class Symbol(_Symbol):
    """
    :func:`click.echo` and :func:`click.style` wrapper class for :data:`SYMBOLS`

    Examples:
        >>> from huti.color import Symbol
        >>>
        >>> Symbol.OK() # OK
        >>>
        >>> Symbol.OK("Install")  # OK Install
        >>>
        >>> Symbol.OK("Install", "Complete")  # OK Install: Complete
        >>>
        >>> Symbol.OK("Install", "Complete", stderr=False)
        OK Install: Complete
        >>>
        >>> Symbol.OK("Debug", "Error", " |", stderr=False)
        OK Debug | Error
        >>>
        >>> Symbol.OK("Value", "2", " ==", file="/tmp/test.txt")  # doctest: +SKIP
        >>>
        >>> Symbol.OK("Value", "2", newline=False)  # OK Value: 2
    """
    CRITICAL = enum.auto()
    """symbol: '…', color: YELLOW (blink)"""
    ERROR = enum.auto()
    """symbol: '✘', color: RED"""
    OK = enum.auto()
    """symbol: '✔', color: GREEN"""
    NOTICE = enum.auto()
    """symbol: '‼', color: CYAN"""
    SUCCESS = enum.auto()
    """symbol: '◉', color: BLUE"""
    VERBOSE = enum.auto()
    """symbol: '＋', color: MAGENTA"""
    WARNING = enum.auto()
    """symbol: '！', color: YELLOW"""
    MINUS = enum.auto()
    """letter: '-', color: RED"""
    MORE = enum.auto()
    """letter: '>, color: MAGENTA"""
    MULTIPLY = enum.auto()
    """letter: 'x', color: BLUE"""
    PLUS = enum.auto()
    """letter: '+', color: GREEN"""
    WAIT = enum.auto()
    """symbol: '…', color: YELLOW (blink)"""
