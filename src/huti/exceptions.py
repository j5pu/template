"""
Huti Exceptions Module
"""
__all__ = (
    "HutiBaseError",
    "InvalidArgument",
)


class HutiBaseError(Exception):
    """
    Base Exception from which all other custom Exceptions defined in semantic_release
    inherit
    """


class InvalidArgument(HutiBaseError):
    """
    Raised when function is called with invalid argument
    """
