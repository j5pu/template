"""
Huti Meta Module
"""
__all__ = (
    "NamedtupleMeta",
)

import abc


class NamedtupleMeta(metaclass=abc.ABCMeta):
    """
    namedtupl.

    Examples:
        >>> import collections
        >>> from huti.meta import NamedtupleMeta
        >>>
        >>> named = collections.namedtuple('named', 'a', defaults=('a', ))
        >>>
        >>> assert isinstance(named(), NamedtupleMeta) == True
        >>> assert isinstance(named(), tuple) == True
        >>>
        >>> assert issubclass(named, NamedtupleMeta) == True
        >>> assert issubclass(named, tuple) == True
    """
    _fields = ()
    _field_defaults = {}  # noqa: RUF012

    @abc.abstractmethod
    def _asdict(self):
        return {}

    # noinspection PyPep8Naming
    @classmethod
    def __subclasshook__(cls, C):
        if cls is NamedtupleMeta:
            return callable(C._asdict) and all([issubclass(C, tuple), hasattr(C, "_fields"),
                                                hasattr(C, "_field_defaults")])
        return NotImplemented
