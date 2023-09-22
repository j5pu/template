"""
System Environment Variables
"""
__all__ = (
    "LOGNAME",
    "OLDPWD",
    "PATH",
    "PWD",
    "SHELL",
    "SUDO_COMMAND",
    "SUDO_GID",
    "SUDO_UID",
    "SUDO_USER",
    "USER",
    "VIRTUAL_ENV",

)

from pathlib import Path

from .main import environment

LOGNAME: str
OLDPWD: Path
PATH: str
PWD: Path
SHELL: str
SUDO_COMMAND: str
SUDO_GID: int
SUDO_UID: int
SUDO_USER: str
USER: str
VIRTUAL_ENV: Path

environment()
