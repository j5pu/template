"""
Huti Classes Module
"""
__all__ = (
    "CalledProcessError",
    "Chain",
    "CmdError",
    "FileConfig",
    "GroupUser",
    "LetterCounter",
    "TempDir",
)

import collections
import pathlib
import signal
import string
import subprocess
import tempfile
from typing import AnyStr, Optional, Sequence

from huti.enums import ChainRV
from huti.typings import StrOrBytesPath


class CalledProcessError(subprocess.SubprocessError):
    """
    Patched :class:`subprocess.CalledProcessError`.

    Raised when run() and the process returns a non-zero exit status.

    Attributes:
        cmd: The command that was run.
        returncode: The exit code of the process.
        output: The output of the process.
        stderr: The error output of the process.
        completed: :class:`subprocess.CompletedProcess` object.
    """
    returncode: int
    cmd: StrOrBytesPath | Sequence[StrOrBytesPath]
    output: AnyStr | None
    stderr: AnyStr | None
    completed: subprocess.CompletedProcess | None

    def __init__(self, returncode: int | None = None,
                 cmd: StrOrBytesPath | Sequence[StrOrBytesPath] | None = None,
                 output: AnyStr | None = None, stderr: AnyStr | None = None,
                 completed: Optional[subprocess.CompletedProcess] = None) -> None:
        """
        Patched :class:`subprocess.CalledProcessError`.

        Args:
            cmd: The command that was run.
            returncode: The exit code of the process.
            output: The output of the process.
            stderr: The error output of the process.
            completed: :class:`subprocess.CompletedProcess` object.

        Examples:
            >>> import subprocess
            >>> 3/0  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ZeroDivisionError: division by zero
            >>> subprocess.run(["ls", "foo"], capture_output=True, check=True)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            classes.CalledProcessError:
              Return Code:
                1
            <BLANKLINE>
              Command:
                ['ls', 'foo']
            <BLANKLINE>
              Stderr:
                b'ls: foo: No such file or directory\\n'
            <BLANKLINE>
              Stdout:
                b''
            <BLANKLINE>
        """
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr
        self.completed = completed
        if self.returncode is None:
            self.returncode = self.completed.returncode
            self.cmd = self.completed.args
            self.output = self.completed.stdout
            self.stderr = self.completed.stderr

    def _message(self):
        if self.returncode and self.returncode < 0:
            try:
                return f"Died with {signal.Signals(-self.returncode)!r}."
            except ValueError:
                return f"Died with with unknown signal {-self.returncode}."
        else:
            return f"{self.returncode:d}"

    def __str__(self):
        return f"""
  Return Code:
    {self._message()}

  Command:
    {self.cmd}

  Stderr:
    {self.stderr}

  Stdout:
    {self.output}
"""

    @property
    def stdout(self) -> str:
        """Alias for output attribute, to match stderr"""
        return self.output

    @stdout.setter
    def stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout is a transparent alias for .output
        self.output = value


class Chain(collections.ChainMap):
    # noinspection PyUnresolvedReferences
    """
    Variant of chain that allows direct updates to inner scopes and returns more than one value,
    not the first one.

    Examples:
        >>> from huti import Chain, ChainRV
        >>>
        >>> class Test3:
        ...     a = 2
        >>>
        >>> class Test4:
        ...     a = 2
        >>>
        >>> Test1 = collections.namedtuple('Test1', 'a b')
        >>> Test2 = collections.namedtuple('Test2', 'a d')
        >>> test1 = Test1(1, 2)
        >>> test2 = Test2(3, 5)
        >>> test3 = Test3()
        >>> test4 = Test4()
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2))]
        >>> chain = Chain(*maps)
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 2}]
        >>> chain = Chain(*maps, rv=ChainRV.FIRST)
        >>> assert chain['a'] == 1
        >>> chain = Chain(*maps, rv=ChainRV.ALL)
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 1}, {'z': 2}]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)),\
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps)
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 2}]
        >>> chain = Chain(*maps, rv=ChainRV.FIRST)
        >>> assert chain['a'] == 1
        >>> chain = Chain(*maps, rv=ChainRV.ALL)
        >>> assert chain['a'] == [1, 2, 3, {'z': 1}, {'z': 1}, {'z': 2}, 1, 3]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps)
        >>> del chain['a']
        >>> assert chain == Chain({'b': 2}, {'c': 3}, {'d': 4}, test1, test2)
        >>> assert chain['a'] == [1, 3]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps)
        >>> assert chain.delete('a') == Chain({'b': 2}, {'c': 3}, {'d': 4}, test1, test2)
        >>> assert chain.delete('a')['a'] == [1, 3]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps, rv=ChainRV.FIRST)
        >>> del chain['a']
        >>> del maps[0]['a'] # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError:
        >>>
        >>> assert chain['a'] == 2
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test2]
        >>> chain = Chain(*maps, rv=ChainRV.FIRST)
        >>> new = chain.delete('a')
        >>> del maps[0]['a'] # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError:
        >>> assert new.delete('a')
        >>> del maps[1]['a'] # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        KeyError:
        >>>
        >>> assert new['a'] == 3
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test3]
        >>> chain = Chain(*maps)
        >>> del chain['a']
        >>> assert chain[4] == []
        >>> assert not hasattr(test3, 'a')
        >>> assert chain.set('a', 9)
        >>> assert chain['a'] == [9, 1]
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test4]
        >>> chain = Chain(*maps)
        >>> chain.set('j', 9)  # doctest: +ELLIPSIS
        Chain({'a': 1, 'b': 2, 'j': 9}, {'a': 2, 'c': 3}, {'a': 3, 'd': 4}, {'a': {'z': 1}}, {'a': {'z': 1}}, \
{'a': {'z': 2}}, Test1(a=1, b=2), <....Test4 object at 0x...>)
        >>> assert [maps[0]['j']] == chain['j'] == [9]
        >>> chain.set('a', 10)  # doctest: +ELLIPSIS
        Chain({'a': 10, 'b': 2, 'j': 9}, {'a': 10, 'c': 3}, {'a': 10, 'd': 4}, {'a': 10}, {'a': 10}, {'a': 10}, \
Test1(a=1, b=2), <....Test4 object at 0x...>)
        >>> # noinspection PyUnresolvedReferences
        >>> assert [maps[0]['a'], 1] == chain['a'] == [maps[7].a, 1] == [10, 1]  # 1 from namedtuple
        >>>
        >>> maps = [dict(a=1, b=2), dict(a=2, c=3), dict(a=3, d=4), dict(a=dict(z=1)), dict(a=dict(z=1)), \
        dict(a=dict(z=2)), test1, test4]
        >>> chain = Chain(*maps, rv=ChainRV.FIRST)
        >>> chain.set('a', 9)  # doctest: +ELLIPSIS
        Chain({'a': 9, 'b': 2}, {'a': 2, 'c': 3}, {'a': 3, 'd': 4}, {'a': {'z': 1}}, {'a': {'z': 1}}, \
{'a': {'z': 2}}, Test1(a=1, b=2), <....Test4 object at 0x...>)
        >>> assert maps[0]['a'] == chain['a'] == 9
        >>> assert maps[1]['a'] == 2
        """
    rv = ChainRV.UNIQUE
    default = None
    maps = []  # noqa: RUF012

    def __init__(self, *maps, rv=ChainRV.UNIQUE, default=None):
        super().__init__(*maps)
        self.rv = rv
        self.default = default

    def __getitem__(self, key):
        rv = []
        for mapping in self.maps:
            if hasattr(mapping, "_field_defaults"):
                mapping = mapping._asdict()
            elif hasattr(mapping, 'asdict'):
                to_dict = mapping.__class__.asdict
                if isinstance(to_dict, property):
                    mapping = mapping.asdict
                elif callable(to_dict):
                    mapping = mapping.asdict()
            if hasattr(mapping, '__getitem__'):
                try:
                    value = mapping[key]
                    if self.rv is ChainRV.FIRST:
                        return value
                    if (self.rv is ChainRV.UNIQUE and value not in rv) or self.rv is ChainRV.ALL:
                        rv.append(value)
                except KeyError:
                    pass
            elif hasattr(mapping, '__getattribute__') and isinstance(key, str) and \
                    not isinstance(mapping, (tuple, bool, int, str, bytes)):
                try:
                    value = getattr(mapping, key)
                    if self.rv is ChainRV.FIRST:
                        return value
                    if (self.rv is ChainRV.UNIQUE and value not in rv) or self.rv is ChainRV.ALL:
                        rv.append(value)
                except AttributeError:
                    pass
        return self.default if self.rv is ChainRV.FIRST else rv

    def __delitem__(self, key):
        index = 0
        deleted = []
        found = False
        for mapping in self.maps:
            if mapping:
                if not isinstance(mapping, (tuple, bool, int, str, bytes)):
                    if hasattr(mapping, '__delitem__'):
                        if key in mapping:
                            del mapping[key]
                            if self.rv is ChainRV.FIRST:
                                found = True
                    elif hasattr(mapping, '__delattr__') and hasattr(mapping, key) and isinstance(key, str):
                        delattr(mapping.__class__, key) if key in dir(mapping.__class__) else delattr(mapping, key)
                        if self.rv is ChainRV.FIRST:
                            found = True
                if not mapping:
                    deleted.append(index)
                if found:
                    break
            index += 1
        for index in reversed(deleted):
            del self.maps[index]
        return self

    def delete(self, key):
        del self[key]
        return self

    def __setitem__(self, key, value):  # noq: C901
        found = False
        for mapping in self.maps:
            if mapping:
                if not isinstance(mapping, (tuple, bool, int, str, bytes)):
                    if hasattr(mapping, '__setitem__'):
                        if key in mapping:
                            mapping[key] = value
                            if self.rv is ChainRV.FIRST:
                                found = True
                    elif hasattr(mapping, '__setattr__') and hasattr(mapping, key) and isinstance(key, str):
                        setattr(mapping, key, value)
                        if self.rv is ChainRV.FIRST:
                            found = True
                if found:
                    break
        if not found and not isinstance(self.maps[0], (tuple, bool, int, str, bytes)):
            if hasattr(self.maps[0], '__setitem__'):
                self.maps[0][key] = value
            elif hasattr(self.maps[0], '__setattr__') and isinstance(key, str):
                setattr(self.maps[0], key, value)
        return self

    def set(self, key, value):
        return self.__setitem__(key, value)


class CmdError(subprocess.CalledProcessError):
    """
    Raised when run() and the process returns a non-zero exit status.

    Attribute:
      process: The CompletedProcess object returned by run().
    """

    def __init__(self, process=None):
        super().__init__(process.returncode, process.args, output=process.stdout, stderr=process.stderr)

    def __str__(self):
        value = super().__str__()
        if self.stderr is not None:
            value += "\n" + self.stderr
        if self.stdout is not None:
            value += "\n" + self.stdout
        return value


# noinspection PyTypeChecker
FileConfig = collections.namedtuple("FileConfig", ("file", "config"))

# noinspection PyTypeChecker
FrameSimple = collections.namedtuple('FrameSimple', 'back code frame function globals lineno locals name '
                                                    'package path vars')

# noinspection PyTypeChecker
GroupUser = collections.namedtuple('GroupUser', 'group user')


class LetterCounter:
    """
    Letter Counter generator function. This way, each time you call next() on the generator,

    it will yield the next counter value. We will also remove the maximum counter check


    Examples:
        >>> from huti.classes import LetterCounter
        >>>
        >>> c = LetterCounter("Z")
        >>> assert c.increment() == 'AA'

    """

    def __init__(self, start='A'):
        self.current_value = [string.ascii_uppercase.index(v) for v in start[::-1]]

    def increment(self):
        """
        Increments  1

        Exaamples:
            >>> from huti.classes import LetterCounter
            >>>
            >>> c = LetterCounter('BWDLQZZ')
            >>> assert c.increment() == 'BWDLRAA'
            >>> assert c.increment() == 'BWDLRAB'

        Returns:

        """
        for i in range(0, len(self.current_value)):
            # If digit is less than Z, increment and finish
            if self.current_value[i] < 25:
                self.current_value[i] += 1
                break
            # Otherwise, set digit to A (0) and continue to next digit
            else:
                self.current_value[i] = 0
                # If we've just set the most significant digit to A,
                # we need to add another 'A' at the most significant end
                if i == len(self.current_value) - 1:
                    self.current_value.append(0)
                    break
        # Form the string and return
        return ''.join(reversed([string.ascii_uppercase[i] for i in self.current_value]))


class TempDir(tempfile.TemporaryDirectory):
    """
    Wrapper for :class:`tempfile.TemporaryDirectory` that provides Path-like

    Examples:
        >>> from huti.classes import TempDir
        >>> from huti.variables import MACOS
        >>> with TempDir() as tmp:
        ...     if MACOS:
        ...         assert tmp.parts[1] == "var"
        ...         assert tmp.resolve().parts[1] == "private"
    """

    def __enter__(self):
        """
        Return the path of the temporary directory

        Returns:
            Path of the temporary directory
        """
        return pathlib.Path(self.name)


subprocess.CalledProcessError = CalledProcessError
