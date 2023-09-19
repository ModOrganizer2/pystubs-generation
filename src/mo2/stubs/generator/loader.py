import os
import sys
from modulefinder import Module
from pathlib import Path
from typing import Any


def load_mobase(path: os.PathLike[Any]) -> Module:
    """
    Load the mobase from the given MO2 installation path and
    returns it.

    Args:
        path: Path to the MO2 installation (folder containing the ModOrganizer.exe).

    Returns: The mobase module.
    """

    path = Path(path)

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
        os.add_dll_directory(str(path))  # type: ignore
        os.add_dll_directory(str(path.joinpath("dlls")))  # type: ignore

    # We need to add plugins/data to sys.path, mainly for PyQt6
    sys.path.insert(1, path.joinpath("plugins", "plugin_python", "libs").as_posix())

    import mobase  # type: ignore

    return mobase  # type: ignore


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

    args = parser.parse_args()

    mobase = load_mobase(args.install_dir)
