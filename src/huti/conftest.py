from pathlib import Path

import pytest


@pytest.fixture()
def rootdir(request) -> Path:
    return Path(request.config.rootdir)


@pytest.fixture(autouse=True)
def namespace(doctest_namespace, request):
    doctest_namespace["rootdir"] = Path(request.config.rootdir)
