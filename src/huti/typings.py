"""
.dotfiles Typings Module
"""
import os
import tempfile
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Literal, Type, TypeAlias, Union

__all__ = (
    "AnyIO",
    "ExcType",
    "GitScheme",
    "PathType",
    "AnyPath",
    "StrOrBytesPath",
    "TemporaryFileType"
)

AnyIO = IO[AnyStr]
ExcType: TypeAlias = Type[Exception] | tuple[Type[Exception], ...]
GitScheme = Literal["git+file", "git+https", "git+ssh", "https", "ssh"]
PathType: TypeAlias = 'Path'
AnyPath: TypeAlias = Union[PathType, Path, PathLike, AnyStr, IO[AnyStr]]
StrOrBytesPath = str | bytes | os.PathLike[str] | os.PathLike[bytes]


class TemporaryFileType(type(tempfile.NamedTemporaryFile())):
    file: PathType = None
