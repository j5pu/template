"""
Huti Enums Module
"""
__all__ = (
    "ChainRV",
    "EnumLower",
    "PathIs",
    "PathSuffix",
    "FileName",
)

import enum
import pathlib
from typing import Callable


class EnumLower(enum.Enum):
    def _generate_next_value_(self: str, start, count: int, last_values) -> str:
        return str(self).lower()


class ChainRV(enum.Enum):
    ALL = enum.auto()
    FIRST = enum.auto()
    UNIQUE = enum.auto()

