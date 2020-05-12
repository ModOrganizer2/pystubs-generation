# -*- encoding: utf-8 -*-

import ctypes
import importlib.machinery
import os
import sys

from pathlib import Path


def load_dll(path: Path):
    """ Convenient wrapper for ctypes.cdll.LoadLibrary that can take a path
    object. """
    ctypes.cdll.LoadLibrary(str(path))


def load_mobase(path: Path):
    """ Load the mobase from the given MO2 installation path and
    returns it.

    Args:
        path: Path to the MO2 installation (folder containg the ModOrganizer.exe).

    Returns: The mobase module. """

    # We need absolute path for loading DLL and modules:
    path = path.resolve()

    os.environ["PATH"] = os.pathsep.join(
        [str(path), str(path.joinpath("dlls")), os.environ.get("PATH", "")]
    )

    # We need to load the dependencies manually for whatever reason... Adding them to
    # the PATH environment variable is not enough.

    # 1. The Qt DLLs (this is quite fast so I am not filtering the ones we do not
    # need):
    for dll in path.joinpath("dlls").iterdir():
        if dll.name.startswith("Qt5") and dll.name.endswith(".dll"):
            load_dll(dll)

    # 2. Python and boost python (needs to find the one matching):
    for dll in path.iterdir():
        if dll.name.endswith(".dll") and (
            dll.name.startswith("python") or dll.name.startswith("boost_python")
        ):
            load_dll(dll)

    # 3. uibase.dll
    load_dll(path.joinpath("uibase.dll"))

    # We need to add plugins/data to sys.path, mainly for PyQt5
    sys.path.insert(1, path.joinpath("plugins", "data").as_posix())

    return importlib.machinery.ExtensionFileLoader(
        "mobase", path.joinpath("plugins", "data", "pythonrunner.dll").as_posix()
    ).load_module()  # type: ignore


if __name__ == "__main__":

    mobase = load_mobase(Path(sys.argv[1]))
