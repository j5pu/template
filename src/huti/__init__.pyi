import abc
import collections
import enum
from typing import Any
from typing import Iterable
from typing import MutableMapping
from typing import Type

__all__: tuple[str, ...] = ...

class ChainRV(enum.Enum):
    ALL = ...
    FIRST = ...
    UNIQUE = ...


class Chain(collections.ChainMap):
    rv: ChainRV
    default: Any
    maps: list[Iterable | Namedtuple | MutableMapping]

    def __init__(self, *maps: ..., rv: ChainRV = ..., default: Any = ...) -> None: ...

    def __getitem__(self, key: Any) -> Any: ...

    def __delitem__(self, key: Any) -> None: ...

    def delete(self, key: Any) -> Chain: ...

    def __setitem__(self, key: Any, value: Any) -> None: ...

    def set(self, key: Any, value: Any) -> None: ...


class Namedtuple(metaclass=abc.ABCMeta):
    # noinspection PyPep8Naming
    @classmethod
    def __subclasshook__(cls, C: Type) -> bool: ...

    @abc.abstractmethod
    def _asdict(self) -> dict[str, Any]: ...

    _fields: tuple[str, ...]
    _field_defaults: dict[str, Any]