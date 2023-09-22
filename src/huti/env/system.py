"""
System Environment Variables
"""
__all__ = (
    "ALPINE",
    "ALPINE_LIKE",
    "ARCH",
    "BUSYBOX",
    "CENTOS",
    "CLT",
    "COMPLETION",
    "CONTAINER",
    "DEBIAN",
    "DEBIAN_FRONTEND",
    "DEBIAN_LIKE",
    "DIST_CODENAME",
    "DIST_ID",
    "DIST_ID_LIKE",
    "DIST_UNKNOWN",
    "DIST_VERSION",
    "FEDORA",
    "FEDORA_LIKE",
    "HOMEBREW_CASK",
    "HOMEBREW_CELLAR",
    "HOMEBREW_ETC",
    "HOMEBREW_KEGS",
    "HOMEBREW_LIB",
    "HOMEBREW_OPT",
    "HOMEBREW_PREFIX",
    "HOMEBREW_PROFILE",
    "HOMEBREW_REPOSITORY",
    "HOMEBREW_TAPS",
    "HOST",
    "HOST_PROMPT",
    "KALI",
    "NIXOS",
    "PM",
    "PM_INSTALL",
    "PYTHON_VERSION",
    "RHEL",
    "RHEL_LIKE",
    "SSH",
    "UBUNTU",
    "UNAME",
)

from pathlib import Path

from .main import environment

ALPINE: bool
"""'DIST_ID' is 'alpine' and not: nix or busybox"""

ALPINE_LIKE: bool
"""'DIST_ID' is 'alpine'"""

ARCH: bool
"""'DIST_ID' is 'arch' for archlinux"""

BUSYBOX: bool
"""if not '/etc/os-release' and not '/sbin'."""

CENTOS: bool
"""'DIST_ID' is 'centos'"""

CLT: Path
"""Command Line Tools /usr directory (xcode-select -p)"""

COMPLETION: Path
"""BASH completion installation path"""

CONTAINER: bool
"""Running in docker container"""

DEBIAN: bool
"""'DIST_ID' is 'debian'"""

DEBIAN_FRONTEND: str
"""'noninteractive' if 'IS_CONTAINER' and 'DEBIAN_LIKE' are set"""

DEBIAN_LIKE: bool
"""'DIST_ID_LIKE is 'debian'"""

DIST_CODENAME: str
"""Distribution Codename: Catalina, Big Sur, kali-rolling, focal, etc."""

DIST_ID: str
"""alpine|centos|debian|kali|macOS|ubuntu|..."""

DIST_ID_LIKE: str
"""One of: alpine|debian|rhel fedora"""

DIST_UNKNOWN: str
"""'DIST_ID' is unknown"""

DIST_VERSION: str
"""Distribution Version: macOS (10.15.1, 10.16, ...), kali (2021.2, ...), ubuntu (20.04, ...)"""

FEDORA: bool
"""'DIST_ID' is 'fedora'"""

FEDORA_LIKE: bool
"""'DIST_ID' is 'fedora' or 'fedora' in 'DIST_ID_LIKE'"""

HOMEBREW_CASK: Path
"""Cask Versions (similar to opt)"""

HOMEBREW_CELLAR: Path
"""Version of formula, $HOMEBREW_PREFIX/opt is a symlink to $HOMEBREW_CELLAR"""

HOMEBREW_ETC: Path
"""Homebrew etc"""

HOMEBREW_KEGS: Path
"""Homebrew unlinked Kegs (in $HOMEBREW_OPT) to add to PATH"""

HOMEBREW_LIB: Path
"""Homebrew $HOMEBREW_PREFIX/lib"""

HOMEBREW_OPT: Path
"""Symlink for the latest version of formula to $HOMEBREW_CELLAR"""

HOMEBREW_PREFIX: Path
"""Homebrew prefix (brew shellenv)"""

HOMEBREW_PROFILE: Path
"""Profile compat dir (profile.d), under etc"""

HOMEBREW_REPOSITORY: Path
"""Repository and Library with homebrew gems and Taps (brew shellenv)"""

HOMEBREW_TAPS: Path
"""Taps path under '$HOMEBREW_REPOSITORY/Library'"""

HOST: str
"""First part of hostname: foo.com (foo), example.foo.com (example)"""

HOST_PROMPT: str
"""Symbol and 'HOST' if 'CONTAINER' or 'SSH'"""

KALI: bool
"""'DIST_ID' is 'kali'"""

NIXOS: bool
"""'DIST_ID' is 'alpine' and '/etc/nix'"""

PM: str
"""Default Package Manager: apk, apt, brew, nix and yum"""

PM_INSTALL: str
"""Default Package Manager with Install Options (Quiet and no cache for containers)"""

PYTHON_VERSION: str
"""Python Major and Minor Version"""

RHEL: bool
"""'DIST_ID' is 'rhel'"""

RHEL_LIKE: bool
"""'DIST_ID' is 'rhel' or 'rhel' in 'DIST_ID_LIKE'"""

SSH: bool
"""'SSH_CLIENT' or 'SSH_TTY' or 'SSH_CONNECTION'"""

UBUNTU: bool
"""'DIST_ID' is 'ubuntu'"""

UNAME: str
"""Operating System System Name: darwin or linux (same as 'sys.platform')"""

environment()
