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


class _PathIs(enum.Enum):
    def _generate_next_value_(self: str, *args):
        return self.lower()


class PathIs(_PathIs):
    """
    Path Is Dir or File Enum Class.

    Examples:
        >>> from huti.enums import PathIs
        >>>
        >>> PathIs.EXISTS.value
        'exists'
    """
    EXISTS = enum.auto()
    IS_DIR = enum.auto()
    IS_FILE = enum.auto()


class _PathSuffix(enum.Enum):
    def _generate_next_value_(self: str, *args) -> pathlib.Path | Callable[[str], pathlib.Path]:
        return pathlib.Path(
            (f'__{self.rstrip("_")}__' if self.endswith('_') else '' if self == 'NONE' else self).lower())


class PathSuffix(_PathSuffix):
    # noinspection PyCallingNonCallable
    """
        Path Suffix Enum Class

        Examples:
            >>> from huti.enums import PathSuffix
            >>>
            >>> PathSuffix.TOML("hola")
            PosixPath('hola.toml')
            >>> PathSuffix.TOML.dot
            PosixPath('.toml')

        """
    NONE = enum.auto()  # ''
    BASH = enum.auto()
    CFG = enum.auto()
    ENV = enum.auto()
    GIT = enum.auto()
    GITCONFIG = enum.auto()
    INI = enum.auto()
    J2 = enum.auto()
    JINJA2 = enum.auto()
    JSON = enum.auto()
    LOG = enum.auto()
    MD = enum.auto()
    MONGO = enum.auto()
    OUT = enum.auto()
    PTH = enum.auto()
    PY = enum.auto()
    PYI = enum.auto()
    RLOG = enum.auto()
    RST = enum.auto()
    SCRIPTS = enum.auto()
    SH = enum.auto()
    SHELVE = enum.auto()
    SSH = enum.auto()
    TOML = enum.auto()
    TXT = enum.auto()
    YAML = enum.auto()
    YML = enum.auto()

    def __call__(self, name=None):
        return pathlib.Path((name if name else self.name) + self.dot.name)

    @property
    def dot(self): return pathlib.Path('.' + str(self.value.name))

    @property
    def name(self): return self.value.name


# noinspection PyCallingNonCallable
class FileName(enum.Enum):
    """
    File Names

    >>> from huti.enums import FileName
    >>>
    >>> FileName.INIT()
    PosixPath('__init__.py')
    >>> FileName.PYPROJECT()
    PosixPath('pyproject.toml')
    """
    INIT = PathSuffix.PY("__init__")
    MAIN = PathSuffix.PY("__main__")
    PACKAGE = PathSuffix.JSON("package")
    PYPROJECT = PathSuffix.TOML("pyproject")
    REQUIREMENTS = PathSuffix.TXT("requirements")
    README = PathSuffix.MD("README")
    SETTINGS = PathSuffix.INI("setup")
    SETUP = PathSuffix.CFG("setup")

    def __call__(self) -> pathlib.Path:
        return self.value
