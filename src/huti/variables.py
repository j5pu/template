"""
Huti Variables Module
"""
__all__ = (
    "BUILTIN",
    "BUILTIN_CLASS",
    "BUILTIN_CLASS_NO_EXCEPTION",
    "BUILTIN_CLASS_DICT",
    "BUILTIN_CLASS_NO_DICT",
    "BUILTIN_FUNCTION",
    "BUILTIN_MODULE_NAMES",
    "HUTI_SOURCES",
    "HUTI_PROJECT",
    "HUTI_ROOT",
)

import importlib
import os
import pwd
import sys
import types
from pathlib import Path

import rich.console

BUILTIN = (__i if isinstance(__i := globals()['__builtins__'], dict) else vars(__i)).copy()
BUILTIN_CLASS = tuple(filter(lambda x: isinstance(x, type), BUILTIN.values()))
BUILTIN_CLASS_NO_EXCEPTION = tuple(filter(lambda x: not issubclass(x, BaseException), BUILTIN_CLASS))
BUILTIN_CLASS_DICT = (classmethod, staticmethod, type, importlib._bootstrap.BuiltinImporter,)
BUILTIN_CLASS_NO_DICT = tuple(set(BUILTIN_CLASS_NO_EXCEPTION).difference(BUILTIN_CLASS_DICT))
BUILTIN_FUNCTION = tuple(filter(lambda x: isinstance(x, (types.BuiltinFunctionType, types.FunctionType,)),
                                BUILTIN.values()))
BUILTIN_MODULE_NAMES = sys.builtin_module_names
HUTI_SOURCES = Path(__file__).parent
"""Huti sources directory"""
HUTI_PROJECT = HUTI_SOURCES.name
"""Huti project name"""
HUTI_ROOT = HUTI_SOURCES.parent.parent
"""Huti Repository Path"""

