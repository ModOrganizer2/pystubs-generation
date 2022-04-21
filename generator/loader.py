# -*- encoding: utf-8 -*-

import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path


def load_module(name: str, path: Path):
    # Create the loader:
    loader = importlib.machinery.ExtensionFileLoader(  # type: ignore
        name, path.as_posix()
    )

    # Extract the spec:
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None

    # Create the module and execute it?
    module = importlib.util.module_from_spec(spec)
    if module is None:
        raise ImportError(f"Failed to import module {name} from {path}.")

    loader.exec_module(module)

    return module


def load_mobase(path: Path, moprivate: bool = False):
    """
    Load the mobase from the given MO2 installation path and
    returns it.

    Args:
        path: Path to the MO2 installation (folder containing the ModOrganizer.exe).
        moprivate: If True, the moprivate module will also be loaded and returned
            alongside mobase.

    Returns: The mobase module.
    """

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
        os.add_dll_directory(str(path))  # type: ignore[attr-defined]
        os.add_dll_directory(str(path.joinpath("dlls")))  # type: ignore[attr-defined]

    # We need to add plugins/data to sys.path, mainly for PyQt6
    sys.path.insert(1, path.joinpath("plugins", "data").as_posix())

    mobase = load_module("mobase", path.joinpath("plugins", "data", "pythonrunner.dll"))

    if not moprivate:
        return mobase

    moprivate = load_module(
        "moprivate", path.joinpath("plugins", "data", "pythonrunner.dll")
    )

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
