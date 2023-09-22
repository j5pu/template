__all__ = (
    "BuildWithPTH",
    "DevelopWithPTH",
    "EasyInstallWithPTH",
    "InstallLibWithPTH",
    "InstallPth",
)

import distutils.command.build
import itertools
from pathlib import Path

import setuptools.command.develop
import setuptools.command.easy_install
import setuptools.command.install
import setuptools.command.install_lib

from huti.functions import find_file

pth_file: Path | None | list[Path] = pth_file[0] if (pth_file := find_file("*.pth", Path.cwd() / "src")) else None


class BuildWithPTH(distutils.command.build.build):
    def run(self):
        super().run()
        print(f"BuildWithPTH: {pth_file}")
        if pth_file:
            self.copy_file(str(pth_file), str(Path(self.build_lib, pth_file.name)))


class DevelopWithPTH(setuptools.command.develop.develop):
    def run(self):
        super().run()
        print(f"DevelopWithPTH: {pth_file}")

        if pth_file:
            self.copy_file(str(pth_file), str(Path(self.install_dir, pth_file.name)))


class EasyInstallWithPTH(setuptools.command.easy_install.easy_install):
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        print(f"EasyInstallWithPTH: {pth_file}")
        if pth_file:
            self.copy_file(str(pth_file), str(Path(self.install_dir, pth_file.name)))


class InstallLibWithPTH(setuptools.command.install_lib.install_lib):
    def run(self):
        super().run()
        print(f"InstallLibWithPTH: {pth_file}")
        if pth_file:
            dest = str(Path(self.install_dir, pth_file.name))
            self.copy_file(str(pth_file), dest)
            self.outputs = [dest]

    def get_outputs(self):
        return itertools.chain(setuptools.command.install_lib.install_lib.get_outputs(self), self.outputs)


class InstallPth(setuptools.command.install.install):
    def run(self):
        super().run()
        print(f"InstallPth: {pth_file}")
        if pth_file:
            self.copy_file(str(pth_file), str(Path(self.install_lib, pth_file.name)))
