"""
Huti Exceptions Module
"""
__all__ = (
    "HutiBaseError",
    "CommandNotFound",
    "InvalidArgument",
)


class HutiBaseError(Exception):
    """
    Base Exception from which all other custom Exceptions defined in semantic_release
    inherit
    """


class CommandNotFound(HutiBaseError):
    """
    Raised when function is called with invalid argument
    """


class InvalidArgument(HutiBaseError):
    """
    Raised when function is called with invalid argument
    """

