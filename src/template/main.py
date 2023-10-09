
def doctest_fixtures():
    """Return fixtures for doctests.

    Examples:
        >>> from pathlib import Path
        >>> import huti
        >>> root = Path(huti.__file__).parent.parent.parent
        >>> assert rootdir == root  # type: ignore[attr-defined]
        >>> assert getfixture("rootdir") == root  # type: ignore[attr-defined]
    """
