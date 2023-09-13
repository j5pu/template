import abc

__all__: tuple[str, ...] = ...

class NamedtupleMeta(metaclass=abc.ABCMeta):
    # noinspection PyPep8Naming
    @classmethod
    def __subclasshook__(cls, C: Type) -> bool: ...

    @abc.abstractmethod
    def _asdict(self) -> dict[str, Any]: ...

    _fields: tuple[str, ...]
    _field_defaults: dict[str, Any]