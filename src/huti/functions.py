"""
Huti Functions Module
"""

__all__ = (
    "aiocmd",
    "aioclosed",
    "aiocommand",
    "aiodmg",
    "aiogz",
    "aioloop",
    "aioloopid",
    "aiorunning",
    "allin",
    "ami",
    "anyin",
    "brew_bundle",
    "cache",
    "chdir",
    "cmd",
    "cmdrun",
    "cmdsudo",
    "command",
    "current_task_name",
    "dependencies",
    "requirements",
    "dict_sort",
    "distribution",
    "dmg",
    "effect",
    "elementadd",
    "exif_rm_tags",
    "filterm",
    "findup",
    "firstfound",
    "flatten",
    "framesimple",
    "from_latin9",
    "fromiter",
    "getpths",
    "getsitedir",
    "getstdout",
    "group_user",
    "gz",
    "noexc",
    "parent",
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
    "sourcepath",
    "split_pairs",
    "stdout",
    "stdquiet",
    "strip",
    "superproject",
    "supertop",
    "suppress",
    "syssudo",
    "tag_latest",
    "tardir",
    "tilde",
    "timestamp_now",
    "toiter",
    "to_latin9",
    "tomodules",
    "top",
    "tox",
    "version",
    "which",
)

import asyncio
import collections
import contextlib
import difflib
import functools
import getpass
import grp
import importlib.metadata
import inspect
import io
import os
import pathlib
import platform
import pwd
import random
import re
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import time
import types
from pathlib import Path
from typing import (
    Any,
    AnyStr,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    Literal,
    MutableMapping,
    Optional,
    OrderedDict,
    ParamSpec,
    TextIO,
    TypeVar,
    cast,
)

import bs4
import fitz
import jsonpickle
import packaging.requirements
import requests
import semver
import strip_ansi
import structlog
import toml

from huti.alias import RunningLoop
from huti.classes import CalledProcessError, CmdError, FrameSimple, GroupUser, TempDir
from huti.constants import HUTI_DATA, PDF_REDUCE_THRESHOLD, PYTHON_FTP, SCAN_PREFIX, venv
from huti.datas import Top
from huti.enums import FileName, PathIs, PathSuffix
from huti.env import USER
from huti.exceptions import CommandNotFound, InvalidArgument
from huti.typings import AnyPath, ExcType, StrOrBytesPath
from huti.variables import EXECUTABLE, EXECUTABLE_SITE, PW_ROOT, PW_USER

P = ParamSpec("P")
T = TypeVar("T")
_KT = TypeVar("_KT")
_T = TypeVar("_T")
_VT = TypeVar("_VT")
_cache_which = {}


async def aiocmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Async Exec Command

    Examples:
        >>> import asyncio
        >>> from huti.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = asyncio.run(aiocmd("git", "clone", "https://github.com/octocat/Hello-World.git", cwd=tmp))
        ...     assert rv.returncode == 0
        ...     assert (tmp / "Hello-World" / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        JetBrainsError

    Returns:
        None
    """
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs
    )

    out, err = await proc.communicate()
    completed = subprocess.CompletedProcess(
        args, returncode=proc.returncode, stdout=out.decode() if out else None, stderr=err.decode() if err else None
    )
    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


def aioclosed() -> bool:
    """check if event loop is closed"""
    return asyncio.get_event_loop().is_closed()


async def aiocommand(
        data: str | list, decode: bool = True, utf8: bool = False, lines: bool = False
) -> subprocess.CompletedProcess:
    """
    Asyncio run cmd.

    Args:
        data: command.
        decode: decode and strip output.
        utf8: utf8 decode.
        lines: split lines.

    Returns:
        CompletedProcess.
    """
    proc = await asyncio.create_subprocess_shell(
        data, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, loop=asyncio.get_running_loop()
    )
    out, err = await proc.communicate()
    if decode:
        out = out.decode().rstrip(".\n")
        err = err.decode().rstrip(".\n")
    elif utf8:
        out = out.decode("utf8").strip()
        err = err.decode("utf8").strip()

    out = out.splitlines() if lines else out

    return subprocess.CompletedProcess(data, proc.returncode, out, cast(Any, err))


async def aiodmg(src: Path | str, dest: Path | str) -> None:
    """
    Async Open dmg file and copy the app to dest

    Examples:
        # >>> await dmg(Path("/tmp/JetBrains.dmg"), Path("/tmp/JetBrains"))

    Args:
        src: dmg file
        dest: path to copy to

    Returns:
        CompletedProcess
    """
    with TempDir() as tmpdir:
        await aiocmd("hdiutil", "attach", "-mountpoint", tmpdir, "-nobrowse", "-quiet", src)
        for item in src.iterdir():
            if item.name.endswith(".app"):
                await aiocmd("cp", "-r", tmpdir / item.name, dest)
                await aiocmd("xattr", "-r", "-d", "com.apple.quarantine", dest)
                await aiocmd("hdiutil", "detach", tmpdir, "-force")
                break


async def aiogz(src: Path | str, dest: Path | str = ".") -> Path:
    """
    Async ncompress .gz src to dest (default: current directory)

    It will be uncompressed to the same directory name as src basename.
    Uncompressed directory will be under dest directory.

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.functions import aiogz
        >>>
        >>> cwd = Path.cwd()
        >>> with TempDir() as workdir:
        ...     os.chdir(workdir)
        ...     with TempDir() as compress:
        ...         file = compress / "test.txt"
        ...         file.touch()  # doctest: +ELLIPSIS
        ...         compressed = tardir(compress)
        ...         with TempDir() as uncompress:
        ...             uncompressed = asyncio.run(aiogz(compressed, uncompress))
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: file to uncompress
        dest: destination directory to where uncompress directory will be created (default: current directory)

    Returns:
        Absolute Path of the Uncompressed Directory
    """
    return await asyncio.to_thread(gz, src, dest)


def aioloop() -> RunningLoop | None:
    """Get running loop"""
    return noexc(RuntimeError, asyncio.get_running_loop)


def aioloopid() -> int | None:
    """Get running loop id"""
    try:
        return asyncio.get_running_loop()._selector
    except RuntimeError:
        return None


def aiorunning() -> bool:
    """Check if event loop is running"""
    return asyncio.get_event_loop().is_running()


def allin(origin: Iterable, destination: Iterable) -> bool:
    """
    Checks all items in origin are in destination iterable.

    Examples:
        >>> from huti.functions import allin
        >>> from huti.variables import BUILTIN_CLASS
        >>>
        >>> class Int(int):
        ...     pass
        >>> allin(tuple.__mro__, BUILTIN_CLASS)
        True
        >>> allin(Int.__mro__, BUILTIN_CLASS)
        False
        >>> allin('tuple int', 'bool dict int')
        False
        >>> allin('bool int', ['bool', 'dict', 'int'])
        True
        >>> allin(['bool', 'int'], ['bool', 'dict', 'int'])
        True

    Args:
        origin: origin iterable.
        destination: destination iterable to check if origin items are in.

    Returns:
        True if all items in origin are in destination.
    """
    origin = toiter(origin)
    destination = toiter(destination)
    return all(x in destination for x in origin)


def ami(user: str = "root") -> bool:
    """
    Check if Current User is User in Argument (default: root)

    Examples:
        >>> from huti.functions import ami
        >>>
        >>> ami(os.getenv("USER"))
        True
        >>> ami()
        False

    Arguments:
        user: to check against current user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    return os.getuid() == pwd.getpwnam(user or getpass.getuser()).pw_uid


def anyin(origin: Iterable, destination: Iterable) -> Any | None:
    """
    Checks any item in origin are in destination iterable and return the first found.

    Examples:
        >>> from huti.functions import anyin
        >>> from huti.variables import BUILTIN_CLASS
        >>>
        >>> class Int(int):
        ...     pass
        >>> anyin(tuple.__mro__, BUILTIN_CLASS)
        <class 'tuple'>
        >>> assert anyin('tuple int', BUILTIN_CLASS) is None
        >>> anyin('tuple int', 'bool dict int')
        'int'
        >>> anyin('tuple int', ['bool', 'dict', 'int'])
        'int'
        >>> anyin(['tuple', 'int'], ['bool', 'dict', 'int'])
        'int'

    Args:
        origin: origin iterable.
        destination: destination iterable to check if any of origin items are in.

    Returns:
        First found if any item in origin are in destination.
    """
    origin = toiter(origin)
    destination = toiter(destination)
    for item in toiter(origin):
        if item in destination:
            return item


def brew_bundle(brewfile: Path | str = HUTI_DATA / "Brewfile", c: Optional[str] = None) -> int:
    """
    Installs brewfile under data directory

    Examples:
        >>> from huti.functions import brew_bundle
        >>> assert brew_bundle() == 0
        >>> assert brew_bundle(c="convert") is None

    Args:
        brewfile: brewfile to install
        c: command that needs to be absent to run brew bundle
    """

    if which("brew") and brewfile.exists() and (c is None or not which(c)):
        return subprocess.check_call(
            [
                "brew",
                "bundle",
                "--no-lock",
                "--quiet",
                f"--file={brewfile}",
            ]
        )


class _CacheWrapper(Generic[_T]):
    __wrapped__: Callable[..., _T]

    def __call__(self, *args: Any, **kwargs: Any) -> _T | Coroutine[Any, Any, _T]:
        ...


def cache(
        func: Callable[..., _T | Coroutine[Any, Any, _T]] = ...
) -> Callable[[Callable[..., _T]], _CacheWrapper[_T]] | _T | Coroutine[Any, Any, _T] | Any:
    """
    Caches previous calls to the function if object can be encoded.

    Examples:
        >>> import asyncio
        >>> from typing import cast
        >>> from typing import Coroutine
        >>> from environs import Env as Environs
        >>> from collections import namedtuple
        >>> from huti.functions import cache
        >>>
        >>> @cache
        ... def test(a):
        ...     print(True)
        ...     return a
        >>>
        >>> @cache
        ... async def test_async(a):
        ...     print(True)
        ...     return a
        >>>
        >>> test({})
        True
        {}
        >>> test({})
        {}
        >>> asyncio.run(cast(Coroutine, test_async({})))
        True
        {}
        >>> asyncio.run(cast(Coroutine, test_async({})))
        {}
        >>> test(Environs())
        True
        <Env {}>
        >>> test(Environs())
        <Env {}>
        >>> asyncio.run(cast(Coroutine, test_async(Environs())))
        True
        <Env {}>
        >>> asyncio.run(cast(Coroutine, test_async(Environs())))
        <Env {}>
        >>>
        >>> @cache
        ... class Test:
        ...     def __init__(self, a):
        ...         print(True)
        ...         self.a = a
        ...
        ...     @property
        ...     @cache
        ...     def prop(self):
        ...         print(True)
        ...         return self
        >>>
        >>> Test({})  # doctest: +ELLIPSIS
        True
        <....Test object at 0x...>
        >>> Test({})  # doctest: +ELLIPSIS
        <....Test object at 0x...>
        >>> Test({}).a
        {}
        >>> Test(Environs()).a
        True
        <Env {}>
        >>> Test(Environs()).prop  # doctest: +ELLIPSIS
        True
        <....Test object at 0x...>
        >>> Test(Environs()).prop  # doctest: +ELLIPSIS
        <....Test object at 0x...>
        >>>
        >>> Test = namedtuple('Test', 'a')
        >>> @cache
        ... class TestNamed(Test):
        ...     __slots__ = ()
        ...     def __new__(cls, *args, **kwargs):
        ...         print(True)
        ...         return super().__new__(cls, *args, **kwargs)
        >>>
        >>> TestNamed({})
        True
        TestNamed(a={})
        >>> TestNamed({})
        TestNamed(a={})
        >>> @cache
        ... class TestNamed(Test):
        ...     __slots__ = ()
        ...     def __new__(cls, *args, **kwargs): return super().__new__(cls, *args, **kwargs)
        ...     def __init__(self): super().__init__()
        >>> TestNamed({}) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: __init__() takes 1 positional argument but 2 were given
    """
    memo = {}
    log = structlog.get_logger()
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory())
    coro = inspect.iscoroutinefunction(func)
    if coro:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            """Async Cache Wrapper."""
            key = None
            save = True
            try:
                key = jsonpickle.encode((args, kwargs))
                if key in memo:
                    return memo[key]
            except Exception as exception:
                log.warning("Not cached", func=func, args=args, kwargs=kwargs, exception=exception)
                save = False
            value = await func(*args, **kwargs)
            if key and save:
                memo[key] = value
            return value
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Cache Wrapper."""
            key = None
            save = True
            try:
                key = jsonpickle.encode((args, kwargs))
                if key in memo:
                    return memo[key]
            except Exception as exception:
                log.warning("Not cached", func=func, args=args, kwargs=kwargs, exception=exception)
                save = False
            value = func(*args, **kwargs)
            if key and save:
                memo[key] = value
            return value
    return wrapper


@contextlib.contextmanager
def chdir(data: StrOrBytesPath | bool = True) -> Iterable[tuple[pathlib.Path, pathlib.Path]]:
    """
    Change directory and come back to previous directory.

    Examples:
        # FIXME: Ubuntu
        >>> from pathlib import Path
        >>> from huti.functions import chdir
        >>> from huti.variables import MACOS
        >>>
        >>> previous = Path.cwd()
        >>> new = Path('/usr/local')
        >>> with chdir(new) as (p, n):
        ...     assert previous == p
        ...     assert new == n
        ...     assert n == Path.cwd()
        >>>
        >>> new = Path('/bin/ls')
        >>> with chdir(new) as (p, n):
        ...     assert previous == p
        ...     assert new.parent == n
        ...     assert n == Path.cwd()
        >>>
        >>> new = Path('/bin/foo')
        >>> with chdir(new) as (p, n):
        ...     assert previous == p
        ...     assert new.parent == n
        ...     assert n == Path.cwd()
        >>>
        >>> with chdir() as (p, n):
        ...     assert previous == p
        ...     if MACOS
        ...         assert "var" in str(n)
        ...     assert n == Path.cwd() # doctest: +SKIP

    Args:
        data: directory or parent if file or True for temp directory

    Returns:
        Old directory and new directory
    """

    def y(new):
        os.chdir(new)
        return oldpwd, new

    oldpwd = pathlib.Path.cwd()
    try:
        if data is True:
            with TempDir() as tmp:
                yield y(tmp)
        else:
            yield y(parent(data, none=False))
    finally:
        os.chdir(oldpwd)


def cmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Exec Command

    Examples:
        >>> from huti.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = cmd("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        CmdError

    Returns:
        None
    """

    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


def cmdrun(
        data: Iterable, exc: bool = False, lines: bool = True, shell: bool = True, py: bool = False, pysite: bool = True
) -> subprocess.CompletedProcess | int | list | str:
    """
    Runs a cmd.

    Examples:
        >>> import huti
        >>> from huti.functions import cmdrun
        >>> from huti.functions import tox
        >>>
        >>> cmdrun('ls a')  # doctest: +ELLIPSIS
        CompletedProcess(args='ls a', returncode=..., stdout=[], stderr=[...])
        >>> assert 'Requirement already satisfied' in cmdrun('pip install pip', py=True).stdout[0]
        >>> cmdrun('ls a', shell=False, lines=False)  # doctest: +ELLIPSIS
        CompletedProcess(args=['ls', 'a'], returncode=..., stdout='', stderr=...)
        >>> cmdrun('echo a', lines=False)  # Extra '\' added to avoid docstring error.
        CompletedProcess(args='echo a', returncode=0, stdout='a\\n', stderr='')
        >>> assert "venv" not in cmdrun("sysconfig", py=True, lines=False).stdout
        >>> if not tox:
        ...     import sysconfig; print(sysconfig.get_paths())
        ...     print("No tox")
        ...     print(__file__)
        ...     assert "venv" in cmdrun("sysconfig", py=True, pysite=False, lines=False).stdout

    Args:
        data: command.
        exc: raise exception.
        lines: split lines so ``\\n`` is removed from all lines (extra '\' added to avoid docstring error).
        py: runs with python executable.
        shell: expands shell variables and one line (shell True expands variables in shell).
        pysite: run on site python if running on a VENV.

    Returns:
        Union[CompletedProcess, int, list, str]: Completed process output.

    Raises:
        CmdError:
    """
    if py:
        m = "-m"
        if isinstance(data, str) and data.startswith("/"):
            m = ""
        data = f"{EXECUTABLE_SITE if pysite else EXECUTABLE} {m} {data}"
    elif not shell:
        data = toiter(data)

    text = not lines

    proc = subprocess.run(data, shell=shell, capture_output=True, text=text)

    def std(out=True):
        if out:
            if lines:
                return proc.stdout.decode("utf-8").splitlines()
            else:
                # return proc.stdout.rstrip('.\n')
                return proc.stdout
        else:
            if lines:
                return proc.stderr.decode("utf-8").splitlines()
            else:
                # return proc.stderr.decode("utf-8").rstrip('.\n')
                return proc.stderr

    rv = subprocess.CompletedProcess(proc.args, proc.returncode, std(), std(False))
    if rv.returncode != 0 and exc:
        raise CmdError(rv)
    return rv


def cmdsudo(*args, user: str = "root", **kwargs) -> subprocess.CompletedProcess | None:
    """
    Run Program with sudo if user is different that the current user

    Arguments:
        *args: command and args to run
        user: run as user (Default: False)
        **kwargs: subprocess.run kwargs

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, *args], **kwargs)
    return None


def command(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Exec Command with the following defaults compared to :func:`subprocess.run`:

        - capture_output=True
        - text=True
        - check=True

    Examples:
        >>> from huti.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = command("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / ".git").exists()

    Args:
        *args: command and args
        **kwargs: `subprocess.run` kwargs

    Raises:
        CmdError

    Returns:
        None
    """

    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CalledProcessError(completed=completed)
    return completed


def current_task_name() -> str:
    """Current asyncio task name"""
    return asyncio.current_task().get_name() if aioloop() else ""


def dependencies(
        data: pathlib.Path | str | None = None, install: bool = False, upgrade: bool = False, extras: bool = True
) -> dict[str, list[packaging.requirements.Requirement]] | str | None:
    # noinspection PyUnresolvedReferences
    """
    List or install dependencies for a package from pyproject.toml, project directory (using pytproject.toml)
        or package name. If package name will search on Distribution

    Examples:
        >>> from pathlib import Path
        >>> import typer
        >>> import huti
        >>> from huti.functions import dependencies
        >>> from huti.functions import requirements
        >>> from huti.functions import superproject
        >>>
        >>> def names(req, k):
        ...     return [i.name for i in req[k]]
        >>>
        >>> def check(req, k, name):
        ...     assert name in names(req, k)
        >>>
        >>> def check_toml(req):
        ...     check(req, "dependencies", "beautifulsoup4")
        ...     check(req, "dev", "ipython")
        ...     check(req, "docs", "sphinx")
        ...     check(req, "tests", "pytest")
        >>>
        >>> def check_typer(req):
        ...     check(req, "dependencies", "click")
        ...     check(req, "all", "colorama")
        ...     check(req, "dev", "flake8")
        ...     check(req, "doc", "mkdocs")
        ...     check(req, "test", "pytest")

        >>> huti_root = supertop(huti.__file__)
        >>> check_toml(dependencies(huti_root))
        >>>
        >>> with chdir(huti_root):
        ...     check_toml(dependencies("pyproject.toml"))
        >>>
        >>> check_toml(dependencies())
        >>>
        >>> check_typer(dependencies("typer"))
        >>>
        >>> with chdir(parent(typer.__file__)):
        ...     check_typer(dependencies())

    Args:
        data: pyproject.toml path, package name to search in Distribution or project directory
            to find pyproject.toml.  If None, the default, will search up for the top
            of the project pyproject.toml or project name if installed in cwd.
        install: install requirements, False to list (default: True)
        upgrade: upgrade requirements (default: False)
        extras: extras (default: True)

    Returns:
        Requirements or None if install

    Raises:
        CalledProcessError: if pip install command fails.
        InvalidArgument: could not find pyproject.toml or should be: pyproject.toml path,
            package name to search in Distribution or project; directory to add pyproject.toml
    """

    # noinspection PyUnusedLocal
    def quote(d):
        return [f'"{i}"' if {">", "<"} & set(i) else i for i in d]

    deps, ex, error, read, up = [], {}, None, True, []

    if data is None:
        t = top()
        data = top().pyproject_toml
        if data is None and t.installed:
            data = t.name
        elif data is None:
            raise InvalidArgument(f"{t=}; could not find pyproject.toml or package name")

    if (pyproject := pathlib.Path(data)).is_file() is False and len(pyproject.parts) == 1:
        requires = importlib.metadata.Distribution.from_name(data).requires
        for item in requires:
            if "; extra" in item:
                values = item.split(" ; extra == ")
                key = values[1].replace('"', "")
                if key not in ex:
                    ex[key] = []
                ex[key].append(values[0])
            else:
                deps.append(item)
        read = False
    elif pyproject.is_file():
        pass
    elif pyproject.is_dir():
        pyproject /= "pyproject.toml"
        if not pyproject.is_file:
            error = True
    else:
        error = True

    if error:
        raise InvalidArgument(
            f"{data=}; should be: pyproject.toml path, "
            f"package name to search in Distribution or project; directory to add pyproject.toml"
        )

    if read:
        conf = toml.load(pyproject)
        deps = conf["project"]["dependencies"]
        if extras:
            ex = conf["project"]["optional-dependencies"]
    if install:
        if upgrade:
            up = [
                "--upgrade",
            ]
        if extras:
            ex = list(ex.values())
        return subprocess.check_output(
            [sys.executable, "-m", "pip", "install", *up, "-q", *(deps + flatten(ex, recurse=True))]
        ).decode()

    rv = {"dependencies": deps} | ex
    return {key: [packaging.requirements.Requirement(req) for req in value] for key, value in rv.items()}


requirements = dependencies


def dict_sort(
        data: dict[_KT, _VT], ordered: bool = False, reverse: bool = False
) -> dict[_KT, _VT] | OrderedDict[_KT, _VT]:
    """
    Order a dict based on keys.

    Examples:
        >>> from collections import OrderedDict
        >>> from huti.functions import dict_sort
        >>>
        >>> d = {"b": 2, "a": 1, "c": 3}
        >>> dict_sort(d)
        {'a': 1, 'b': 2, 'c': 3}
        >>> dict_sort(d, reverse=True)
        {'c': 3, 'b': 2, 'a': 1}
        >>> v = platform.python_version()
        >>> if "rc" not in v:
        ...     # noinspection PyTypeHints
        ...     assert dict_sort(d, ordered=True) == OrderedDict([('a', 1), ('b', 2), ('c', 3)])

    Args:
        data: dict to be ordered.
        ordered: OrderedDict.
        reverse: reverse.

    Returns:
        Union[dict, collections.OrderedDict]: Dict sorted
    """
    data = {key: data[key] for key in sorted(data.keys(), reverse=reverse)}
    if ordered:
        return collections.OrderedDict(data)
    return data


def distribution(data: Optional[pathlib.Path | str] = None) -> importlib.metadata.Distribution:
    """
    Package installed version

    Examples:
        >>> from importlib.metadata import Distribution
        >>> from huti.functions import distribution
        >>>
        >>> assert isinstance(distribution("rich"), Distribution)

    Args:
        data: package name or path to use basename (Default: `ROOT`)

    Returns
        Installed version
    """
    return suppress(
        importlib.metadata.Distribution.from_name,
        data if len(toiter(data, split="/")) == 1 else data.name,
        exception=importlib.metadata.PackageNotFoundError,
    )


def dmg(src: Path | str, dest: Path | str) -> None:
    """
    Open dmg file and copy the app to dest

    Examples:
        # >>> await dmg(Path("/tmp/JetBrains.dmg"), Path("/tmp/JetBrains"))

    Args:
        src: dmg file
        dest: path to copy to

    Returns:
        CompletedProcess
    """
    with TempDir() as tmpdir:
        cmd("hdiutil", "attach", "-mountpoint", tmpdir, "-nobrowse", "-quiet", src)
        for item in src.iterdir():
            if item.name.endswith(".app"):
                cmd("cp", "-r", tmpdir / item.name, dest)
                cmd("xattr", "-r", "-d", "com.apple.quarantine", dest)
                cmd("hdiutil", "detach", tmpdir, "-force")
                break


def effect(apply: Callable, *args: Iterable) -> None:
    """
    Perform function on iterable.

    Examples:
        >>> from types import SimpleNamespace
        >>> from huti.functions import effect
        >>> simple = SimpleNamespace()
        >>> effect(lambda x: simple.__setattr__(x, dict()), 'a b', 'c')
        >>> assert simple.a == {}
        >>> assert simple.b == {}
        >>> assert simple.c == {}

    Args:
        apply: Function to apply.
        *args: Iterable to perform function.

    Returns:
        No Return.
    """
    for arg in toiter(args):
        for item in arg:
            apply(item)


def elementadd(name: str | tuple[str, ...], closing: bool | None = False) -> str:
    """
    Converts to HTML element.
    >>> from huti.functions import elementadd
    >>>
    >>> assert elementadd('light-black') == '<light-black>'
    >>> assert elementadd('light-black', closing=True) == '</light-black>'
    >>> assert elementadd(('green', 'bold',)) == '<green><bold>'
    >>> assert elementadd(('green', 'bold',), closing=True) == '</green></bold>'

    Args:
        name: text or iterable text.
        closing: True if closing/end, False if opening/start.

    Returns:
        Str
    """
    return "".join(f'<{"/" if closing else ""}{i}>' for i in ((name,) if isinstance(name, str) else name))


def exif_rm_tags(file: Path | str):
    """Removes tags with exiftool in pdf"""
    which("exiftool", raises=True)

    subprocess.check_call(["exiftool", "-q", "-q", "-all=", "-overwrite_original", file])


def filterm(
        d: MutableMapping[_KT, _VT], k: Callable[..., bool] = lambda x: True, v: Callable[..., bool] = lambda x: True
) -> MutableMapping[_KT, _VT]:
    """
    Filter Mutable Mapping.

    Examples:
        >>> from huti.functions import filterm
        >>>
        >>> assert filterm({'d':1}) == {'d': 1}
        >>> # noinspection PyUnresolvedReferences
        >>> assert filterm({'d':1}, lambda x: x.startswith('_')) == {}
        >>> # noinspection PyUnresolvedReferences
        >>> assert filterm({'d': 1, '_a': 2}, lambda x: x.startswith('_'), lambda x: isinstance(x, int)) == {'_a': 2}

    Returns:
        Filtered dict with
    """
    # noinspection PyArgumentList
    return d.__class__({x: y for x, y in d.items() if k(x) and v(y)})


# TODO: findup, top, requirements with None, requirements install and upgrade y GitHub Actions
def findup(
        path: StrOrBytesPath = None,
        kind: PathIs = PathIs.IS_FILE,
        name: str | PathSuffix | pathlib.Path | Callable[..., pathlib.Path] = PathSuffix.ENV.dot,
        uppermost: bool = False,
) -> pathlib.Path | None:
    """
    Find up if name exists or is file or directory.

    Examples:
        >>> import email.mime.application
        >>> from pathlib import Path
        >>> import huti
        >>> import huti.cli
        >>> from huti.enums import PathSuffix, FileName
        >>> from huti.functions import chdir, findup, parent
        >>>
        >>>
        >>> file = Path(email.mime.application.__file__)
        >>>
        >>> with chdir(parent(huti.__file__)):
        ...     pyproject_toml = findup(huti.__file__, name=FileName.PYPROJECT())
        ...     assert pyproject_toml.is_file()
        >>>
        >>> with chdir(parent(huti.cli.__file__)):
        ...     cli_init_py = findup(name=FileName.INIT())
        ...     assert cli_init_py.is_file()
        ...     assert cli_init_py == Path(huti.cli.__file__)
        ...     huti_init_py = findup(name=FileName.INIT(), uppermost=True)
        ...     assert huti_init_py.is_file()
        ...     assert huti_init_py == Path(huti.__file__)
        >>>
        >>> assert findup(kind=PathIs.IS_DIR, name=huti.__name__) == Path(huti.__name__).parent.resolve()
        >>>
        >>> assert findup(file, kind=PathIs.EXISTS, name=FileName.INIT()) == file.parent / FileName.INIT()
        >>> assert findup(file, name=FileName.INIT()) == file.parent / FileName.INIT()
        >>> assert findup(file, name=FileName.INIT(), uppermost=True) == file.parent.parent / FileName.INIT()

    Args:
        path: CWD if None or Path.
        kind: Exists, file or directory.
        name: File or directory name.
        uppermost: Find uppermost found if True (return the latest found if more than one) or first if False.

    Returns:
        Path if found.
    """
    name = (
        name
        if isinstance(name, str)
        else name.name
        if isinstance(name, pathlib.Path)
        else name()
        if callable(name)
        else name.value
    )
    start = parent(path or os.getcwd())
    latest = None
    while True:
        if getattr(find := start / name, kind.value)():
            if not uppermost:
                return find
            latest = find
        if (start := start.parent) == pathlib.Path("/"):
            return latest


def firstfound(data: Iterable, apply: Callable) -> Any:
    """
    Returns first value in data if apply is True.

    Examples:
        >>> from huti.functions import firstfound
        >>>
        >>> assert firstfound([1, 2, 3], lambda x: x == 2) == 2
        >>> assert firstfound([1, 2, 3], lambda x: x == 4) is None

    Args:
        data: iterable.
        apply: function to apply.

    Returns:
        Value if found.
    """
    for i in data:
        if apply(i):
            return i


def flatten(
        data: tuple | list | set, recurse: bool = False, unique: bool = False, sort: bool = True
) -> tuple | list | set:
    """
    Flattens an Iterable

    Examples:
        >>> from huti.functions import flatten
        >>>
        >>> assert flatten([1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]]) == [1, 2, 3, 1, 5, 7, [2, 4, 1], 7, 6]
        >>> assert flatten([1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]], recurse=True) == [1, 1, 1, 2, 2, 3, 4, 5, 6, 7, 7]
        >>> assert flatten((1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]), unique=True) == (1, 2, 3, 4, 5, 6, 7)

    Args:
        data: iterable
        recurse: recurse
        unique: when recurse
        sort: sort

    Returns:
        Union[list, Iterable]:
    """
    if unique:
        recurse = True

    cls = data.__class__

    flat = []
    _ = [
        flat.extend(flatten(item, recurse, unique) if recurse else item)
        if isinstance(item, list)
        else flat.append(item)
        for item in data
        if item
    ]
    value = set(flat) if unique else flat
    if sort:
        try:
            value = cls(sorted(value))
        except TypeError:
            value = cls(value)
    return value


def framesimple(data: inspect.FrameInfo | types.FrameType | types.TracebackType) -> FrameSimple | None:
    """
    :class:`rc.FrameSimple`.

    Examples:
        >>> import inspect
        >>> from huti.functions import framesimple
        >>>
        >>> frameinfo = inspect.stack()[0]
        >>> finfo = framesimple(frameinfo)
        >>> ftype = framesimple(frameinfo.frame)
        >>> assert frameinfo.frame.f_code == finfo.code
        >>> assert frameinfo.frame == finfo.frame
        >>> assert frameinfo.filename == str(finfo.path)
        >>> assert frameinfo.lineno == finfo.lineno
        >>> fields_frame = list(FrameSimple._fields)
        >>> fields_frame.remove('vars')
        >>> for attr in fields_frame:
        ...     assert getattr(finfo, attr) == getattr(ftype, attr)

    Returns:
        :class:`FrameSimple`.
    """
    if isinstance(data, inspect.FrameInfo):
        frame = data.frame
        back = frame.f_back
        lineno = data.lineno
    elif isinstance(data, types.FrameType):
        frame = data
        back = data.f_back
        lineno = data.f_lineno
    elif isinstance(data, types.TracebackType):
        frame = data.tb_frame
        back = data.tb_next
        lineno = data.tb_lineno
    else:
        return

    code = frame.f_code
    f_globals = frame.f_globals
    f_locals = frame.f_locals
    function = code.co_name
    v = f_globals | f_locals
    name = v.get("__name__") or function
    return FrameSimple(
        back=back,
        code=code,
        frame=frame,
        function=function,
        globals=f_globals,
        lineno=lineno,
        locals=f_locals,
        name=name,
        package=v.get("__package__") or name.split(".")[0],
        path=sourcepath(data),
        vars=v,
    )


def from_latin9(*args) -> str:
    """
    Converts string from latin9 hex

    Examples:
        >>> from huti.functions import from_latin9
        >>>
        >>> from_latin9("f1")
        'ñ'
        >>>
        >>> from_latin9("4a6f73e920416e746f6e696f205075e972746f6c6173204d6f6e7461f1e973")
        'José Antonio Puértolas Montañés'
        >>>
        >>> from_latin9("f1", "6f")
        'ño'

    Args:
        args:

    Returns:
        str
    """
    rv = ""
    if len(args) == 1:
        pairs = split_pairs(args[0])
        for pair in pairs:
            rv += bytes.fromhex("".join(pair)).decode("latin9")
    else:
        for char in args:
            rv += bytes.fromhex(char).decode("latin9")
    return rv


def fromiter(data, *args):
    """
    Gets attributes from Iterable of objects and returns dict with

    Examples:
        >>> from types import SimpleNamespace as Simple
        >>> from huti.functions import fromiter
        >>>
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], 'a', 'b', 'c') == {'a': [1, 2], 'b': [1]}
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], ('a', 'b', ), 'c') == {'a': [1, 2], 'b': [1]}
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], 'a b c') == {'a': [1, 2], 'b': [1]}

    Args:
        data: object.
        *args: attributes.

    Returns:
        Tuple
    """
    value = {k: [getattr(C, k) for C in data if hasattr(C, k)] for i in args for k in toiter(i)}
    return {k: v for k, v in value.items() if v}


def getpths() -> dict[str, pathlib.Path] | None:
    """
    Get list of pths under ``sitedir``

    Examples:
        >>> from huti.functions import getpths
        >>>
        >>> pths = getpths()
        >>> assert "distutils-precedence" in pths

    Returns:
        Dictionary with pth name and file
    """
    try:
        sitedir = getsitedir()
        names = os.listdir(sitedir)
    except OSError:
        return
    return {
        re.sub("(-[0-9].*|.pth)", "", name): pathlib.Path(sitedir / name) for name in names if name.endswith(".pth")
    }


def getsitedir(index: bool = 2) -> pathlib.Path:
    """Get site directory from stack if imported by :mod:`site` in a ``.pth``file or :mod:`sysconfig`

    Examples:
        >>> from huti.functions import getsitedir
        >>> assert "packages" in str(getsitedir())

    Args:
        index: 1 if directly needed by this function (default: 2), for caller to this function

    Returns:
        Path instance with site directory
    """
    if (sitedir := sys._getframe(index).f_locals.get("sitedir")) is None:
        sitedir = sysconfig.get_paths()["purelib"]
    return pathlib.Path(sitedir)


def getstdout(func: Callable, *args: Any, ansi: bool = False, new: bool = True, **kwargs: Any) -> str | Iterable[str]:
    """
    Redirect stdout for func output and remove ansi and/or new line.

    Args:
        func: callable.
        *args: args to callable.
        ansi: strip ansi.
        new: strip new line.
        **kwargs: kwargs to callable.

    Returns:
        str | Iterable[str, str]:
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        func(*args, **kwargs)
    return strip(buffer.getvalue(), ansi=ansi, new=new) if ansi or new else buffer.getvalue()


def group_user(name: int | str = USER) -> GroupUser:
    """
    Group and User for Name (id if name is str and vice versa).

    Examples:
        >>> import os
        >>> import pathlib
        >>>
        >>> from huti.functions import group_user
        >>> from huti.variables import PW_USER, PW_ROOT
        >>>
        >>> s = pathlib.Path().stat()
        >>> gr = group_user()
        >>> assert gr.group == s.st_gid and gr.user == s.st_uid
        >>> gr = group_user(name=PW_USER.pw_uid)
        >>> actual_gname = gr.group
        >>> assert gr.group != PW_ROOT.pw_name and gr.user == PW_USER.pw_name
        >>> gr = group_user('root')
        >>> assert gr.group != s.st_gid and gr.user == 0
        >>> gr = group_user(name=0)
        >>> assert gr.group != actual_gname and gr.user == 'root'

    Args:
        name: usename or id (default: `data.ACTUAL.pw_name`)

    Returns:
        GroupUser.
    """
    if isinstance(name, str):
        struct = (
            struct if name == (struct := PW_USER).pw_name or name == (struct := PW_ROOT).pw_name else pwd.getpwnam(name)
        )
        return GroupUser(group=struct.pw_gid, user=struct.pw_uid)
    struct = struct if name == (struct := PW_USER).pw_uid or name == (struct := PW_ROOT).pw_uid else pwd.getpwuid(name)
    return GroupUser(group=grp.getgrgid(struct.pw_gid).gr_name, user=struct.pw_name)


def gz(src: Path | str, dest: Path | str = ".") -> Path:
    """
    Uncompress .gz src to dest (default: current directory)

    It will be uncompressed to the same directory name as src basename.
    Uncompressed directory will be under dest directory.

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.functions import gz
        >>> cwd = Path.cwd()
        >>> with TempDir() as workdir:
        ...     os.chdir(workdir)
        ...     with TempDir() as compress:
        ...         file = compress / "test.txt"
        ...         file.touch()  # doctest: +ELLIPSIS
        ...         compressed = tardir(compress)
        ...         with TempDir() as uncompress:
        ...             uncompressed = gz(compressed, uncompress)
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: file to uncompress
        dest: destination directory to where uncompress directory will be created (default: current directory)

    Returns:
        Absolute Path of the Uncompressed Directory
    """
    dest = Path(dest)
    with tarfile.open(src, "r:gz") as tar:
        tar.extractall(dest)
        return (dest / tar.getmembers()[0].name).parent.absolute()


def noexc(
        func: Callable[..., _T], *args: Any, default_: Any = None, exc_: ExcType = Exception, **kwargs: Any
) -> _T | Any:
    """
    Execute function suppressing exceptions.

    Examples:
        >>> from huti.functions import noexc
        >>> assert noexc(dict(a=1).pop, 'b', default_=2, exc_=KeyError) == 2

    Args:
        func: callable.
        *args: args.
        default_: default value if exception is raised.
        exc_: exception or exceptions.
        **kwargs: kwargs.

    Returns:
        Any: Function return.
    """
    try:
        return func(*args, **kwargs)
    except exc_:
        return default_


def parent(path: StrOrBytesPath = pathlib.Path(__file__), none: bool = True) -> pathlib.Path | None:
    """
    Parent if File or None if it does not exist.

    Examples:
        >>> from huti.functions import parent
        >>>
        >>> parent("/bin/ls")
        PosixPath('/bin')
        >>> parent("/bin")
        PosixPath('/bin')
        >>> parent("/bin/foo", none=False)
        PosixPath('/bin')
        >>> parent("/bin/foo")

    Args:
        path: file or dir.
        none: return None if it is not a directory and does not exist (default: True)

    Returns:
        Path
    """
    return (
        path.parent
        if (path := pathlib.Path(path)).is_file()
        else path
        if path.is_dir()
        else None
        if none
        else path.parent
    )


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


def python_latest(start: str | int | None = None) -> semver.VersionInfo:
    """
    Python latest version avaialble

    Examples:
        >>> import platform
        >>> from huti.functions import python_latest
        >>>
        >>> v = platform.python_version()
        >>> if "rc" not in v:
        ...     assert python_latest(v).match(f">={v}")
        ...     assert python_latest(v.rpartition(".")[0]).match(f">={v}")
        ...     assert python_latest(sys.version_info.major).match(f">={v}")
        >>>
        >>> assert python_latest("3.12").minor == 12

    Args:
        start: version startswith match, i.e.: "3", "3.10", "3.10", 3 or None to use `PYTHON_VERSION`
          environment variable or :obj:``sys.version`` if not set (Default: None).

    Returns:
        Latest Python Version
    """
    if start is None:
        start = python_version()
    start = str(start)
    start = start.rpartition(".")[0] if len(start.split(".")) == 3 else start
    return sorted([i for i in python_versions() if str(i).startswith(start)])[-1]


def python_version() -> str:
    """
    Major and Minor Python Version from ``PYTHON_VERSION`` environment variable, or
     ``PYTHON_REQUIRES`` environment variable or :obj:`sys.version`

    Examples:
        >>> import os
        >>> import platform
        >>> from huti.functions import python_version
        >>>
        >>> v = python_version()
        >>> assert platform.python_version().startswith(v)
        >>> assert len(v.split(".")) == 2
        >>>
        >>> os.environ["PYTHON_VERSION"] = "3.10"
        >>> assert python_version() == "3.10"
        >>>
        >>> os.environ["PYTHON_VERSION"] = "3.12-dev"
        >>> assert python_version() == "3.12-dev"
        >>>
        >>> os.environ["PYTHON_VERSION"] = "3.12.0b4"
        >>> assert python_version() == "3.12"

    Returns:
        str
    """
    p = platform.python_version()
    ver = os.environ.get("PYTHON_VERSION", p) or os.environ.get("PYTHON_REQUIRES", p)
    if len(ver.split(".")) == 3:
        return ver.rpartition(".")[0]
    return ver


def python_versions() -> list[semver.VersionInfo, ...]:
    """
    Python versions avaialble

    Examples:
        >>> import platform
        >>> from huti.functions import python_versions
        >>>
        >>> v = platform.python_version()
        >>> if not "rc" in v:
        ...     assert v in python_versions()

    Returns:
        Tuple of Python Versions
    """
    rv = []
    for link in bs4.BeautifulSoup(requests.get(PYTHON_FTP, timeout=2).text, "html.parser").find_all("a"):
        if link := re.match(r"((3\.([7-9]|[1-9][0-9]))|4).*", link.get("href").rstrip("/")):
            rv.append(semver.VersionInfo.parse(link.string))
    return sorted(rv)


def request_x_api_key_json(url, key: str = "") -> dict[str, str] | None:
    """
    API request helper with API Key and returning json

    Examples:
        >>> from huti.functions import request_x_api_key_json
        >>>
        >>> request_x_api_key_json("https://api.iplocation.net/?ip=8.8.8.8", \
                "rn5ya4fp/tzI/mENxaAvxcMo8GMqmg7eMnCvUFLIV/s=")
        {'ip': '8.8.8.8', 'ip_number': '134744072', 'ip_version': 4, 'country_name': 'United States of America',\
 'country_code2': 'US', 'isp': 'Google LLC', 'response_code': '200', 'response_message': 'OK'}

    Args:
        url: API url
        key: API Key

    Returns:
        response json
    """
    headers = {"headers": {"X-Api-Key": key}} if key else {}
    response = requests.get(url, **headers, timeout=2)
    if response.status_code == requests.codes.ok:
        return response.json()


def sourcepath(data: Any) -> Path:
    """
    Get path of object.

    Examples:
        >>> import asyncio
        >>> import huti.__init__
        >>> from huti.functions import sourcepath
        >>>
        >>> finfo = inspect.stack()[0]
        >>> globs_locs = (finfo.frame.f_globals | finfo.frame.f_locals).copy()
        >>> assert sourcepath(sourcepath) == Path(__file__)
        >>> assert sourcepath(asyncio.__file__) == Path(asyncio.__file__)
        >>> assert sourcepath(dict(a=1)) == Path("{'a': 1}")

    Returns:
        Path.
    """
    if isinstance(data, MutableMapping):
        f = data.get("__file__")
    elif isinstance(data, inspect.FrameInfo):
        f = data.filename
    else:
        try:
            f = inspect.getsourcefile(data) or inspect.getfile(data)
        except TypeError:
            f = None
    return Path(f or str(data))


def split_pairs(text):
    """
    Split text in pairs for even length

    Examples:
        >>> from huti.functions import split_pairs
        >>>
        >>> split_pairs("123456")
        [('1', '2'), ('3', '4'), ('5', '6')]

    Args:
        text:

    Returns:

    """
    return list(zip(text[0::2], text[1::2]))


def stdout(shell: AnyStr, keepends: bool = False, split: bool = False) -> list[str] | str | None:
    """Return stdout of executing cmd in a shell or None if error.

    Execute the string 'cmd' in a shell with 'subprocess.getstatusoutput' and
    return a stdout if success. The locale encoding is used
    to decode the output and process newlines.

    A trailing newline is stripped from the output.

    Examples:
        >>> from huti.functions import stdout
        >>>
        >>> stdout("ls /bin/ls")
        '/bin/ls'
        >>> stdout("true")
        ''
        >>> stdout("ls foo")
        >>> stdout("ls /bin/ls", split=True)
        ['/bin/ls']

    Args:
        shell: command to be executed
        keepends: line breaks when ``split`` if true, are not included in the resulting list unless keepends
            is given and true.
        split: return a list of the stdout lines in the string, breaking at line boundaries.(default: False)

    Returns:
        Stdout or None if error.
    """

    exitcode, data = subprocess.getstatusoutput(shell)

    if exitcode == 0:
        if split:
            return data.splitlines(keepends=keepends)
        return data
    return None


@contextlib.contextmanager
def stdquiet() -> tuple[TextIO, TextIO]:
    """
    Redirect stdout/stderr to StringIO objects to prevent console output from
    distutils commands.

    Returns:
        Stdout, Stderr
    """

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    new_stdout = sys.stdout = io.StringIO()
    new_stderr = sys.stderr = io.StringIO()
    try:
        yield new_stdout, new_stderr
    finally:
        new_stdout.seek(0)
        new_stderr.seek(0)
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def strip(obj: str | Iterable[str], ansi: bool = False, new: bool = True) -> str | Iterable[str]:
    """
    Strips ``\n`` And/Or Ansi from string or Iterable.

    Args:
        obj: object or None for redirect stdout
        ansi: ansi (default: False)
        new: newline (default: True)

    Returns:
        Same type with NEWLINE removed.
    """

    def rv(x):
        if isinstance(x, str):
            x = x.removesuffix("\n") if new else x
            x = strip_ansi.strip_ansi(x) if ansi else x
        if isinstance(x, bytes):
            x = x.removesuffix(b"\n") if new else x
        return x

    cls = type(obj)
    if isinstance(obj, str):
        return rv(obj)
    return cls(rv(i) for i in obj)


def superproject(path: pathlib.Path | str = "") -> pathlib.Path | None:
    """
    Show the absolute resolved path of the root of the superproject's working tree (if exists) that uses the current
    repository as its submodule (--show-superproject-working-tree) or show the absolute path of the
    top-level directory of the working tree (--show-toplevel).

    Exmples:
        >>> import os
        >>> import pathlib
        >>> import huti
        >>> from huti.classes import TempDir
        >>> from huti.functions import chdir
        >>> from huti.functions import superproject
        >>> from huti.functions import supertop
        >>> from huti.functions import command
        >>>
        >>> supertop(huti.__file__)  # doctest: +ELLIPSIS
        PosixPath('.../huti')
        >>>
        >>> with TempDir() as tmp:
        ...     if "site-packages" not in __file__:
        ...         assert superproject() == pathlib.Path(huti.__file__).parent.parent.parent
        ...     assert superproject(tmp) is None
        ...     rv = command("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert superproject(tmp) == tmp.resolve()
        ...     assert superproject(tmp / "README") == tmp.resolve()
        ...     rv = command("git", "submodule", "add", "https://github.com/octocat/Hello-World.git", cwd=tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / ".git").exists()
        ...     assert (tmp / ".git").is_dir()
        ...     with chdir(tmp):
        ...         assert superproject() == tmp.resolve()
        ...     with chdir(tmp /"Hello-World"):
        ...         assert superproject() == tmp.resolve()
        ...         assert superproject(tmp / "Hello-World/README") == tmp.resolve()

    Args:
        path: path inside working tree

    Returns:
        top repository absolute resolved path
    """
    c = f"git -C {parent(path, none=False)} rev-parse --show-superproject-working-tree --show-toplevel"
    if output := stdout(c, split=True):
        return pathlib.Path(output[0])


supertop = superproject


def suppress(func: Callable[P, T], *args: P.args, exception: ExcType | None = Exception, **kwargs: P.kwargs) -> T:
    """
    Try and supress exception.

    Args:
        func: function to call
        *args: args to pass to func
        exception: exception to suppress (default: Exception)
        **kwargs: kwargs to pass to func

    Returns:
        result of func
    """
    with contextlib.suppress(exception or Exception):
        return func(*args, **kwargs)


def syssudo(user: str = "root") -> subprocess.CompletedProcess | None:
    """
    Rerun Program with sudo ``sys.executable`` and ``sys.argv`` if user is different that the current user

    Arguments:
        user: run as user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, sys.executable, *sys.argv])
    return None


def tag_latest(path: AnyPath = None) -> str:
    """
    latest tag

    Examples:
        >>> import huti
        >>> from huti.functions import tag_latest
        >>> from huti.functions import top
        >>> t = top(huti)
        >>> if t.top:
        ...    assert tag_latest(huti.__file__) != ""

    """
    c = f"-C {parent(path)}" if path else ""
    return stdout(f"git {c} describe --abbrev=0 --tags") or ""


def tardir(src: Path | str) -> Path:
    """
    Compress directory src to <basename src>.tar.gz in cwd

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.functions import tardir
        >>> cwd = Path.cwd()
        >>> with TempDir() as workdir:
        ...     os.chdir(workdir)
        ...     with TempDir() as compress:
        ...         file = compress / "test.txt"
        ...         file.touch()  # doctest: +ELLIPSIS
        ...         compressed = tardir(compress)
        ...         with TempDir() as uncompress:
        ...             uncompressed = gz(compressed, uncompress)
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: directory to compress

    Raises:
        FileNotFoundError: No such file or directory
        ValueError: Can't compress current working directory

    Returns:
        Compressed Absolute File Path
    """
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(f"{src}: No such file or directory")

    if src.resolve() == Path.cwd().resolve():
        raise ValueError("Can't compress current working directory")

    name = Path(src).name + ".tar.gz"
    dest = Path(name)
    with tarfile.open(dest, "w:gz") as tar:
        for root, _, files in os.walk(src):
            for file_name in files:
                tar.add(os.path.join(root, file_name))
        return dest.absolute()


def tilde(path: str | Path = ".") -> str:
    """
    Replaces $HOME with ~

    Examples:
        >>> from huti.functions import tilde
        >>> assert tilde(f"{Path.home()}/file") == f"~/file"

    Arguments
        path: path to replace (default: '.')

    Returns:
        str
    """
    return str(path).replace(str(Path.home()), "~")


def timestamp_now(file: Path | str):
    """set modified and create date of file to now"""
    now = time.time()
    os.utime(file, (now, now))


def toiter(obj: Any, always: bool = False, split: str = " ") -> Any:
    """
    To iter.

    Examples:
        >>> import pathlib
        >>> from huti.functions import toiter
        >>>
        >>> assert toiter('test1') == ['test1']
        >>> assert toiter('test1 test2') == ['test1', 'test2']
        >>> assert toiter({'a': 1}) == {'a': 1}
        >>> assert toiter({'a': 1}, always=True) == [{'a': 1}]
        >>> assert toiter('test1.test2') == ['test1.test2']
        >>> assert toiter('test1.test2', split='.') == ['test1', 'test2']
        >>> assert toiter(pathlib.Path("/tmp/foo")) == ('/', 'tmp', 'foo')

    Args:
        obj: obj.
        always: return any iterable into a list.
        split: split for str.

    Returns:
        Iterable.
    """
    if isinstance(obj, str):
        obj = obj.split(split)
    elif hasattr(obj, "parts"):
        obj = obj.parts
    elif not isinstance(obj, Iterable) or always:
        obj = [obj]
    return obj


def to_latin9(chars: str) -> str:
    """
    Converts string to latin9 hex

    Examples:
        >>> from huti.constants import JOSE
        >>> from huti.functions import to_latin9
        >>>
        >>> to_latin9("ñ")
        'f1'
        >>>
        >>> to_latin9(JOSE)
        '4a6f73e920416e746f6e696f205075e972746f6c6173204d6f6e7461f1e973'

    Args:
        chars:

    Returns:
        hex str
    """
    rv = ""
    for char in chars:
        rv += char.encode("latin9").hex()
    return rv


def tomodules(obj: Any, suffix: bool = True) -> str:
    """
    Converts Iterable to A.B.C

    >>> from huti.functions import tomodules
    >>> assert tomodules('a b c') == 'a.b.c'
    >>> assert tomodules('a b c.py') == 'a.b.c'
    >>> assert tomodules('a/b/c.py') == 'a.b.c'
    >>> assert tomodules(['a', 'b', 'c.py']) == 'a.b.c'
    >>> assert tomodules('a/b/c.py', suffix=False) == 'a.b.c.py'
    >>> assert tomodules(['a', 'b', 'c.py'], suffix=False) == 'a.b.c.py'

    Args:
        obj: iterable.
        suffix: remove suffix.

    Returns:
        String A.B.C
    """
    split = "/" if isinstance(obj, str) and "/" in obj else " "
    return ".".join(i.removesuffix(Path(i).suffix if suffix else "") for i in toiter(obj, split=split))


def top(data: types.ModuleType | StrOrBytesPath | None = None) -> Top:
    """
    Get Top Level Package/Module Path.

    Examples:
        >>> import email.mime.application
        >>> from pathlib import Path
        >>> import pytest_cov
        >>> import semantic_release.cli.commands
        >>> import huti
        >>> import huti.cli
        >>> from huti.enums import PathSuffix, FileName
        >>> from huti.functions import chdir, findup, parent, top
        >>>
        >>> with chdir(huti.__file__):
        ...     t_top = top()
        ...     assert "__init__.py" in str(t_top.init_py)
        ...     assert "huti" == t_top.name
        ...     assert "HUTI_" == t_top.prefix
        ...     assert "huti.pth" in str(t_top.pth_source)  # doctest: +SKIP
        ...     if t_top.installed:
        ...         assert "site-packages" in str(t_top.init_py)
        ...         assert "site-packages" in str(t_top.path)
        ...         assert "site-packages" in str(t_top.pth_source)
        ...         assert "site-packages" in str(t_top.root)
        ...     else:
        ...         assert t_top.pth is None
        ...         assert "huti/pyproject.toml" in str(t_top.pyproject_toml)
        ...         assert "huti/venv" in str(t_top.venv)
        >>>
        >>> t_module = top(huti)
        >>> with chdir(huti.cli.__file__):
        ...     t_cwd = top()
        >>> t_cli = top(pathlib.Path(huti.cli.__file__).parent)
        >>> assert t_module == t_cwd == t_cli
        >>>
        >>> t_semantic = top(semantic_release.cli)
        >>> t_semantic  # doctest: +ELLIPSIS
        Top(init_py=PosixPath('/.../site-packages/semantic_release/__init__.py'), \
installed=True, name='semantic_release', \
path=PosixPath('/.../site-packages/semantic_release'), \
prefix='SEMANTIC_RELEASE_', pth=None, pth_source=None, \
pyproject_toml=None, \
root=PosixPath('/.../site-packages/semantic_release'), \
top=..., \
venv=...)
        >>>
        >>> t_pytest_cov = top(pytest_cov)
        >>> t_pytest_cov  # doctest: +ELLIPSIS
        Top(init_py=PosixPath('.../site-packages/pytest_cov/__init__.py'), \
installed=True, name='pytest_cov', \
path=PosixPath('.../site-packages/pytest_cov'), \
prefix='PYTEST_COV_', \
pth=PosixPath('.../site-packages/pytest-cov.pth'), \
pth_source=None, \
pyproject_toml=None, root=PosixPath('.../site-packages/pytest_cov'), \
top=..., \
venv=...)

    Args:
        data: ModuleType, directory or file name (default: None). None for cwd.

    Raises:
        AttributeError: __file__ not found.
    """

    if isinstance(data, types.ModuleType):
        p = data.__file__
    elif isinstance(data, (str, pathlib.Path, pathlib.PurePath)):
        p = data
    else:
        p = os.getcwd()

    init_py = installed = path = pth_source = pyproject_toml = None

    start = parent(p)
    root = None
    t = None
    if start and (t := superproject(start)):
        root = pathlib.Path(t)
    v = root / venv.__name__ if root else None

    if start:
        while True:
            if (rv := start / FileName.INIT()).is_file():
                init_py, path = rv, start
            if (rv := start / FileName.PYPROJECT()).is_file():
                pyproject_toml = rv
            if any(
                [
                    start.name == "dist-packages",
                    start.name == "site-packages",
                    start.name == pathlib.Path(sys.executable).resolve().name,
                    (start / "pyvenv.cfg").is_file(),
                ]
            ):
                installed, root = True, start
                break
            finish = root.parent if root else None
            if (start := start.parent) == (finish or pathlib.Path("/")):
                break
    root = pyproject_toml.parent if root is None and pyproject_toml else path
    if pyproject_toml:
        name = toml.load(pyproject_toml)["project"]["name"]
    elif path:
        name = path.name
    else:
        name = data

    name_dash = name.replace("_", "-")

    pths = getpths()

    if path:
        pth_source = (
            pth_source
            if (
                    path
                    and (
                            ((pth_source := path / PathSuffix.PTH(name)).is_file())
                            or ((pth_source := path / PathSuffix.PTH(name.replace("_", "-"))).is_file())
                    )
            )
            else None
        )

    return Top(
        init_py=init_py,
        installed=installed,
        name=name,
        path=path,
        prefix=f"{name.upper()}_",
        pth=pths.get(name, pths.get(name_dash)),
        pth_source=pathlib.Path(pth_source) if pth_source else None,
        pyproject_toml=pyproject_toml,
        root=root,
        top=t,
        venv=v,
    )


def tox() -> bool:
    """running in tox"""
    return ".tox" in sysconfig.get_paths()["purelib"]


def version(data: types.ModuleType | pathlib.Path | str | None = None) -> str:
    """
    Package installed version

    Examples:
        >>> import IPython
        >>> import semver
        >>> import huti
        >>> from huti.functions import version
        >>>
        >>> if (ver := version(huti)) and "dev" not in ver:
        ...     assert semver.VersionInfo.parse(version(huti))
        >>> assert semver.VersionInfo.parse(version(IPython))  # __version__
        >>> assert version(semver) == version(semver.__file__) == version(pathlib.Path(semver.__file__).parent) \
            == version("semver")
        >>> assert semver.VersionInfo.parse(version(semver))

    Arguments:
        data: module to search for __version__ or use name, package name oir path.name (Default: `PROJECT`)

    Returns
        Installed version
    """
    if isinstance(data, types.ModuleType) and hasattr(data, "__version__"):
        return data.__version__

    t = top(data)
    if isinstance(data, str) and "/" not in data:
        name = data
    elif isinstance(data, types.ModuleType):
        name = data.__name__
    else:
        name = t.name

    if t.pyproject_toml:
        if (v := toml.load(t.pyproject_toml).get("project", {}).get("version")) is None and t.root:
            v = tag_latest(t.root)
        if t.name == name:
            return v

    if not name:
        raise InvalidArgument(f"name is required: {data=}")

    return suppress(importlib.metadata.version, name, exception=importlib.metadata.PackageNotFoundError)


def which(data="sudo", raises: bool = False) -> str:
    """
    Checks if cmd or path is executable or exported bash function.

    Examples:
        # FIXME: Ubuntu

        >>> from huti.functions import which
        >>> if which():
        ...    assert "sudo" in which()
        >>> assert which('/usr/local') == ''
        >>> assert which('/usr/bin/python3') == '/usr/bin/python3'
        >>> assert which('let') == 'let'
        >>> assert which('source') == 'source'
        >>> which("foo", raises=True) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        huti.exceptions.CommandNotFound: foo

    Attribute:
        data: command or path.
        raises: raise exception if command not found

    Raises:
        CommandNotFound:


    Returns:
        Cmd path or ""
    """
    rv = (
            shutil.which(data, mode=os.X_OK)
            or subprocess.run(f"command -v {data}", shell=True, text=True, capture_output=True).stdout.rstrip("\n")
            or ""
    )

    if raises and not rv:
        raise CommandNotFound(data)

    return rv
