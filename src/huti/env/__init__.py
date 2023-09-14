# coding=utf-8
"""
shrc environment package
"""
from . import default
from . import env
from . import main
from . import misc
from . import osrelease
from . import secrets
from . import system

from .default import *
from .env import *
from .main import *
from .misc import *
from .osrelease import *
from .secrets import *
from .system import *

__all__ = \
    default.__all__ + \
    env.__all__ + \
    main.__all__ + \
    misc.__all__ + \
    osrelease.__all__ + \
    secrets.__all__ + \
    system.__all__

# TODO: parcheo esto con el python-decouple que lea antes el .env