__all__: tuple[str, ...] = ...

import collections
import subprocess
import tempfile
from pathlib import Path
from types import CodeType, FrameType
from typing import Any, AnyStr, Iterable, MutableMapping, NamedTuple, Sequence

from huti.enums import ChainRV
from huti.meta import NamedtupleMeta
from huti.typings import StrOrBytesPath

class CalledProcessError(subprocess.SubprocessError):
    returncode: int
    cmd: StrOrBytesPath | Sequence[StrOrBytesPath]
    output: AnyStr | None
    stdout: AnyStr | None
    stderr: AnyStr | None
    completed: subprocess.CompletedProcess | None

    def __init__(self, returncode: int | None = ...,
                 cmd: StrOrBytesPath | Sequence[StrOrBytesPath] | None = ...,
                 output: AnyStr | None = ..., stderr: AnyStr | None = ...,
                 completed: subprocess.CompletedProcess = ...) -> ...: ...

    def _message(self): ...

    def __str__(self): ...


class Chain(collections.ChainMap):
    rv: ChainRV
    default: Any
    maps: list[Iterable | NamedtupleMeta | MutableMapping]

    def __init__(self, *maps: ..., rv: ChainRV = ..., default: Any = ...) -> None: ...

    def __getitem__(self, key: Any) -> Any: ...

    def __delitem__(self, key: Any) -> None: ...

    def delete(self, key: Any) -> Chain: ...

    def __setitem__(self, key: Any, value: Any) -> None: ...

    def set(self, key: Any, value: Any) -> None: ...


class CmdError(subprocess.CalledProcessError):
    def __init__(self, process: subprocess.CompletedProcess | None = None): ...

    def __str__(self) -> str: ...


class FileConfig(NamedTuple):
    file: Path
    config: dict


class FrameSimple(NamedTuple):
    back: FrameType
    code: CodeType
    frame: FrameType
    function: str
    globals: dict[str, Any]
    lineno: int
    locals: dict[str, Any]
    name: str
    package: str
    path: Path
    vars: dict[str, Any]


class GroupUser(NamedTuple):
    group: int | str
    user: int | str


class LetterCounter:
    current_value: list[int]

    def __init__(self, start: str = ...): ...

    def increment(self) -> str: ...


class TempDir(tempfile.TemporaryDirectory):
    def __enter__(self) -> Path: ...
