"""
Huti Constants Module
"""
__all__ = (
    "GIT_DEFAULT_SCHEME",
    "GITHUB_DOMAIN",
    "GITHUB_URL",
    "PYTHON_FTP",
    "venv"
)

import venv


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
PYTHON_FTP = "https://www.python.org/ftp/python"
"""Python FTP Server URL"""

venv.CORE_VENV_DEPS = ("build", "darglint", "icecream", "ipython", "pip", "pip-tools", "pytest", "pytest-asyncio",
                       "rich", "setuptools", "setuptools_scm", "tox", "wheel",)
