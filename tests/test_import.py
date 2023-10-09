import template


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(template.__name__, str)
