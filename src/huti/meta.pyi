import abc

__all__: tuple[str, ...] = ...

from typing import Any

class NamedtupleMeta(metaclass=abc.ABCMeta):
    # noinspection PyPep8Naming
    @classmethod
    def __subclasshook__(cls, C: type) -> bool: ...

    @abc.abstractmethod
    def _asdict(self) -> dict[str, Any]: ...

    _fields: tuple[str, ...]
    _field_defaults: dict[str, Any]
