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
    "venv"
)

import venv
from pathlib import Path

GIT_DEFAULT_SCHEME = "https"
GITHUB_DOMAIN = "github.com"
GITHUB_URL = {
    "api": f"https://api.{GITHUB_DOMAIN}/",
    "git+file": "git+file:///",
    "git+https": f"git+https://{GITHUB_DOMAIN}/",
    "git+ssh": f"git+ssh://git@{GITHUB_DOMAIN}/",
    "https": f"https://{GITHUB_DOMAIN}/",
    "ssh": f"git@{GITHUB_DOMAIN}:",
}
"""
GitHub: api, git+file, git+https, git+ssh, https, ssh and git URLs
(join directly the user or path without '/' or ':')
"""
HUTI_DATA = Path(__file__).parent / "data"
HUTI_DATA_TESTS = HUTI_DATA / "tests"
JOSE = "José Antonio Puértolas Montañés"
PDF_REDUCE_THRESHOLD = 2000000
"""Reduce pdf for files bigger than 2MB"""
PYTHON_FTP = "https://www.python.org/ftp/python"
"""Python FTP Server URL"""
SCAN_PREFIX = "scanned_"
venv.CORE_VENV_DEPS = ("build", "darglint", "icecream", "ipython", "pip", "pip-tools", "pytest", "pytest-asyncio",
                       "rich", "setuptools", "setuptools_scm", "tox", "wheel",)
