import pytest

from huti.functions import superproject


# https://docs.pytest.org/en/stable/how-to/doctest.html#doctest
@pytest.fixture(autouse=True)
def add_root(doctest_namespace):
    doctest_namespace["ROOT"] = superproject(__file__)
