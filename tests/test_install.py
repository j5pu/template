import sysconfig
from pathlib import Path

import template

from pip._internal.cli.main import main as _main

ROOT = Path(__file__).parent.parent
PACKAGE = template.__name__


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    print(str(ROOT))
    rc = _main(["install", "-q", str(ROOT)])
    assert rc == 0


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    rc = _main(["uninstall", "-q", "-y", PACKAGE])
    assert rc == 0


def test_install() -> None:
    """Test that the package can be imported."""
    paths = sysconfig.get_paths()
    purelib = Path(paths["purelib"])
    scripts = Path(paths["scripts"])
    assert (purelib / f"{PACKAGE}.pth").is_file()
    assert (scripts / f"{PACKAGE}-script").is_file()
    assert (scripts / f"{PACKAGE}-script-1").is_file()
    assert (scripts / f"{PACKAGE}-test").is_file()
    assert (purelib / f"{PACKAGE}/data/Brewfile").is_file()
