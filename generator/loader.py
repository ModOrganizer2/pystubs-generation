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

    # Adding to PATH environment variable for python < 3.8 and
    # via os.add_dll_directory (python >= 3.8).
    # See: https://stackoverflow.com/a/58632354/2666289
    if sys.version_info < (3, 8):
        os.environ["PATH"] = os.pathsep.join(
            [str(path), str(path.joinpath("dlls")), os.environ.get("PATH", "")]
        )
    else:
        os.add_dll_directory(str(path))
        os.add_dll_directory(str(path.joinpath("dlls")))

    # We need to add plugins/data to sys.path, mainly for PyQt5
    sys.path.insert(1, path.joinpath("plugins", "data").as_posix())

    return importlib.machinery.ExtensionFileLoader(
        "mobase", path.joinpath("plugins", "data", "pythonrunner.dll").as_posix()
    ).load_module()  # type: ignore


if __name__ == "__main__":

    mobase = load_mobase(Path(sys.argv[1]))
