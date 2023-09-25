"""
Huti Constants Module
"""
__all__ = (
    "GIT_DEFAULT_SCHEME",
    "GITHUB_DOMAIN",
    "GITHUB_URL",
    "HUTI_DATA",
    "HUTI_DATA_TESTS",
    "JOSE",
    "PDF_REDUCE_THRESHOLD",
    "PYTHON_FTP",
    "SCAN_PREFIX",
)

from pathlib import Path

HUTI_DATA = Path(__file__).parent / "data"
HUTI_DATA_TESTS = HUTI_DATA / "tests"
JOSE = "José Antonio Puértolas Montañés"
PDF_REDUCE_THRESHOLD = 2000000
"""Reduce pdf for files bigger than 2MB"""
PYTHON_FTP = "https://www.python.org/ftp/python"
"""Python FTP Server URL"""
SCAN_PREFIX = "scanned_"
