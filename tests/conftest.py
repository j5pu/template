import pytest

from huti.env import Env
from huti.functions import superproject


# FIXME: are not found in docstrings
# https://docs.pytest.org/en/7.1.x/how-to/doctest.html#doctest-namespace-fixture
@pytest.fixture(autouse=True)
def add_root(doctest_namespace):
    env = Env()
    doctest_namespace["ENV"] = env
    doctest_namespace["CI"] = env.CI
    doctest_namespace["ROOT"] = superproject(__file__)
