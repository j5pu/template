"""
Huti Alias Module
"""
__all__ = (
    "ic",
    "icc",
    "ThreadLock",
    "LockClass",
    "ModuleSpec",
    "RunningLoop",
)
import asyncio.events
import importlib._bootstrap
import os
import threading

try:
    from icecream import IceCreamDebugger  # type: ignore[name-defined]

    ic = IceCreamDebugger(prefix="")
    icc = IceCreamDebugger(prefix="", includeContext=True)
    ic.enabled = icc.enabled = bool(os.environ.get("IC"))
except ModuleNotFoundError:
    def ic(*a):
        return None if not a else a[0] if len(a) == 1 else a


    def icc(*a):
        return None if not a else a[0] if len(a) == 1 else a

ThreadLock = threading.Lock
LockClass = type(ThreadLock())
ModuleSpec = importlib._bootstrap.ModuleSpec
RunningLoop = asyncio.events._RunningLoop

