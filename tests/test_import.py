import huti


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(huti.__name__, str)
