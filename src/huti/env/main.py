"""
Huti environment package
"""
__all__ = (
    "parse",
    "environment",
)

import ipaddress
import os
import sys
import urllib.parse
from ipaddress import IPv4Address, IPv6Address
from pathlib import Path
from urllib.parse import ParseResult


def parse(variable: str = "USER") -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:

    """
    Parses variable from environment

    Parses:
        - bool: 1, 0, True, False, yes, no, on, off (case insensitive)
        - int: integer only numeric characters but 1 and 0 or SUDO_UID or SUDO_GID
        - ipaddress: ipv4/ipv6 address
        - url: if "//" or "@" is found it will be parsed as url
        - path: start with / or ~ or .
        - others as string

    Arguments:
        variable: variable name to parse from environment (default: USER)

    Examples:
        >>> assert isinstance(parse(), str)
        >>>
        >>> os.environ['FOO'] = '1'
        >>> assert parse("FOO") is True
        >>>
        >>> os.environ['FOO'] = '0'
        >>> assert parse("FOO") is False
        >>>
        >>> os.environ['FOO'] = 'TrUe'
        >>> assert parse("FOO") is True
        >>>
        >>> os.environ['FOO'] = 'OFF'
        >>> assert parse("FOO") is False
        >>>
        >>> os.environ['FOO'] = '~/foo'
        >>> assert parse("FOO") == Path('~/foo')
        >>>
        >>> os.environ['FOO'] = '/foo'
        >>> assert parse("FOO") == Path('/foo')
        >>>
        >>> os.environ['FOO'] = './foo'
        >>> assert parse("FOO") == Path('./foo')
        >>>
        >>> os.environ['FOO'] = './foo'
        >>> assert parse("FOO") == Path('./foo')
        >>>
        >>> v = "https://github.com"
        >>> os.environ['FOO'] = v
        >>> assert parse("FOO").geturl() == v
        >>>
        >>> v = "git@github.com"
        >>> os.environ['FOO'] = v
        >>> assert parse("FOO").geturl() == v
        >>>
        >>> v = "0.0.0.0"
        >>> os.environ['FOO'] = v
        >>> assert parse("FOO").exploded == v
        >>>
        >>> os.environ['FOO'] = "::1"
        >>> assert parse("FOO").exploded.endswith(":0001")
        >>>
        >>> v = "2"
        >>> os.environ['FOO'] = v
        >>> assert parse("FOO") == int(v)
        >>>
        >>> v = "2.0"
        >>> os.environ['FOO'] = v
        >>> assert parse("FOO") == v
        >>>
        >>> del os.environ['FOO']
        >>> assert parse("FOO") is None

    Returns:
        None
    """
    if value := os.environ.get(variable):
        if variable in ("SUDO_UID", "SUDO_GID"):
            return int(value)
        elif value.lower() in ['1', 'true', 'yes', 'on']:
            return True
        elif value.lower() in ['0', 'false', 'no', 'off']:
            return False
        elif value[0] in ['/', '~', '.'] and variable != "PATH":
            return Path(value)
        elif '://' in value or '@' in value:
            return urllib.parse.urlparse(value)
        else:
            try:
                return ipaddress.ip_address(value)
            except ValueError:
                if value.isnumeric():
                    return int(value)
    return value


def environment() -> None:
    """
    Parses all globals in :obj:`__all__` of the module imported from environment variables

    Parses:
        - bool: 1, 0, True, False, yes, no, on, off (case insensitive)
        - int: integer only numeric characters but 1 and 0 or SUDO_UID or SUDO_GID
        - ipaddress: ipv4/ipv6 address
        - url: if "//" or "@" is found it will be parsed as url
        - path: start with / or ~ or .
        - others as string

    Examples:
        >>> from huti.env.default import *
        >>> assert isinstance(USER, str)
        >>> assert isinstance(PWD, Path)

    Returns:
        None
    """
    data = sys._getframe(1).f_globals
    for variable in data["__all__"]:
        data[variable] = parse(variable)
