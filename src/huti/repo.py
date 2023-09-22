"""Repo Git Module"""
import subprocess
import tempfile
from dataclasses import InitVar, dataclass, field
from typing import Optional, Type
from urllib.parse import ParseResult

import git
from furl import furl
from git import Git as GitCmd
from git import GitCmdObjectDB, GitConfigParser
from gitdb import LooseObjectDB

from huti.constants import GIT_DEFAULT_SCHEME, GITHUB_DOMAIN
from huti.env import GIT
from huti.functions import aiocmd, cmd
from huti.path import AnyPath, Path
from huti.typings import GitScheme
from huti.variables import HUTI_PROJECT, HUTI_ROOT

__all__ = (
    "OwnerRepo",
    "Repo",
    "aioclone",
    "clone"
)


@dataclass
class OwnerRepo:
    """
    Owner Repo and Url Parser Class

    if scheme is "git+file" will only use repo argument as the path and must be absolute path

    furl:
        - url.query: after "?", i.e. ?ref=master&foo=bar
        - url.args: query args dict, i.e. {'ref': 'master', 'foo': 'bar'}
        - url.fragment: after "#", i.e. #two/directories?one=argument
        - url.fragment.path.segments: i.e. ['two', 'directories']
        - url.fragment.args: i.e. {'one': 'argument'}


    Examples:
        >>> import os
        >>> import pytest
        >>> from huti.repo import OwnerRepo
        >>>
        >>> OwnerRepo().url.url # doctest: +ELLIPSIS
        'https://github.com/.../huti'
        >>> OwnerRepo(repo="test").url.url # doctest: +ELLIPSIS
        'https://github.com/.../test'
        >>> str(OwnerRepo("cpython", "cpython").url)
        'https://github.com/cpython/cpython'

        # FIXME: 'git+file:%2Ftmp%2Fcpython.git'
        >>> str(OwnerRepo(repo="/tmp/cpython", scheme="git+file").url) # doctest: +SKIP
        'git+file:///tmp/cpython'
        >>> OwnerRepo("cpython", "cpython", scheme="git+https").url.url
        'git+https://github.com/cpython/cpython'
        >>> if not os.environ.get("CI"):
        ...     assert OwnerRepo("cpython", "cpython", scheme="git+ssh").url.url == \
                    'git+ssh://git@github.com/cpython/cpython'
        ...     assert OwnerRepo("cpython", "cpython", scheme="ssh").url.url == \
                    'ssh://git@github.com/cpython/cpython'


    :param owner: repo owner
    :param repo: repo name
    :param scheme: Git URL scheme
    :param url: furl instance of GitHub URL
    """
    owner: str = field(default=GIT)
    repo: str = field(default=HUTI_PROJECT)
    scheme: str = field(default=GIT_DEFAULT_SCHEME)
    url: furl | ParseResult | Path | str = field(default=None)

    def __post_init__(self):
        if self.url:
            self.url = furl(self.url if isinstance(self.url, (str, furl)) else
                            self.url.geturl() if isinstance(self.url, ParseResult) else
                            Repo(Path(self.url)).remote().url)
            self.scheme = self.url.scheme
            self.owner = self.url.path.segments[0]
            self.repo = self.url.path.segments[1].removesuffix(".git")
        else:
            args = {"scheme": self.scheme, "host": GITHUB_DOMAIN, "path": [self.owner, self.repo]}
            if self.scheme == "git+file":
                if not self.repo.startswith("/"):
                    raise ValueError(f"Repo must be an absolute file for '{self.scheme}': {self.repo}")
                args["path"] = [str(Path(self.repo).absolute().with_suffix(".git"))]
                del args["host"]
            elif "ssh" in self.scheme:
                args["username"] = "git"
            self.url = furl(**args)

    @classmethod
    def from_path(cls, path: Path) -> "OwnerRepo":
        """
        Parse a path into owner and repo
        """
        return cls(owner=path.parent.name, repo=path.name)


@dataclass
class Repo(git.Repo):
    """
    Dataclass Wrapper for :class:`git.Repo`.

    Represents a git repository and allows you to query references,
    gather commit information, generate diffs, create and clone repositories query
    the log.

    'working_tree_dir' is the working tree directory, but will raise AssertionError if we are a bare repository.
    """
    git: GitCmd = field(init=False)
    """
    The Repo class manages communication with the Git binary.

    It provides a convenient interface to calling the Git binary, such as in::

     g = Repo( git_dir )
     g.init()                   # calls 'git init' program
     rval = g.ls_files()        # calls 'git ls-files' program

    ``Debugging``
        Set the GIT_PYTHON_TRACE environment variable print each invocation
        of the command to stdout.
        Set its value to 'full' to see details about the returned values.

    """
    git_dir: AnyPath | None = field(default=None, init=False)
    """the .git repository directory, which is always set"""
    odb: Type[LooseObjectDB] = field(init=False)
    working_dir: AnyPath | None = field(default=None, init=False)
    """working directory of the git command, which is the working tree
    directory if available or the .git directory in case of bare repositories"""
    path: InitVar[AnyPath | None] = None
    """File or Directory inside the git repository, the default with search_parent_directories"""
    expand_vars: InitVar[bool] = True
    odbt: InitVar[Type[LooseObjectDB]] = GitCmdObjectDB
    """the path to either the root git directory or the bare git repo"""
    search_parent_directories: InitVar[bool] = True
    """if True, all parent directories will be searched for a valid repo as well."""

    def __post_init__(self, path: AnyPath | None, expand_vars: bool,
                      odbt: Type[LooseObjectDB], search_parent_directories: bool):
        """
        Create a new Repo instance

        Examples:
            >>> from huti.repo import Repo
            >>> assert Repo(__file__)
            >>> Repo("~/repo.git")  # doctest: +SKIP
            >>> Repo("${HOME}/repo")  # doctest: +SKIP

        Raises:
            InvalidGitRepositoryError
            NoSuchPathError

        Args:
            path: File or Directory inside the git repository, the default with search_parent_directories set to True
                or the path to either the root git directory or the bare git repo
                if search_parent_directories is changed to False
            expand_vars: if True, environment variables will be expanded in the given path
            search_parent_directories: Search all parent directories for a git repository.
        Returns:
            Repo: Repo instance
        """
        super().__init__(path if path is None else Path(path).to_parent(), expand_vars=expand_vars,
                         odbt=odbt, search_parent_directories=search_parent_directories)

    @classmethod
    def bare(cls, name: Optional[str] = None, repo: "Repo" = None) -> "Repo":
        """
        Create a bare repository in a temporary directory, to manage global/system config or as a remote for testing.

        Args:
            name: the path of the bare repository
            repo: Repo instance to update git config with remote url of the new bare repository (default: None)

        Returns:
            Repo: Repo instance
        """
        with tempfile.TemporaryDirectory(suffix=".git") as tmpdir:
            bare = cls.init(Path(tmpdir) / (f"{name}.git" if name else ""), bare=True)
            if repo:
                repo.config_writer().set_value("remote.origin.url", repo.git_dir).release()
            return bare

    @property
    def git_config(self) -> GitConfigParser:
        """
        Wrapper for :func:`git.Repo.config_reader`, so it is already read and can be used

        The configuration will include values from the system, user and repository
        configuration files.

        Examples:
            >>> conf = Repo(__file__).git_config
            >>> conf.has_section('remote "origin"')
            True
            >>> conf.has_option('remote "origin"', 'url')
            True
            >>> conf.get('remote "origin"', 'url')  # doctest: +ELLIPSIS
            'https://github.com/...'
            >>> conf.get_value('remote "origin"', 'url', "")  # doctest: +ELLIPSIS
            'https://github.com/...'

        Returns:
            GitConfigParser: GitConfigParser instance
        """
        config = self.config_reader()
        config.read()
        return config

    @property
    def origin_url(self) -> furl:
        """Git Origin URL."""

        return furl(next(iter(self.remote().urls)))

    @property
    def top(self) -> Path:
        """Repo Top Directory Path."""
        path = Path(self.working_dir)
        return Path(path.parent if ".git" in path else path)


async def aioclone(owner: str | None = None, repo: str = HUTI_ROOT, scheme: GitScheme = GIT_DEFAULT_SCHEME,
                   path: Path | str = None) -> subprocess.CompletedProcess:
    """
    Async Clone Repository

    Examples:
        >>> import asyncio
        >>> from huti.repo import aioclone
        >>> from huti.classes import TempDir
        >>>
        >>> with TempDir() as tmp:
        ...     directory = tmp / "1" / "2" / "3"
        ...     rv = asyncio.run(aioclone("octocat", "Hello-World", path=directory))
        ...     assert rv.returncode == 0
        ...     assert (directory / "README").exists()

    Args:
        owner: github owner, None to use GIT or USER environment variable if not defined (Default: `GIT`)
        repo: github repository (Default: `PROJECT`)
        scheme: url scheme (Default: "https")
        path: path to clone (Default: `repo`)

    Returns:
        CompletedProcess
    """
    path = path or Path.cwd() / repo
    path = Path(path)
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        return await aiocmd("git", "clone", OwnerRepo(owner, repo, scheme).url.url, path)


def clone(owner: str | None = None, repo: str = HUTI_ROOT, scheme: GitScheme = GIT_DEFAULT_SCHEME,
          path: Path | str = None) -> subprocess.CompletedProcess | None:
    """
    Clone Repository

    Examples:
        >>> import os
        >>> from huti.classes import TempDir
        >>> from huti.repo import clone
        >>>
        >>> with TempDir() as tmp:
        ...     directory = tmp / "1" / "2" / "3"
        >>> if not os.environ.get("CI"):
        ...     rv = clone("octocat", "Hello-World", "git+ssh", directory)
        ...     assert rv.returncode == 0
        ...     assert (directory / "README").exists()

    Args:
        owner: github owner, None to use GIT or USER environment variable if not defined (Default: `GIT`)
        repo: github repository (Default: `PROJECT`)
        scheme: url scheme (Default: "https")
        path: path to clone (Default: `repo`)

    Returns:
        CompletedProcess
    """
    path = path or Path.cwd() / repo
    path = Path(path)
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        return cmd("git", "clone", OwnerRepo(owner, repo, scheme).url.url, path)
    return None
