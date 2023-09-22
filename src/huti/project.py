"""Puntos Project Module"""
import subprocess
import sys
import sysconfig
from dataclasses import InitVar, dataclass, field
from types import SimpleNamespace
from typing import ClassVar

import setuptools.config
import toml
from packaging.specifiers import SpecifierSet

from huti.classes import FileConfig
from huti.constants import venv
from huti.functions import toiter
from huti.path import AnyPath, Path
from huti.variables import HUTI_ROOT

__all__ = (
    "EnvBuilder",
    "ProjectBase",
    "Project"
)


@dataclass
class EnvBuilder(venv.EnvBuilder):
    # noinspection PyUnresolvedReferences
    """
    Wrapper for :class:`venv.EnvBuilder`.

    Changed defaults for: `prompt`` `symlinks` and `with_pip`, adds `env_dir` to `__init__` arguments.

    This class exists to allow virtual environment creation to be
    customized. The constructor parameters determine the builder's
    behaviour when called upon to create a virtual environment.

    By default, the builder makes the system (global) site-packages dir
    *un*available to the created environment.

    If invoked using the Python -m option, the default is to use copying
    on Windows platforms but symlinks elsewhere. If instantiated some
    other way, the default is to *not* use symlinks (changed with the wrapper to use symlinks always).

    Args:
        system_site_packages: bool
            If True, the system (global) site-packages dir is available to created environments.
        clear: bool
            If True, delete the contents of the environment directory if it already exists, before environment creation.
        symlinks: bool
            If True, attempt to symlink rather than copy files into virtual environment.
        upgrade: bool
            If True, upgrade an existing virtual environment.
        with_pip: bool
            If True, ensure pip is installed in the virtual environment.
        prompt: str
            Alternative terminal prefix for the environment.
        upgrade_deps: bool
            Update the base venv modules to the latest on PyPI (python 3.9+).
        context: Simplenamespace
            The information for the environment creation request being processed.
        env_dir: bool
            The target directory to create an environment in.
        """
    system_site_packages: bool = False
    clear: bool = False
    symlinks: bool = True
    upgrade: bool = False
    with_pip: bool = True
    prompt: str | None = "."
    upgrade_deps: bool = False
    env_dir: Path | str | None = None
    context: SimpleNamespace | None = field(default=None, init=False)

    def __post_init__(self):
        # noinspection PyUnresolvedReferences
        """
        Initialize the environment builder and also creates the environment is does not exist.

        Args:
            system_site_packages: If True, the system (global) site-packages
                                     dir is available to created environments.
            clear: If True, delete the contents of the environment directory if
                      it already exists, before environment creation.
            symlinks: If True, attempt to symlink rather than copy files into
                         virtual environment.
            upgrade: If True, upgrade an existing virtual environment.
            with_pip: If True, ensure pip is installed in the virtual
                         environment.
            prompt: Alternative terminal prefix for the environment.
            env_dir: The target directory to create an environment in.
            upgrade_deps: Update the base venv modules to the latest on PyPI (python 3.9+).
        """
        super().__init__(system_site_packages=self.system_site_packages, clear=self.clear, symlinks=self.symlinks,
                         upgrade=self.upgrade, with_pip=self.with_pip, prompt=self.prompt,
                         **({"upgrade_deps": self.upgrade_deps} if sys.version_info >= (3, 9) else {}))
        if self.env_dir:
            self.env_dir = Path(self.env_dir)
            if self.env_dir.exists():
                self.ensure_directories()
            else:
                self.create(self.env_dir)

    def create(self, env_dir: Path | str | None = None) -> None:
        """
        Create a virtual environment in a directory.

        :param env_dir: The target directory to create an environment in.
        """
        if env_dir and self.env_dir is None:
            self.env_dir = env_dir
        super().create(self.env_dir)

    def ensure_directories(self, env_dir: Path | str | None = None) -> SimpleNamespace:
        """
        Create the directories for the environment.

        :param env_dir: The target directory to create an environment in.

        Returns:
            A context object which holds paths in the environment, for use by subsequent logic.
        """
        self.context = super().ensure_directories(env_dir or self.env_dir)
        return self.context

    def post_setup(self, context: SimpleNamespace | None = None) -> None:
        """
        Hook for post-setup modification of the venv. Subclasses may install
        additional packages or scripts here, add activation shell scripts, etc.

        :param context: The information for the environment creation request
                        being processed.
        """
        Project().pip_install()


@dataclass
class ProjectBase:
    """
    Project Base Class

    if name it will get the info from distribution instead of local project files
    """
    name: str = field(default=None, init=False)
    python_running_major_minor: str = field(default=None, init=False)
    """Python major.minor version running in the project"""
    python_exe_site: Path | None = field(default=None, init=False)
    """python site executable"""
    top: Path | None = field(default=None, init=False)
    """project git top level path"""

    data: InitVar[AnyPath] = None

    def __post_init__(self, data):
        self.python_running_major_minor = sysconfig.get_python_version()
        self.python_exe_site = Path(sys.executable).resolve()
        if data and toiter(data).len == 1:
            self.name = data
        if not data:
            top = subprocess.getoutput('git rev-parse --show-toplevel')
            if top:
                self.top = Path(top).resolve()

    @classmethod
    def from_name(cls, name: str = HUTI_ROOT) -> 'ProjectBase':
        """
        Create a ProjectBase instance from project name

        Args:
            name: project name

        Returns:
            ProjectBase: ProjectBase instance
        """
        return cls(name)


@dataclass
class Project(ProjectBase):
    """
    PyProject Class
    """
    extras_require: tuple[str, ...] = field(default_factory=tuple, init=False)
    """extras_requires from setup.cfg options"""
    install_requires: tuple[str, ...] = field(default_factory=tuple, init=False)
    """install_requires from setup.cfg options"""
    pypi_name: str = field(default="", init=False)
    """name from setup.cfg metadata"""
    py_packages: tuple[str, ...] = field(default_factory=tuple, init=False)
    """python packages from setup.cfg options"""
    pyproject_toml: FileConfig | None = field(default=None, init=False)
    """pyproject.toml"""
    python_exe_venv: Path | None = field(default=None, init=False)
    """python venv executable"""
    _python_requires: SpecifierSet = field(default=SpecifierSet, init=False)
    """python_requires from setup.cfg options"""
    requirements: tuple[str, ...] = field(default_factory=tuple, init=False)
    """all requirements: install_requires, extras_require and :data:`venv.CORE_VENV_DEPS`"""
    setup_cfg: FileConfig | None = field(default=None, init=False)
    """setup.cfg"""
    venv: EnvBuilder = field(default=None, init=False)
    """venv builder"""

    pip_install_options: ClassVar[tuple[str, ...]] = ("-m", "pip", "install", "--quiet", "--no-warn-script-location",)
    pip_upgrade_options: ClassVar[tuple[str, ...]] = (*pip_install_options, "--upgrade")

    def __post_init__(self, data):
        """
        Post Init
        """
        super().__post_init__(data)
        if self.top:
            file = self.top / 'pyproject.toml'
            if file.exists():
                self.pyproject_toml = FileConfig(file=file, config=toml.load(file))

            file = self.top / 'setup.cfg'
            if file.exists():
                self.setup_cfg = FileConfig(file=file, config=setuptools.config.read_configuration(file))

            if self.setup_cfg:
                metadata = self.setup_cfg.config.get("metadata", {})
                self.pypi_name = metadata.get('name', None)

                options = self.setup_cfg.config.get('options', {})
                self.extras_require = tuple(sorted({dep for extra in options.get('extras_require', {}).values()
                                                    for dep in extra}))
                self.install_requires = tuple(options.get('install_requires', []))
                self.py_packages = tuple(options.get('packages', []))
                self.python_requires = options.get('python_requires')
                self.requirements = tuple(sorted(self.install_requires + self.extras_require + venv.CORE_VENV_DEPS))

                self.venv = EnvBuilder(env_dir=self.top / venv.__name__)
                self.python_exe_venv = Path(self.venv.context.env_exec_cmd)

    def pip_install(self, *args: str, site: bool = False, upgrade: bool = False) -> None:
        """
        Install packages in venv

        Args:
            *args: packages to install (default: all requirements)
            site: install packages in site or venv (default: False)
            upgrade: upgrade packages (default: False)

        Returns:
            None
        """
        executable = self.python_exe_site if site else self.python_exe_venv
        subprocess.check_call([executable, *self.pip_upgrade_options, "pip", "wheel"])
        subprocess.check_call([executable, *(self.pip_upgrade_options if upgrade else self.pip_install_options),
                               *(args or self.requirements)])

    @property
    def python_requires(self) -> str:
        if len(self._python_requires) > 0:
            return next(iter(self._python_requires)).version
        return ""

    @python_requires.setter
    def python_requires(self, value: SpecifierSet | None) -> None:
        self._python_requires = value or SpecifierSet()
