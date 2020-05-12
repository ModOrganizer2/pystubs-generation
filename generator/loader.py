# -*- encoding: utf-8 -*-

import ctypes
import importlib.machinery
import os
import sys

from pathlib import Path

# List of DLLs dependencies required that are not in the dlls folder:
_DLLS = [
    "python38.dll",
    "boost_python38-vc142-mt-x64-1_73.dll",
    "uibase.dll",
]


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
    for dll in path.joinpath("dlls").iterdir():
        if dll.name.startswith("Qt5") and dll.name.endswith(".dll"):
            ctypes.cdll.LoadLibrary(str(dll))
    for extra_dll in _DLLS:
        ctypes.cdll.LoadLibrary(str(path.joinpath(extra_dll)))

    # We need to add plugins/data to sys.path, mainly for PyQt5
    sys.path.insert(1, path.joinpath("plugins", "data").as_posix())

    return importlib.machinery.ExtensionFileLoader(
        "mobase", path.joinpath("plugins", "data", "pythonrunner.dll").as_posix()
    ).load_module()  # type: ignore


if __name__ == "__main__":

    mobase = load_mobase(Path(sys.argv[1]))
