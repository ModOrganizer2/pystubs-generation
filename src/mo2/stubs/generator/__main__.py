import argparse
import inspect
import logging
import subprocess
import types
from collections.abc import Sequence
from pathlib import Path
from typing import Callable

from .loader import load_mobase
from .mtypes import Class, PyTyping
from .parser import is_enum
from .register import MobaseRegister
from .utils import Settings, clean_class
from .writer import Writer, is_list_of_functions

LOGGER = logging.getLogger(__package__)


def extract_objects(
    module: object, skips: Sequence[str] = []
) -> list[tuple[str, type]]:
    objects: list[tuple[str, type]] = []

    assert hasattr(module, "__name__")
    module_name: str = module.__name__  # type: ignore

    for name in dir(module):
        if name.startswith("__") or name in skips:
            continue

        obj = getattr(module, name)

        # skip submodules
        if inspect.ismodule(obj):
            continue

        # skip imports - type object have wrong __module__?
        if hasattr(obj, "__module__") and obj.__module__ != module_name:
            if obj.__module__ != types.__name__ or hasattr(types, name):
                continue

        objects.append((name, obj))

    return objects


def add_mobase_header(writer: Writer):
    writer.print_imports(
        [
            "abc",
            ("enum", ["Enum"]),
            "os",
            (
                "typing",
                [
                    "Callable",
                    "Dict",
                    "Iterator",
                    "Optional",
                    "overload",
                    "Sequence",
                    "Type",
                    "TypeVar",
                    "Union",
                ],
            ),
            "PyQt6.QtCore",
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
        ]
    )


def add_mobase_widgets_header(writer: Writer):
    writer.print_imports(
        [
            (
                "typing",
                ["List", "Tuple", "Union", "overload"],
            ),
            "PyQt6.QtCore",
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser("stubs generator for the MO2 python interface")
    parser.add_argument(
        "install_dir",
        metavar="INSTALL_DIR",
        type=Path,
        default=None,
        help="installation directory of Mod Organizer 2",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("stubs/setup/mobase-stubs"),
        help="output folder (default stubs/setup/mobase-stubs)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose mode (all logs go to stderr)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="configuration file",
    )

    args = parser.parse_args()

    logging.basicConfig()
    LOGGER.setLevel(logging.WARNING)

    if args.verbose:
        LOGGER.setLevel(logging.INFO)

    output_path: Path = args.output
    config_path: Path | None = args.config

    # create the register
    register = MobaseRegister()

    # load mobase (cannot simply do "import mobase")
    mobase = load_mobase(Path(args.install_dir))

    # headers
    module_headers: dict[str, Callable[[Writer], None]] = {
        "mobase": add_mobase_header,
        "mobase.widgets": add_mobase_widgets_header,
    }

    # list of objects directly in mobase
    module_objects: dict[str, list[tuple[str, type]]] = {
        "mobase": extract_objects(
            mobase,
            [
                # the "real" IPlugin is IPluginBase
                "IPlugin",
            ],
        ),
        "mobase.widgets": extract_objects(mobase.widgets),  # type: ignore
    }

    for name, objects in module_objects.items():
        # load settings from the configuration
        settings: Settings = Settings(register)
        if config_path is not None:
            with open(config_path, "r") as fp:
                settings = Settings(register, fp, module=name)

        for n, o in objects:
            register.add_object(n, o)

        # enum first, and then alphabetical, should be fine with the __future__ import
        objects = sorted(
            objects, key=lambda e: (isinstance(e[1], type), not is_enum(e[1]), e[0])
        )

        # Process everything:
        for n, o in objects:
            # Create the corresponding object:
            c = register.make_object(n, o)

            if isinstance(c, Class):
                # Clean the class (e.g., remove duplicates methods due to wrappers):
                clean_class(c)

                # Path the class using the configuration:
                settings.patch_class(c)

            elif isinstance(c, PyTyping):
                ...

            elif is_list_of_functions(c):
                settings.patch_functions(c)

            else:
                LOGGER.critical(
                    "Cannot generated stubs for {}, unsupported object type.".format(n)
                )

        output_folder = output_path
        if name != "mobase":
            output_folder = output_path.joinpath(
                name.replace("mobase.", "").replace(".", "/")
            )

        # create directory if required
        output_folder.mkdir(parents=True, exist_ok=True)

        # write everything
        with open(output_folder.joinpath("__init__.pyi"), "w") as output:
            writer = Writer(package=name, output=output, settings=settings)

            # the __future__ import must be at the beginning
            writer.print_imports([("__future__", ["annotations"])])
            writer.print_version(settings.version)

            module_headers[name](writer)

            for n, _o in objects:
                # Get the corresponding object:
                c = register.get_object(n)

                writer.print_object(c)

        subprocess.run(
            [
                "ruff",
                "--silent",
                "format",
                output_folder.joinpath("__init__.pyi").as_posix(),
            ]
        )
        subprocess.run(
            [
                "ruff",
                "--silent",
                "check",
                "--select",
                "I",
                "--fix",
                output_folder.joinpath("__init__.pyi").as_posix(),
            ]
        )


if __name__ == "__main__":
    main()
