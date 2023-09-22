import enum
from enum import Enum
from typing import IO, Any

from .enums import EnumLower

__all__: tuple[str, ...] = ...


class _Color(EnumLower):
    # noinspection PyShadowingBuiltins
    def __call__(self,
                 message: Any = ...,
                 exit: int | None = ...,
                 stderr: bool = ...,
                 file: IO[Any] | str = ...,
                 newline: bool = ...,
                 bg: str | int | tuple[int, int, int] = ...,
                 bold: bool | None = ...,
                 dim: bool | None = ...,
                 underline: bool | None = ...,
                 overline: bool | None = ...,
                 italic: bool | None = ...,
                 blink: bool | None = ...,
                 reverse: bool | None = ...,
                 strikethrough: bool | None = ...,
                 reset: bool = ...,
                 colorize: bool | None = None) -> ...: ...


class _ColorAuto:
    value = enum._auto_null


class Color(_Color):
    BLACK = ...
    BLUE = ...
    CYAN = ...
    GREEN = ...
    MAGENTA = ...
    RED = ...
    WHITE = ...
    YELLOW = ...
    BRIGHT_BLACK = ...
    BRIGHT_BLUE = ...
    BRIGHT_CYAN = ...
    BRIGHT_GREEN = ...
    BRIGHT_MAGENTA = ...
    BRIGHT_RED = ...
    BRIGHT_WHITE = ...
    BRIGHT_YELLOW = ...
    RESET = ...

    def style(self, text: Any,
              bg: str | int | tuple[int, int, int] = ...,
              bold: bool | None = ...,
              dim: bool | None = ...,
              underline: bool | None = ...,
              overline: bool | None = ...,
              italic: bool | None = ...,
              blink: bool | None = ...,
              reverse: bool | None = ...,
              strikethrough: bool | None = ...,
              reset: bool = True) -> str: ...


COLOR_FIRST_OTHER = {
    "first": {"bold": ..., "italic": ..., },
    "other": {"bold": ..., "italic": ..., },
}
SYMBOL = {
    "CRITICAL": {"text": ..., "fg": ..., "blink": ..., },
    "ERROR": {"text": ..., "fg": ..., },
    "OK": {"text": ..., "fg": ..., },
    "NOTICE": {"text": ..., "fg": ..., },
    "SUCCESS": {"text": ..., "fg": ..., },
    "VERBOSE": {"text": ..., "fg": ..., },
    "WARNING": {"text": ..., "fg": ..., },
    "MINUS": {"text": ..., "fg": ..., },
    "MORE": {"text": ..., "fg": ..., },
    "MULTIPLY": {"text": ..., "fg": ..., },
    "PLUS": {"text": ..., "fg": ..., },
    "WAIT": {"text": ..., "fg": ..., },
}


class _Symbol(Enum):
    def _generate_next_value_(self: str, start: int, count: int, last_values: list[Any]) -> Any: ...

    def __call__(self,
                 first: Any = ...,
                 other: Any = ...,
                 separator: str = ...,
                 exit: int | None = ...,
                 stderr: bool = ...,
                 file: IO[Any] | str | None = ...,
                 newline: bool = ...,
                 colorize: bool | None = None) -> ...: ...


class _SymbolAuto:
    value: enum._auto_null


class Symbol(_Symbol):
    CRITICAL = ...
    ERROR = ...
    OK = ...
    NOTICE = ...
    SUCCESS = ...
    VERBOSE = ...
    WARNING = ...
    MINUS = ...
    MORE = ...
    MULTIPLY = ...
    PLUS = ...
    WAIT = ...
