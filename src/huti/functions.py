"""
Huti Functions Module
"""

__all__ = (
    "cache",
    "exif_rm_tags",
    "pdf_diff",
    "pdf_from_picture",
    "pdf_linearize",
    "pdf_reduce",
    "pdf_scan",
    "pdf_to_picture",
    "python_latest",
    "python_version",
    "python_versions",
    "request_x_api_key_json",
    "strip",
)

import asyncio
import difflib
import functools
import inspect
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    Literal,
    Optional,
    cast,
)

import bs4
import fitz
import jsonpickle
import requests
import semver
import strip_ansi
import structlog
import toml
from ppip import command as command
from ppip import exec_module_from_file as exec_module_from_file
from ppip import find_file as find_file
from ppip import parent as parent
from ppip import stdout as stdout
from ppip import superproject as superproject
from ppip import supertop as supertop

from huti.alias import RunningLoop
from huti.classes import CalledProcessError, CmdError, FrameSimple, GroupUser, TempDir
from huti.constants import HUTI_DATA, PDF_REDUCE_THRESHOLD, PYTHON_FTP, SCAN_PREFIX, venv
from huti.datas import Top
from huti.enums import FileName, PathIs, PathSuffix
from huti.env import USER, VIRTUAL_ENV
from huti.exceptions import CommandNotFound, InvalidArgument
from huti.typings import AnyPath, ExcType, StrOrBytesPath
from huti.variables import EXECUTABLE, EXECUTABLE_SITE, PW_ROOT, PW_USER


def exif_rm_tags(file: Path | str):
    """Removes tags with exiftool in pdf"""
    which("exiftool", raises=True)

    subprocess.check_call(["exiftool", "-q", "-q", "-all=", "-overwrite_original", file])


def pdf_diff(file1: Path | str, file2: Path | str) -> list[bytes]:
    """
    Show diffs of two pdfs

    Args:
        file1:
        file2:

    Returns:
        True if equals
    """
    return list(
        difflib.diff_bytes(
            difflib.unified_diff, Path(file1).read_bytes().splitlines(), Path(file2).read_bytes().splitlines(), n=1
        )
    )


def pdf_from_picture(file: Path | str, picture: Path | str, rm: bool = True) -> Path:
    """
    Creates pdf from image

    Args:
        file: pdf file
        picture: image file
        rm: remove image file (default: True)
    """
    doc = fitz.Document()
    doc.new_page()
    page = doc[0]
    page.insert_image(page.rect, filename=picture)
    doc.save(Path(file))
    if rm:
        Path(picture).unlink()
    return file


def pdf_linearize(file: Path | str):
    """linearize pdf (overwrites original)"""
    which("qpdf")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir) / "tmp.pdf"
        subprocess.run(["qpdf", "--linearize", file, tmp])
        Path(tmp).replace(file)


def pdf_reduce(
        path: Path | str,
        level: Literal["/default", "/prepress", "ebook", "/screen"] = "/prepress",
        threshold: int | None = PDF_REDUCE_THRESHOLD,
):
    """
    Compress pdf

    https://www.adobe.com/acrobat/hub/how-to-compress-pdf-in-linux.html

    Examples:
        >>> import shutil
        >>> from huti.constants import HUTI_DATA_TESTS
        >>> from huti.functions import pdf_reduce
        >>>
        >>> original = HUTI_DATA_TESTS / "5.2M.pdf"
        >>> backup = HUTI_DATA_TESTS / "5.2M-bk.pdf"
        >>>
        >>> shutil.copyfile(original, backup)  # doctest: +ELLIPSIS
        PosixPath('.../huti/data/tests/5.2M-bk.pdf')
        >>> original_size = original.stat().st_size
        >>> pdf_reduce(original, level="/screen")
        >>> reduced_size = original.stat().st_size
        >>> assert original_size != reduced_size  # doctest: +SKIP
        >>> shutil.move(backup, original)  # doctest: +ELLIPSIS
        PosixPath('.../huti/data/tests/5.2M.pdf')

    Args:
        path:
        threshold: limit in MB to reduce file size, None to reuce any pdf
        level: /default is selected by the system, /prepress 300 dpi, ebook 150 dpi, screen 72 dpi

    Returns:

    """
    if threshold is None or Path(path).stat().st_size > threshold:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir) / "tmp.pdf"
            subprocess.check_call(
                [
                    "gs",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    f"-dPDFSETTINGS={level}",
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    f"-sOutputFile={tmp}",
                    path,
                ]
            )
            Path(tmp).replace(path)


def pdf_scan(file: Path, directory: Optional[Path] = None) -> Path:
    """
    Looks like scanned, linearize and sets tag color

    Examples:
        >>> from pathlib import Path
        >>> from huti.constants import HUTI_DATA
        >>> from huti.constants import HUTI_DATA_TESTS
        >>> from huti.constants import SCAN_PREFIX
        >>> from huti.functions import pdf_scan
        >>>
        >>> for f in Path(HUTI_DATA_TESTS).iterdir():
        ...     if f.is_file() and f.suffix == ".pdf":
        ...         assert f"generated/{SCAN_PREFIX}" in str(pdf_scan(f, HUTI_DATA_TESTS / "generated"))

    Args:
        file: path of file to be scanned
        directory: destination directory (Default: file directory)

    Returns:
        Destination file
    """
    rotate = round(random.uniform(*random.choice([(-0.9, -0.5), (0.5, 0.9)])), 2)

    file = Path(file)
    filename = f"{SCAN_PREFIX}{file.stem}{file.suffix}"
    if directory:
        directory = Path(directory)
        if not directory.is_dir():
            directory.mkdir(parents=True, exist_ok=True)
        dest = directory / filename
    else:
        dest = file.with_name(filename)

    which("convert", raises=True)

    subprocess.check_call(
        [
            "convert",
            "-density",
            "120",
            file,
            "-attenuate",
            "0.4",
            "+noise",
            "Gaussian",
            "-rotate",
            str(rotate),
            "-attenuate",
            "0.03",
            "+noise",
            "Uniform",
            "-sharpen",
            "0x1.0",
            dest,
        ]
    )
    return dest


def pdf_to_picture(file: Path | str, dpi: int = 300, fmt: Literal["jpeg", "png"] = "jpeg") -> Path:
    """Creates a file with jpeg in the same directory from first page of pdf"""
    which("pdftoppm")

    file = Path(file)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir) / "tmp"
        subprocess.run(["pdftoppm", f"-{fmt}", "-r", str(dpi), "-singlefile", file, tmp])
        suffix = f".{fmt}" if fmt == "png" else ".jpg"
        if not (dest := tmp.with_suffix(suffix)).exists():
            raise FileNotFoundError(f"File not found {dest}")
        return shutil.copy(dest, file.with_suffix(suffix))
