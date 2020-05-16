# -*- encoding: utf-8 -*-

import importlib.machinery
import os
import sys

from pathlib import Path


def load_mobase(path: Path, moprivate: bool = False):
    """ Load the mobase from the given MO2 installation path and
    returns it.

    Args:
        path: Path to the MO2 installation (folder containg the ModOrganizer.exe).
        moprivate: If True, the moprivate module will also be loaded and returned
            alongisde mobase.

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

    mobase = importlib.machinery.ExtensionFileLoader(
        "mobase", path.joinpath("plugins", "data", "pythonrunner.dll").as_posix()
    ).load_module()

    if not moprivate:
        return mobase

    moprivate = importlib.machinery.ExtensionFileLoader(
        "moprivate", path.joinpath("plugins", "data", "pythonrunner.dll").as_posix()
    ).load_module()

    return mobase, moprivate


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        "Load mobase python module from MO2 installation directory"
    )
    parser.add_argument(
        "install_dir",
        metavar="INSTALL_DIR",
        type=Path,
        default=None,
        help="installation directory of Mod Organizer 2",
    )
    parser.add_argument(
        "-p", "--private", action="store_true", help="also load the moprivate module"
    )

    args = parser.parse_args()

    if args.private:
        mobase, moprivate = load_mobase(args.install_dir, moprivate=True)
    else:
        mobase = load_mobase(args.install_dir)
