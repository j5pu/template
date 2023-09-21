""" Huti Path Module """
__all__ = (
    "Path",
    "Passwd",
    "PathStat",
    "AnyPath",
)

import collections
import contextlib
import grp
import hashlib
import os
import pathlib
import pwd
import stat
import subprocess
import sys
import tempfile
import tokenize
from dataclasses import InitVar, dataclass, field
from typing import TypeAlias, cast

from huti.enums import PathIs
from huti.functions import toiter, which
from huti.typings import AnyPath
from huti.variables import MACOS

_cache_passwd = {}
_cache_which = {}


class Path(pathlib.Path, pathlib.PurePosixPath):
    """Path helper class"""

    def __call__(self, name="", file=PathIs.IS_DIR, passwd=None, mode=None, effective_ids=False, follow_symlinks=False):
        """
        Make dir or touch file and create subdirectories as needed.

        Examples:
            >>> from huti.path import Path
            >>> from huti.enums import PathIs
            >>>
            >>> with Path.tempdir() as t:
            ...     p = t('1/2/3/4')
            ...     assert p.is_dir() is True
            ...     p = t('1/2/3/4/5/6/7.py', file=PathIs.IS_FILE)
            ...     assert p.is_file() is True
            ...     t('1/2/3/4/5/6/7.py/8/9.py', file=PathIs.IS_FILE) # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
            Traceback (most recent call last):
            NotADirectoryError: File: ...

        Args:
            name: path to add.
            file: file or directory.
            passwd: user.
            mode: mode.

        Returns:
            Path.
        """
        # noinspection PyArgumentList
        return (self.mkdir if file is PathIs.IS_DIR or file is PathIs.EXISTS else self.touch)(
            name=name, passwd=passwd, mode=mode, effective_ids=effective_ids, follow_symlinks=follow_symlinks,
        )

    def __contains__(self, value):
        """
        Checks all items in value exist in self.resolve().

        To check only parts use self.has.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert '/usr' in Path('/usr/local')
            >>> assert 'usr local' in Path('/usr/local')
            >>> assert 'home' not in Path('/usr/local')
            >>> assert '' not in Path('/usr/local')
            >>> assert '/' in Path()
            >>> assert os.environ["USER"] in Path.home()

        Args:
            value: space separated list of items to check, or iterable of items.

        Returns:
            bool
        """
        value = self.__class__(value) if isinstance(value, str) and "/" in value else toiter(value)
        return all(item in self.resolve().parts for item in value)

    def __eq__(self, other):
        """
        Equal based on parts

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert Path('/usr/local') == Path('/usr/local')
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return tuple(self.parts) == tuple(other.parts)

    def __hash__(self):
        return self._hash if hasattr(self, '_hash') else hash(tuple(self.parts))

    def __iter__(self):
        """
        Iterate over path parts.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert list(Path('/usr/local')) == ['/', 'usr', 'local',]

        Returns:
            Iterable of path parts.
        """
        return iter(self.parts)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts < other.parts

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts <= other.parts

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts > other.parts

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts >= other.parts

    def access(self, os_mode=os.W_OK, *, dir_fd=None, effective_ids=False, follow_symlinks=False):
        # noinspection LongLine
        """
        Checks if file or directory exists and has access (returns None if file/directory does not exist.

        Use the real uid/gid to test for access to a path `Real Effective IDs`_.

            -   real: user owns the completed.
            -   effective: user invoking.

        Examples:
            >>> import os
            >>> from huti.path import Path
            >>> from huti.variables import MACOS
            >>>
            >>> assert Path().access() is True
            >>> assert Path('/usr/bin').access() is False
            >>> assert Path('/tmp').access(follow_symlinks=True) is True
            >>> assert Path('/tmp').access(effective_ids=True, follow_symlinks=True) is True
            >>> if MACOS:
            ...     assert Path('/etc/bashrc').access(effective_ids=True) is False
            >>> if MACOS and not os.environ.get("CI"):
            ...     assert Path('/etc/sudoers').access(effective_ids=True, os_mode=os.R_OK) is False


        Args:
            os_mode: Operating-system mode bitfield. Can be F_OK to test existence,
                or the inclusive-OR of R_OK, W_OK, and X_OK (default: `os.W_OK`).
            dir_fd: If not None, it should be a file descriptor open to a directory,
                and path should be relative; path will then be relative to that
                directory.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).
            follow_symlinks: If False, and the last element of the path is a symbolic link,
                access will examine the symbolic link itself instead of the file
                the link points to (default: False).

        Note:
            Most operations will use the effective uid/gid (what the operating system
            looks at to make a decision whether you are allowed to do something), therefore this
            routine can be used in a suid/sgid environment to test if the invoking user
            has the specified access to the path.

            When a setuid program (`-rwsr-xr-x`) executes, the completed changes its Effective User ID (EUID)
            from the default RUID to the owner of this special binary executable file:
                -   euid: owner of executable (`os.geteuid()`).
                -   uid: user starting the completed (`os.getuid()`).

        Returns:
            True if access.

        .. _Real Effective IDs:
            https://stackoverflow.com/questions/32455684/difference-between-real-user-id-effective-user-id-and-saved-user-id
        """
        if not self.exists():
            return None
        return os.access(self, mode=os_mode, dir_fd=dir_fd, effective_ids=effective_ids,
                         follow_symlinks=follow_symlinks)

    def add(self, *args, exception=False):
        """
        Add args to self.

        Examples:
            >>> from huti.path import Path
            >>> import huti
            >>>
            >>> p = Path().add('a/a')
            >>> assert Path() / 'a/a' == p
            >>> p = Path().add(*['a', 'a'])
            >>> assert Path() / 'a/a' == p
            >>> p = Path(huti.__file__)
            >>> p.add('a', exception=True)  # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
            Traceback (most recent call last):
            FileNotFoundError...

        Args:
            *args: parts to be added.
            exception: raise exception if self is not dir and parts can not be added (default: False).

        Raises:
            FileNotFoundError: if self is not dir and parts can not be added.

        Returns:
            Compose path.
        """
        # print(self.is_file())
        if exception and self.is_file() and args:
            raise FileNotFoundError(f'parts: {args}, can not be added since path is file or not directory: {self}')
        args = toiter(args)
        path = self
        for arg in args:
            path = path / arg
        return path

    def append_text(self, text, encoding=None, errors=None):
        """
        Open the file in text mode, append to it, and close the file (creates file if not file).

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempfile() as tmp:
            ...    _ = tmp.write_text('Hello')
            ...    assert 'Hello World!' in tmp.append_text(' World!')

        Args:
            text: text to add.
            encoding: encoding (default: None).
            errors: raise error if there is no file (default: None).

        Returns:
            File text with text appended.
        """
        if not isinstance(text, str):
            raise TypeError(f'data must be str, not {text.__class__.__name__}')
        with self.open(mode='a', encoding=encoding, errors=errors) as f:
            f.write(text)
        return self.read_text()

    @contextlib.contextmanager
    def cd(self):
        """
        Change dir context manager to self if dir or parent if file and exists

        Examples:
            >>> from huti.path import Path
            >>>
            >>> new = Path('/usr/local')
            >>> p = Path.cwd()
            >>> with new.cd() as prev:
            ...     assert new == Path.cwd()
            ...     assert prev == p
            >>> assert p == Path.cwd()

        Returns:
            Old Pwd Path.
        """
        oldpwd = self.cwd()
        try:
            self.chdir()
            yield oldpwd
        finally:
            oldpwd.chdir()

    def chdir(self):
        """
        Change to self if dir or file parent if file and file exists.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> new = Path(__file__).chdir()
            >>> assert new == Path(__file__).parent
            >>> assert Path.cwd() == new
            >>>
            >>> new = Path(__file__).parent
            >>> assert Path.cwd() == new
            >>>
            >>> Path("/tmp/foo").chdir()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Raises:
            FileNotFoundError: No such file or directory if path does not exist.

        Returns:
            Path with changed directory.
        """
        path = self.to_parent()
        os.chdir(path)
        return path

    def checksum(self, algorithm='sha256', block_size=65536):
        """
        Calculate the checksum of a file.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempfile() as tmp:
            ...    _ = tmp.write_text('Hello')
            ...    assert tmp.checksum() == '185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969'

        Args:
            algorithm: hash algorithm (default: 'sha256').
            block_size: block size (default: 65536).

        Returns:
            Checksum of file.
        """
        sha = hashlib.new(algorithm)
        with self.open('rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha.update(block)
        return sha.hexdigest()

    def chmod(self, mode=None, effective_ids=False, exception=True, follow_symlinks=False, recursive=False):
        """
        Change mode of self.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempfile() as tmp:
            ...     changed = tmp.chmod(777)
            ...     assert changed.stat().st_mode & 0o777 == 0o777
            ...     assert changed.stats().mode == "-rwxrwxrwx"
            ...     assert changed.chmod("o-x").stats().mode == '-rwxrwxrw-'
            >>>
            >>> Path("/tmp/foo").chmod()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Raises:
            FileNotFoundError: No such file or directory if path does not exist and exception is True.

        Args:
            mode: mode to change to (default: None).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: resolve self if self is symlink (default: True).
            exception: raise exception if self does not exist (default: True).
            recursive: change owner of self and all subdirectories (default: False).

        Returns:
            Path with changed mode.
        """
        if exception and not self.exists():
            raise FileNotFoundError(f'path does not exist: {self}')

        subprocess.run([
            *self.sudo(force=True, effective_ids=effective_ids, follow_symlinks=follow_symlinks),
            f'{self.chmod.__name__}',
            *(["-R"] if recursive and self.is_dir() else []),
            str(mode or (755 if self.is_dir() else 644)),
            self.resolve() if follow_symlinks else self
        ], capture_output=True)

        return self

    def chown(self, passwd=None, effective_ids=False, exception=True, follow_symlinks=False, recursive=False):
        """
        Change owner of path

        Examples:
            >>> from huti.path import Path
            >>> from huti.path import Passwd
            >>> from huti.variables import MACOS
            >>>
            >>> with Path.tempfile() as tmp:
            ...     changed = tmp.chown(passwd=Passwd.from_root())
            ...     st = changed.stat()
            ...     assert st.st_gid == 0
            ...     assert st.st_uid == 0
            ...     stats = changed.stats()
            ...     assert stats.gid == 0
            ...     assert stats.uid == 0
            ...     assert stats.user == "root"
            ...     if MACOS:
            ...         assert stats.group == "wheel"
            ...         g = "admin"
            ...     else:
            ...         assert stats.group == "root"
            ...         g = "adm"
            ...     changed = tmp.chown(f"{os.getuid()}:{g}")
            ...     stats = changed.stats()
            ...     assert stats.group == g
            ...     assert stats.uid == os.getuid()
            >>>
            >>> Path("/tmp/foo").chown()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Raises:
            FileNotFoundError: No such file or directory if path does not exist and exception is True.
            ValueError: passwd must be string with user:group.

        Args:
            passwd: user/group passwd to use, or string with user:group (default: None).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            exception: raise exception if self does not exist (default: True).
            follow_symlinks: resolve self if self is symlink (default: True).
            recursive: change owner of self and all subdirectories (default: False).

        Returns:
            Path with changed owner.
        """
        if exception and not self.exists():
            raise FileNotFoundError(f'path does not exist: {self}')

        if isinstance(passwd, str) and ":" not in passwd:
            raise ValueError(f"passwd must be string with user:group, or 'Passwd' instance, got {passwd}")

        passwd = passwd or Passwd.from_login()

        subprocess.run([
            *self.sudo(force=True, effective_ids=effective_ids, follow_symlinks=follow_symlinks),
            f'{self.chown.__name__}',
            *(["-R"] if recursive and self.is_dir() else []),
            f'{passwd.user}:{passwd.group}' if isinstance(passwd, Passwd) else passwd,
            self.resolve() if follow_symlinks else self
        ], check=True, capture_output=True)

        return self

    def cmp(self, other):
        """
        Determine, whether two files provided to it are the same or not.
        By the same means that their contents are the same or not (excluding any metadata).
        Uses Cryptographic Hashes (using SHA256 - Secure hash algorithm 256) as a hash function.

        Examples:
            >>> from huti.path import Path
            >>> import huti
            >>> import asyncio
            >>>
            >>> assert Path(huti.__file__).cmp(huti.__file__) is True
            >>> assert Path(huti.__file__).cmp(asyncio.__file__) is False

        Args:
            other: other file to compare to

        Returns:
            True if equal.
        """
        return self.checksum() == self.__class__(other).checksum()

    def cp(self, dest, contents=False, effective_ids=False, follow_symlinks=False, preserve=False):
        """
        Wrapper for shell `cp` command to copy file recursivily and adding sudo if necessary.

        Examples:
            # FIXME: Ubuntu
            >>> from huti.path import Path
            >>> from huti.path import Passwd
            >>>
            >>> with Path.tempfile() as tmp:
            ...     changed = tmp.chown(passwd=Passwd.from_root())
            ...     copied = Path(__file__).cp(changed)
            ...     st = copied.stat()
            ...     assert st.st_gid == 0
            ...     assert st.st_uid == 0
            ...     stats = copied.stats()
            ...     assert stats.mode == "-rw-------"
            ...     _ = tmp.chown()
            ...     assert copied.cmp(__file__)

            >>> with Path.tempdir() as tmp:
            ...     _ = tmp.chmod("go+rx")
            ...     _ = tmp.chown(passwd=Passwd.from_root())
            ...     src = Path(__file__).parent
            ...     dirname = src.name
            ...     filename = Path(__file__).name
            ...
            ...     _ = src.cp(tmp)
            ...     destination = tmp / dirname
            ...     stats = destination.stats()
            ...     assert stats.mode == "drwxr-xr-x"
            ...     file = destination / filename
            ...     st = file.stat()
            ...     assert st.st_gid == 0
            ...     assert st.st_uid == 0
            ...     assert file.owner() == "root"
            ...     tmp = tmp.chown(recursive=True)
            ...     assert file.owner != "root"
            ...     assert file.cmp(__file__)
            ...
            ...     _ = src.cp(tmp, contents=True)
            ...     file = tmp / filename
            ...     assert (tmp / filename).cmp(__file__)
            >>>
            >>> Path("/tmp/foo").cp("/tmp/boo")  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Args:
            dest: destination.
            contents: copy contents of self to dest, `cp src/ dest` instead of `cp src dest` (default: False)`.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: '-P' the 'cp' default, no symlinks are followed,
                all symbolic links are followed when True '-L' (actual files are copyed but if there are existing links
                will be left them untouched) (default: False)
                `-H` cp option is not implemented (default: False).
            preserve: preserve file attributes (default: False).

        Raises:
            FileNotFoundError: No such file or directory if path does not exist.

        Returns:
            Dest.
        """
        dest = self.__class__(dest)

        if not self.exists():
            raise FileNotFoundError(f'path does not exist: {self}')

        subprocess.run([
            *dest.sudo(effective_ids=effective_ids, follow_symlinks=follow_symlinks),
            f'{self.cp.__name__}',
            *(["-R"] if self.is_dir() else []),
            *(["-L"] if follow_symlinks else []),
            *(["-p"] if preserve else []),
            f"{self!s}{'/' if contents else ''}", dest
        ], check=True, capture_output=True)

        return dest

    def exists(self) -> bool:
        """
        Check if file exists or is a broken link (super returns False if it is a broken link, we return True).

        Examples:
            >>> from huti.path import Path
            >>>
            >>> Path(__file__).exists()
            True
            >>> with Path.tempcd() as tmp:
            ...    source = tmp.touch("source")
            ...    destination = source.ln("destination")
            ...    assert destination.is_symlink()
            ...    source.unlink()
            ...    assert destination.exists()
            ...    assert not pathlib.Path(destination).exists()

        Returns:
            True if file exists or is broken link.
        """
        if super().exists():
            return True
        return self.is_symlink()

    @classmethod
    def expandvars(cls, path=None):
        """
        Return a Path instance from expanded environment variables in path.

        Expand shell variables of form $var and ${var}.
        Unknown variables are left unchanged.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> Path.expandvars('~/repo')  # doctest: +ELLIPSIS
            Path('~/repo')
            >>> Path.expandvars('${HOME}/repo')  # doctest: +ELLIPSIS
            Path('.../repo')

        Returns:
            Expanded Path.
        """
        return cls(os.path.expandvars(path) if path is not None else "")

    def file_in_parents(self, exception=True, follow_symlinks=False):
        """
        Find up until file with name is found.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempfile() as tmpfile:
            ...     new = tmpfile / "sub" / "file.py"
            ...     assert new.file_in_parents(exception=False) == tmpfile.absolute()
            >>>
            >>> with Path.tempdir() as tmpdir:
            ...    new = tmpdir / "sub" / "file.py"
            ...    assert new.file_in_parents() is None

        Args:
            exception: raise exception if a file is found in parents (default: False).
            follow_symlinks: resolve self if self is symlink (default: True).

        Raises:
            NotADirectoryError: ... No such file or directory: '/tmp/foo'

        Returns:
            File found in parents (str) or None
        """
        path = self.resolve() if follow_symlinks else self
        start = path
        while True:
            if path.is_file():
                if exception:
                    raise NotADirectoryError(f'File: {path} found in path: {start}')
                return path
            elif path.is_dir() or (
                    path := path.parent.resolve() if follow_symlinks else path.parent.absolute()
            ) == self.__class__('/'):
                return None

    def find_up(self, function=PathIs.IS_FILE, name='__init__.py', uppermost=False):
        """
        Find file or dir up.

        Examples:
            >>> import email.mime.application
            >>> import huti
            >>> import huti.env
            >>> from huti.path import Path
            >>>
            >>> assert 'huti/env/__init__.py' in Path(huti.env.__file__).find_up()
            >>> assert 'huti/__init__.py' in Path(huti.__file__).find_up(uppermost=True)


        Args:
            function: :class:`PIs` (default: PIs.IS_FILE)
            name: name (default: data.INIT_PY).
            uppermost: find uppermost (default: False).

        Returns:
            FindUp:
        """
        start = self.to_parent().absolute()
        latest = None
        found = None
        while True:
            find = start / name
            if getattr(find, function.value)():
                found = find
                if not uppermost:
                    return find
                latest = find
            start = start.parent
            if start == Path('/'):
                path = latest if getattr(latest, function.value)() else found
                return path

    def has(self, value):
        """
        Checks all items in value exist in `self.parts` (not absolute and not relative).

        Only checks parts and not resolved as checked by __contains__ or absolute.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert Path('/usr/local').has('/usr') is True
            >>> assert Path('/usr/local').has('usr local') is True
            >>> assert Path('/usr/local').has('home') is False
            >>> assert Path('/usr/local').has('') is False

        Args:
            value: space separated list of items to check, or iterable of items.

        Returns:
            bool
        """
        value = self.__class__(value) if isinstance(value, str) and "/" in value else toiter(value)
        return all(item in self.parts for item in value)

    def ln(self, dest, force=True):
        """
        Wrapper for super `symlink_to` to return the new path and changing the argument.

        If symbolic link already exists and have the same source, it will not be overwritten.

        Similar:

            - dest.symlink_to(src)
            - src.ln(dest) -> dest
            - os.symlink(src, dest)

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempcd() as tmp:
            ...     source = tmp.touch("source")
            ...     _ = source.ln("destination")
            ...     destination = source.ln("destination")
            ...     assert destination.is_symlink()
            ...     assert destination.resolve() == source.resolve()
            ...     assert destination.readlink().resolve() == source.resolve()
            ...
            ...     touch = tmp.touch("touch")
            ...     _ = tmp.ln("touch", force=False)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileExistsError:

        Raises:
            FileExistsError: if dest already exists or is a symbolic link with different source and force is False.

        Args:
           dest: link destination (ln -s self dest)
           force: force creation of link, if file or link exists and is different (default: True)
        """
        # TODO: relative symlinks https://gist.dreamtobe.cn/willprice/311faace6fb4f514376fa405d2220615
        dest = self.__class__(dest)
        if dest.is_symlink() and dest.readlink().resolve() == self.resolve():
            return dest
        if force and dest.exists():
            dest.rm()
        os.symlink(self, dest)
        return dest

    def mkdir(self, name="", passwd=None, mode=None, effective_ids=False, follow_symlinks=False):
        """
        Add directory, make directory, change mode and return new Path.

        Examples:
            >>> import getpass
            >>> from huti.path import Path
            >>> from huti.path import Passwd
            >>>
            >>> with Path.tempcd() as tmp:
            ...     directory = tmp('1/2/3/4')
            ...     assert directory.is_dir() is True
            ...     assert directory.owner() == getpass.getuser()
            ...
            ...     _ = directory.chown(passwd=Passwd.from_root())
            ...     assert directory.owner() == "root"
            ...     five = directory.mkdir("5")
            ...     assert five.text.endswith('/1/2/3/4/5') is True
            ...     assert five.owner() == "root"
            ...
            ...     six = directory("6")
            ...     assert six.owner() == "root"
            ...
            ...     seven = directory("7", passwd=Passwd())
            ...     assert seven.owner() == getpass.getuser()
            ...
            ...     _ = directory.chown(passwd=Passwd())

        Args:
            name: name.
            passwd: group/user for chown, if None ownership will not be changed (default: None).
            mode: mode.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).
            follow_symlinks: resolve self if self is symlink (default: True).

        Raises:
            NotADirectoryError: Directory can not be made because it's a file.

        Returns:
            Path:
        """
        path = (self / str(name)).resolve() if follow_symlinks else (self / str(name))
        if not path.is_dir() and path.file_in_parents(follow_symlinks=follow_symlinks) is None:
            subprocess.run([
                *path.sudo(effective_ids=effective_ids, follow_symlinks=follow_symlinks),
                f'{self.mkdir.__name__}',
                "-p",
                *(["-m", str(mode)] if mode else []),
                path
            ], capture_output=True)

            if passwd is not None:
                path.chown(passwd=passwd, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
        return path

    def mv(self, dest):
        """
        Move.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempdir() as tmp:
            ...     name = 'dir'
            ...     pth = tmp(name)
            ...     assert pth.is_dir()
            ...     _ = pth.mv(tmp('dir2'))
            ...     assert not pth.is_dir()
            ...     assert tmp('dir2').is_dir()
            ...     name = 'file'
            ...     pth = tmp(name, PathIs.IS_FILE)
            ...     assert pth.is_file()
            ...     _ = pth.mv(tmp('file2'))
            ...     assert not pth.is_file()

        Args:
            dest: destination.

        Returns:
            None.
        """
        subprocess.run([*self.__class__(dest).sudo(), f'{self.mv.__name__}', self, dest], check=True,
                       capture_output=True)
        return dest

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None, token=False):  # noqa: A003
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        if token:
            return tokenize.open(self.text) if self.is_file() else None
        return super().open(mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def privileges(self, effective_ids=False):
        """
        Return privileges of file.

        Args:
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).

        Returns:
            Privileges:
        """
        pass

    def realpath(self, exception=False):
        """
        Return the canonical path of the specified filename, eliminating any
        symbolic links encountered in the path.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert Path('/usr/local').realpath() == Path('/usr/local')

        Args:
            exception: raise exception if path does not exist (default: False).

        Returns:
            Path with real path.
        """
        return self.__class__(os.path.realpath(self, strict=not exception))

    def relative(self, path):
        """
        Return relative to path if is relative to path else None.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert Path('/usr/local').relative('/usr') == Path('local')
            >>> assert Path('/usr/local').relative('/usr/local') == Path('.')
            >>> assert Path('/usr/local').relative('/usr/local/bin') is None

        Args:
            path: path.

        Returns:
            Relative path or None.
        """
        p = Path(path).absolute()
        return self.relative_to(p) if self.absolute().is_relative_to(p) else None

    def rm(self, *args, effective_ids=False, follow_symlinks=False, missing_ok=True):
        """
        Delete a folder/file (even if the folder is not empty)

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempdir() as tmp:
            ...     name = 'dir'
            ...     pth = tmp(name)
            ...     assert pth.is_dir()
            ...     pth.rm()
            ...     assert not pth.is_dir()
            ...     name = 'file'
            ...     pth = tmp(name, PathIs.IS_FILE)
            ...     assert pth.is_file()
            ...     pth.rm()
            ...     assert not pth.is_file()
            ...     assert Path('/tmp/a/a/a/a')().is_dir()

        Raises:
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Args:
            *args: parts to add to self.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: True for resolved (default: False).
            missing_ok: missing_ok
        """
        if not missing_ok and not self.exists():
            raise FileNotFoundError(f'{self} does not exist')

        if (path := self.add(*args)).exists():
            subprocess.run([
                *path.sudo(force=True, effective_ids=effective_ids, follow_symlinks=follow_symlinks),
                f'{self.rm.__name__}',
                *(["-rf"] if self.is_dir() else []),
                path.resolve() if follow_symlinks else path,
            ], capture_output=True)

    def rm_empty(self, preserve=True):
        """
        Remove empty directories recursive

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempdir() as tmp:
            ...     first = tmp("1")
            ...
            ...     _ = tmp('1/2/3/4')
            ...     first.rm_empty()
            ...     assert first.exists() is True
            ...     assert Path("1").exists() is False
            ...
            ...     _ = tmp('1/2/3/4')
            ...     first.rm_empty(preserve=False)
            ...     assert first.exists() is False
            ...
            ...     _ = tmp('1/2/3/4/5/6/7.py', file=PathIs.IS_FILE)
            ...     first.rm_empty()
            ...     assert first.exists() is True

        Args:
            preserve: preserve top directory (default: True).

        """
        for directory, _, _ in os.walk(self, topdown=False):
            directory = self.__class__(directory).absolute()
            if len(list(directory.iterdir())) == 0 and (not preserve or (directory != self.absolute() and preserve)):
                os.rmdir(directory)

    def setid(self, name=None, uid=True, effective_ids=False, follow_symlinks=False):
        """
        Sets the set-user-ID-on-execution or set-group-ID-on-execution bits.

        Works if interpreter binary is setuid `u+s,+x` (-rwsr-xr-x), and:

           - executable script and setuid interpreter on shebang (#!/usr/bin/env setuid_interpreter).
           - setuid_interpreter -m module (venv would be created as root

        Works if interpreter binary is setuid `g+s,+x` (-rwxr-sr-x), and:

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempdir() as p:
            ...     a = p.touch('a')
            ...     _ = a.setid()
            ...     assert a.stats().suid is True
            ...     _ = a.setid(uid=False)
            ...     assert a.stats().sgid is True
            ...
            ...     a.rm()
            ...
            ...     _ = a.touch()
            ...     b = a.setid('b')
            ...     assert b.stats().suid is True
            ...     assert a.cmp(b) is True
            ...
            ...     _ = b.setid('b', uid=False)
            ...     assert b.stats().sgid is True
            ...
            ...     _ = a.write_text('a')
            ...     assert a.cmp(b) is False
            ...     b = a.setid('b')
            ...     assert b.stats().suid is True
            ...     assert a.cmp(b) is True

        Args:
            name: name to rename if provided.
            uid: True to set UID bit, False to set GID bit (default: True).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: True for resolved, False for absolute and None for relative
                or doesn't exist (default: True).

        Returns:
            Updated Path.
        """
        change = False
        chmod = f'{"u" if uid else "g"}+s,+x'
        mod = (stat.S_ISUID if uid else stat.S_ISGID) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        target = self.with_name(name) if name else self
        if name and (not target.exists() or not self.cmp(target)):
            self.cp(target, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
            change = True
        elif target.stats().result.st_mode & mod != mod:
            change = True
        if target.owner() != "root":
            change = True
        if change:
            # First: chown, second: chmod
            target.chown(passwd=Passwd.from_root(), follow_symlinks=follow_symlinks)
            target.chmod(mode=chmod, effective_ids=effective_ids, follow_symlinks=follow_symlinks, recursive=True)
        return target

    def setid_cp(self, name=None, uid=True, effective_ids=False, follow_symlinks=False):
        """
        Sets the set-user-ID-on-execution or set-group-ID-on-execution bits.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempdir() as p:
            ...     a = p.touch('a')
            ...     _ = a.setid()
            ...     assert a.stats().suid is True
            ...     _ = a.setid(uid=False)
            ...     assert a.stats().sgid is True
            ...
            ...     a.rm()
            ...
            ...     _ = a.touch()
            ...     b = a.setid('b')
            ...     assert b.stats().suid is True
            ...     assert a.cmp(b) is True
            ...
            ...     _ = b.setid('b', uid=False)
            ...     assert b.stats().sgid is True
            ...
            ...     _ = a.write_text('a')
            ...     assert a.cmp(b) is False
            ...     b = a.setid('b')
            ...     assert b.stats().suid is True
            ...     assert a.cmp(b) is True

        Args:
            name: name to rename if provided.
            uid: True to set UID bit, False to set GID bit (default: True).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: True for resolved, False for absolute and None for relative
                or doesn't exist (default: True).

        Returns:
            Updated Path.
        """
        change = False
        chmod = f'{"u" if uid else "g"}+s,+x'
        mod = (stat.S_ISUID if uid else stat.S_ISGID) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        target = self.with_name(name) if name else self
        if name and (not target.exists() or not self.cmp(target)):
            self.cp(target, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
            change = True
        elif target.stats().result.st_mode & mod != mod:
            change = True
        if target.owner() != "root":
            change = True
        if change:
            # First: chown, second: chmod
            target.chown(passwd=Passwd.from_root(), follow_symlinks=follow_symlinks)
            target.chmod(mode=chmod, effective_ids=effective_ids, follow_symlinks=follow_symlinks, recursive=True)
        return target

    @classmethod
    def setid_executable_cp(cls, name=None, uid=True):
        """
        Sets the set-user-ID-on-execution or set-group-ID-on-execution bits for sys.executable.

        Examples:
            >>> import shutil
            >>> import subprocess
            >>> from huti.path import Path
            >>>
            >>> f = Path.setid_executable_cp('setid_python_test')
            >>> assert subprocess.check_output([f, '-c', 'import os;print(os.geteuid())'], \
                    text=True) == '0\\n' # doctest: +SKIP
            >>> assert subprocess.check_output([f, '-c', 'import os;print(os.getuid())'], \
                    text=True) != '0\\n'  # doctest: +SKIP

            # >>> f.rm()
            # >>> assert f.exists() is False

        Args:
            name: name to rename if provided or False to add 'r' to original name (default: False).
            uid: True to set UID bit, False to set GID bit (default: True).

        Returns:
            Updated Path.
        """
        # FIXME: https://developer.apple.com/documentation/security/hardened_runtime
        #  https://gist.github.com/macshome/15f995a4e849acd75caf14f2e50e7e98

        path = cls(sys.executable)
        return path.setid_cp(name=name if name else f'r{path.name}', uid=uid)

    def stats(self, follow_symlinks=False):
        """
        Return the result of the stat() system call on this path, like
        os.stat() does with extra parsing for bits and root.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> rv = Path().stats()
            >>> assert all([rv.root, rv.sgid, rv.sticky, rv.suid]) is False
            >>>
            >>> with Path.tempfile() as file:
            ...     _ = file.chmod('u+s,+x')
            ...     assert file.stats().suid is True
            ...     _ = file.chmod('g+s,+x')
            ...     assert file.stats().sgid is True

        Args:
            follow_symlinks: If False, and the last element of the path is a symbolic link,
                stat will examine the symbolic link itself instead of the file
                the link points to (default: False).

        Returns:
            PathStat namedtuple :class:`ppath.PathStat`:
            gid: file GID
            group: file group name
            mode: file mode string formatted as '-rwxrwxrwx'
            own: user and group string formatted as 'user:group'
            passwd: instance of :class:`ppath:Passwd` for file owner
            result: result of `os.stat`
            root: is owned by root
            sgid: group executable and sticky bit (GID bit), members execute as the executable group (i.e.: crontab)
            sticky: sticky bit (directories), new files created in this directory will be owned by the directory's owner
            suid: user executable and sticky bit (UID bit), user execute and as the executable owner (i.e.: sudo)
            uid: file UID
            user: file owner name
        """
        mapping = {
            "sgid": stat.S_ISGID | stat.S_IXGRP,
            "suid": stat.S_ISUID | stat.S_IXUSR,
            "sticky": stat.S_ISVTX,
        }
        result = os.stat(self, follow_symlinks=follow_symlinks)
        passwd = Passwd(result.st_uid)
        return PathStat(
            gid=result.st_gid,
            group=grp.getgrgid(result.st_gid).gr_name,
            mode=stat.filemode(result.st_mode),
            own=f'{passwd.user}:{passwd.group}',
            passwd=passwd,
            result=result,
            root=result.st_uid == 0,
            uid=result.st_uid,
            user=passwd.user,
            **{i: result.st_mode & mapping[i] == mapping[i] for i in PathStat._fields if i in mapping}
        )

    def sudo(self, force=False, to_list=True, os_mode=os.W_OK, effective_ids=False, follow_symlinks=False):
        """
        Returns sudo command if path or ancestors exist and is not own by user and sudo command not installed.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> su = which()
            >>> assert Path('/tmp').sudo(to_list=False, follow_symlinks=True) == ''
            >>> assert "sudo" in Path('/usr/bin').sudo(to_list=False)
            >>> assert Path('/usr/bin/no_dir/no_file.text').sudo(to_list=False) == su
            >>> assert Path('no_dir/no_file.text').sudo(to_list=False) == ''
            >>> assert Path('/tmp').sudo(follow_symlinks=True) == []
            >>> assert Path('/usr/bin').sudo() == [su]

        Args:
            force: if sudo installed and user is ot root, return always sudo path
            to_list: return starred/list for command with no shell (default: True).
            os_mode: Operating-system mode bitfield. Can be F_OK to test existence,
                or the inclusive-OR of R_OK, W_OK, and X_OK (default: `os.W_OK`).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).
            follow_symlinks: If False, and the last element of the path is a symbolic link,
                access will examine the symbolic link itself instead of the file
                the link points to (default: False).
        Returns:
            `sudo` or ``, str or list.
        """
        if (rv := which()) and (os.geteuid if effective_ids else os.getuid)() != 0:
            path = self
            while path:
                if path.access(os_mode=os_mode, effective_ids=effective_ids, follow_symlinks=follow_symlinks):
                    if not force:
                        rv = ''
                    break
                elif path.exists() or str(path := (path.parent.resolve() if follow_symlinks else path.parent)) == "/":
                    break
        return ([rv] if rv else []) if to_list else rv

    @property
    def text(self) -> str:
        """
        Path as text.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert Path('/usr/local').text == '/usr/local'

        Returns:
            Path string.
        """
        return str(self)

    @classmethod
    @contextlib.contextmanager
    def tempcd(cls, suffix=None, prefix=None, directory=None):
        """
        Create temporaly directory, change to it and return it.

        This has the same behavior as mkdtemp but can be used as a context manager.

        Upon exiting the context, the directory and everything contained
        in it are removed.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> work = Path.cwd()
            >>> with Path.tempcd() as tmp:
            ...     assert tmp.exists() and tmp.is_dir()
            ...     assert Path.cwd() == tmp.resolve()
            >>> assert work == Path.cwd()
            >>> assert tmp.exists() is False

        Args:
            suffix: If 'suffix' is not None, the directory name will end with that suffix,
                otherwise there will be no suffix. For example, .../T/tmpy5tf_0suffix
            prefix: If 'prefix' is not None, the directory name will begin with that prefix,
                otherwise a default prefix is used.. For example, .../T/prefixtmpy5tf_0
            directory: If 'directory' is not None, the directory will be created in that directory (must exist,
                otherwise a default directory is used. For example, DIRECTORY/tmpy5tf_0

        Returns:
            Directory Path.
        """
        with cls.tempdir(suffix=suffix, prefix=prefix, directory=directory) as tmpdir, tmpdir.cd():
            try:
                yield tmpdir
            finally:
                pass

    @classmethod
    @contextlib.contextmanager
    def tempdir(cls, suffix=None, prefix=None, directory=None):
        """
        Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.

        Upon exiting the context, the directory and everything contained
        in it are removed.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> work = Path.cwd()
            >>> with Path.tempdir() as tmpdir:
            ...     assert tmpdir.exists() and tmpdir.is_dir()
            ...     assert Path.cwd() != tmpdir
            ...     assert work == Path.cwd()
            >>> assert tmpdir.exists() is False

        Args:
            suffix: If 'suffix' is not None, the directory name will end with that suffix,
                otherwise there will be no suffix. For example, .../T/tmpy5tf_0suffix
            prefix: If 'prefix' is not None, the directory name will begin with that prefix,
                otherwise a default prefix is used.. For example, .../T/prefixtmpy5tf_0
            directory: If 'directory' is not None, the directory will be created in that directory (must exist,
                otherwise a default directory is used. For example, DIRECTORY/tmpy5tf_0

        Returns:
            Directory Path.
        """
        with tempfile.TemporaryDirectory(suffix=suffix, prefix=prefix, dir=directory) as tmp:
            try:
                yield cls(tmp)
            finally:
                pass

    @classmethod
    @contextlib.contextmanager
    def tempfile(cls, mode="w", buffering=-1, encoding=None, newline=None, suffix=None, prefix=None, directory=None,
                 delete=True, *, errors=None):
        """
        Create and return a temporary file.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> with Path.tempfile() as tmpfile:
            ...    assert tmpfile.exists() and tmpfile.is_file()
            >>> assert tmpfile.exists() is False

        Args:
            mode: the mode argument to io.open (default "w+b").
            buffering:  the buffer size argument to io.open (default -1).
            encoding: the encoding argument to `io.open` (default None)
            newline: the newline argument to `io.open` (default None)
            delete: whether the file is deleted on close (default True).
            suffix: prefix for filename.
            prefix: prefix for filename.
            directory: directory.
            errors: the errors' argument to `io.open` (default None)

        Returns:
            An object with a file-like interface; the name of the file
            is accessible as its 'name' attribute.  The file will be automatically
            deleted when it is closed unless the 'delete' argument is set to False.
        """
        with tempfile.NamedTemporaryFile(mode=mode, buffering=buffering, encoding=encoding, newline=newline,
                                         suffix=suffix, prefix=prefix, dir=directory, delete=delete,
                                         errors=errors) as tmp:
            try:
                yield cls(tmp.name)
            finally:
                pass

    def to_parent(self):
        """
        Return Parent if is file and exists or self.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> assert Path(__file__).to_parent() == Path(__file__).parent

        Returns:
            Path of directory if is file or self.
        """
        return self.parent if self.is_file() else self

    def touch(self, name="", passwd=None, mode=None, effective_ids=False, follow_symlinks=False):
        """
        Add file, touch and return post_init Path.

        Parent paths are created.
7 años informatico 300 coicertos, 2 discos , horizontes,
        Examples:
            >>> from huti.path import Path
            >>> from huti.path import Passwd
            >>>
            >>> import getpass
            >>> with Path.tempcd() as tmp:
            ...     file = tmp('1/2/3/4/5/6/root.py', file=PathIs.IS_FILE, passwd=Passwd.from_root())
            ...     assert file.is_file() is True
            ...     assert file.parent.owner() == getpass.getuser()
            ...     assert file.owner() == "root"
            ...
            ...     new = file.parent("user.py", file=PathIs.IS_FILE)
            ...     assert new.owner() == getpass.getuser()
            ...
            ...     touch = file.parent.touch("touch.py")
            ...     assert touch.owner() == getpass.getuser()
            ...
            ...     last = (file.parent / "last.py").touch()
            ...     assert last.owner() == getpass.getuser()
            ...     assert last.is_file() is True
            ...
            ...     file.rm()

        Args:
            name: name.
            passwd: group/user for chown, if None ownership will not be changed (default: None).
            mode: mode.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: If False, I think is useless (default: False).

        Returns:
            Path.
        """
        path = self / str(name)
        path = path.resolve() if follow_symlinks else path.absolute()
        if not path.is_file() and not path.is_dir() \
                and path.parent.file_in_parents(follow_symlinks=follow_symlinks) is None:
            if not (d := path.parent).exists():
                d.mkdir(mode=mode, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
            subprocess.run([
                *path.sudo(effective_ids=effective_ids, follow_symlinks=follow_symlinks),
                f'{self.touch.__name__}',
                path
            ], capture_output=True, check=True)
            path.chmod(mode=mode, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
            if passwd is not None:
                path.chown(passwd=passwd, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
        return path

    def with_suffix(self, suffix=""):
        """
        Sets default for suffix to "", since :class:`pathlib.Path` does not have default.

        Return a new path with the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix is an empty
        string, remove the suffix from the path.

        Examples:
            >>> from huti.path import Path
            >>>
            >>> Path("/tmp/test.txt").with_suffix()
            Path('/tmp/test')

        Args:
            suffix: suffix (default: '')

        Returns:
            Path.
        """
        return super().with_suffix(suffix=suffix)


@dataclass
class Passwd:
    """
    Passwd class from either `uid` or `user`

    Args:
    ----
        uid: int
            User ID
        user: str
            Username

    Attributes:
    -----------
        gid: int
            Group ID
        gecos: str
            Full name
        group: str
            Group name
        groups: tuple(str)
            Groups list
        home: Path
            User's home
        shell: Path
            User shell
        uid: int
            User ID (default: :func:`os.getuid` current user id)
        user: str
            Username
    """
    data: InitVar[int | str] = None
    gid: int = field(default=None, init=False)
    gecos: str = field(default=None, init=False)
    group: str = field(default=None, init=False)
    groups: dict[str, int] = field(default=None, init=False)
    home: Path = field(default=None, init=False)
    shell: Path = field(default=None, init=False)
    uid: int = field(default=None, init=False)
    user: str = field(default=None, init=False)

    def __post_init__(self, data):
        """
        Instance of :class:`ppath:Passwd`  from either `uid` or `user` (default: :func:`os.getuid`)

        Uses completed/real id's (os.getgid, os.getuid) instead effective id's (os.geteuid, os.getegid) as default.
            - UID and GID: when login from $LOGNAME, $USER or os.getuid()
            - RUID and RGID: completed real user id and group id inherit from UID and GID
                (when completed start EUID and EGID and set to the same values as RUID and RGID)
            - EUID and EGID: if executable has 'setuid' or 'setgid' (i.e: ping, sudo), EUID and EGID are changed
                to the owner (setuid) or group (setgid) of the binary.
            - SUID and SGID: if executable has 'setuid' or 'setgid' (i.e: ping, sudo), SUID and SGID are saved with
                RUID and RGID to do unprivileged tasks by a privileged completed (had 'setuid' or 'setgid').
                Can not be accessed in macOS with `os.getresuid()` and `os.getresgid()`

        Examples:
            >>> import pathlib
            >>> from huti.variables import MACOS
            >>> from huti.path import Passwd
            >>> from huti.path import Path
            >>>
            >>> default = Passwd()
            >>> user = os.environ["USER"]
            >>> login = Passwd.from_login()
            >>>
            >>> assert default == Passwd(Path()) == Passwd(pathlib.Path())  == Passwd(user) == Passwd(os.getuid()) == \
                    login != Passwd().from_root()
            >>> assert default.gid == os.getgid()
            >>> assert default.home == Path(os.environ["HOME"])
            >>> if shell := os.environ.get("SHELL"):
            ...     assert default.shell == Path(shell)
            >>> assert default.uid == os.getuid()
            >>> assert default.user == user
            >>> if MACOS:
            ...    assert "staff" in default.groups
            ...    assert "admin" in default.groups

        Errors:
            os.setuid(0)
            os.seteuid(0)
            os.setreuid(0, 0)

        os.getuid()
        os.geteuid(
        os.setuid(uid) can only be used if running as root in macOS.
        os.seteuid(euid) -> 0
        os.setreuid(ruid, euid) -> sets EUID and RUID (probar con 501, 0)
        os.setpgid(os.getpid(), 0) -> sets PGID and RGID (probar con 501, 0)

        Returns:
            Instance of :class:`ppath:Passwd`
        """
        if (isinstance(data, str) and not data.isnumeric()) or isinstance(data, pathlib.PurePosixPath):
            passwd = pwd.getpwnam(cast(str, getattr(data, "owner", lambda: None)() or data))
        else:
            passwd = pwd.getpwuid(int(data) if data or data == 0 else os.getuid())

        self.gid = passwd.pw_gid
        self.gecos = passwd.pw_gecos
        self.home = Path(passwd.pw_dir)
        self.shell = Path(passwd.pw_shell)
        self.uid = passwd.pw_uid
        self.user = passwd.pw_name

        group = grp.getgrgid(self.gid)
        self.group = group.gr_name
        self.groups = {grp.getgrgid(gid).gr_name: gid for gid in os.getgrouplist(self.user, self.gid)}
        if self.uid not in _cache_passwd:
            _cache_passwd[self.uid] = _cache_passwd[self.user] = self

    @property
    def is_su(self) -> bool:
        """Returns True if login as root, uid=0 and not `SUDO_USER`"""
        return self.uid == 0 and not bool(os.environ.get("SUDO_USER"))

    @property
    def is_sudo(self) -> bool:
        """Returns True if SUDO_USER is set"""
        return bool(os.environ.get("SUDO_USER"))

    @property
    def is_user(self) -> bool:
        """Returns True if user and not `SUDO_USER`"""
        return self.uid != 0 and not bool(os.environ.get("SUDO_USER"))

    @classmethod
    def from_login(cls):
        """Returns instance of :class:`ppath:Passwd` from '/dev/console' on macOS and `os.getlogin()` on Linux"""
        try:
            user = Path('/dev/console').owner() if MACOS else os.getlogin()
        except OSError:
            user = Path('/proc/self/loginuid').owner()
        if user not in _cache_passwd:
            return cls(user)
        return _cache_passwd[user]

    @classmethod
    def from_sudo(cls):
        """Returns instance of :class:`ppath:Passwd` from `SUDO_USER` if set or current user"""
        uid = os.environ.get("SUDO_UID", os.getuid())
        if uid not in _cache_passwd:
            return cls(uid)
        return _cache_passwd[uid]

    @classmethod
    def from_root(cls):
        """Returns instance of :class:`ppath:Passwd` for root"""
        if 0 not in _cache_passwd:
            return cls(0)
        return _cache_passwd[0]


PathStat = collections.namedtuple('PathStat', 'gid group mode own passwd result root sgid sticky suid uid user')
PathStat.__doc__ = """
namedtuple for :func:`ppath.Path.stats`.

Args:
    gid: file GID
    group: file group name
    mode: file mode string formatted as '-rwxrwxrwx'
    own: user and group string formatted as 'user:group'
    passwd: instance of :class:`ppath:Passwd` for file owner
    result: result of os.stat
    root: is owned by root
    sgid: group executable and sticky bit (GID bit), members execute as the executable group (i.e.: crontab)
    sticky: sticky bit (directories), new files created in this directory will be owned by the directory's owner
    suid: user executable and sticky bit (UID bit), user execute and as the executable owner (i.e.: sudo)
    uid: file UID
    user: file user name
"""
AnyPath: TypeAlias = Path | AnyPath
