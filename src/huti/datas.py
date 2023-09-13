"""
Huti Data  Classes Module
"""
__all__ = (
    "Top",
)

import dataclasses
import pathlib


@dataclasses.dataclass
class Top:
    init_py: pathlib.Path | None
    installed: bool | None
    name: str
    path: pathlib.Path | None
    prefix: str
    pth: pathlib.Path | None
    pth_source: pathlib.Path | None
    pyproject_toml: pathlib.Path | None
    root: pathlib.Path | None
    top: pathlib.Path | None
    """Superproject top"""
    venv: pathlib.Path | None

