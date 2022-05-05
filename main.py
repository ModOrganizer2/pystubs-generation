# -*- encoding: utf-8 -*-

import argparse
import logging
from pathlib import Path
from typing import cast

import black
import isort

from generator import LOGGER
from generator.loader import load_mobase
from generator.mtypes import Class, Function, PyType
from generator.parser import is_enum
from generator.register import MOBASE_REGISTER
from generator.utils import Settings, clean_class
from generator.writer import Writer

parser = argparse.ArgumentParser("Stubs generator for the MO2 python interface")
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
    default="stubs/setup/mobase-stubs/__init__.pyi",
    help="output file (default stubs/setup/mobase-stubs/__init__.pyi)",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="verbose mode (all logs go to stderr)"
)
parser.add_argument(
    "-c",
    "--config",
    type=argparse.FileType("r"),
    default=None,
    help="configuration file",
)

args = parser.parse_args()

logging.basicConfig()
LOGGER.setLevel(logging.WARNING)

if args.verbose:
    LOGGER.setLevel(logging.INFO)

output_path = cast(Path, args.output)

# Load settings from the configuration:
settings: Settings = Settings(register=MOBASE_REGISTER)
if args.config is not None:
    settings = Settings(MOBASE_REGISTER, args.config)

# Parse mobase:

# Load mobase (cannot simply do "import mobase"):
mobase = load_mobase(Path(args.install_dir))

# List of objects:
objects = []

for name in dir(mobase):
    if name.startswith("__"):
        continue

    if name in settings.ignore_names:
        continue

    # we do not want the real MoVariant
    if name == "MoVariant":
        continue

    # ignore the private module
    if name == "private":
        continue

    # for now, ignore this since it is a submodule and we
    # not handle them
    if name == "widgets":
        continue

    # IPlugin is not the real object
    if name == "IPlugin":
        continue

    objects.append((name, getattr(mobase, name)))

# enum first, and then alphabetical, should be fine with the __future__ import
objects = sorted(
    objects, key=lambda e: (isinstance(e[1], type), not is_enum(e[1]), e[0])
)

for n, o in objects:
    MOBASE_REGISTER.add_object(n, o)

# Process everything:
for n, o in objects:

    # Create the corresponding object:
    c = MOBASE_REGISTER.make_object(n, o)

    if isinstance(c, Class):

        # Clean the class (e.g., remove duplicates methods due to wrappers):
        clean_class(c, settings)

        # Path the class using the configuration:
        settings.patch_class(c)

    elif isinstance(c, list) and isinstance(c[0], Function):
        settings.patch_functions(c)

    else:
        LOGGER.critical(
            "Cannot generated stubs for {}, unsupported object type.".format(n)
        )

# Write everything:
with open(args.output, "w") as output:

    writer = Writer(output, settings)

    # the __future__ import must be at the beginning
    writer.print_imports([("__future__", ["annotations"])])
    writer.print_version(settings.mobase["__version__"])  # type: ignore
    writer.print_imports(
        [
            "abc",
            ("enum", ["Enum"]),
            ("pathlib", ["Path"]),
            (
                "typing",
                [
                    "Dict",
                    "Iterable",
                    "Iterator",
                    "List",
                    "Tuple",
                    "Union",
                    "Any",
                    "Optional",
                    "Callable",
                    "overload",
                    "Set",
                    "TypeVar",
                    "Type",
                ],
            ),
            "PyQt6.QtCore",
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
        ]
    )

    # Needs to define the MVariant and GameFeatureType type:
    writer._print(f"MoVariant = {PyType.MO_VARIANT}")
    writer._print(f"FileWrapper = {PyType.FILE_WRAPPER}")
    writer._print(f"DirectoryWrapper = {PyType.DIRECTORY_WRAPPER}")
    writer._print('GameFeatureType = TypeVar("GameFeatureType")')
    writer._print()

    # This is a class to represent interface not implemented:
    writer.print_class(Class("InterfaceNotImplemented", [], []))
    writer._print()

    for n, o in objects:

        # Get the corresponding object:
        c = MOBASE_REGISTER.get_object(n)

        if isinstance(c, Class):
            writer.print_class(c)

        elif isinstance(c, list) and isinstance(c[0], Function):
            for fn in c:
                writer.print_function(fn)

black.format_file_in_place(
    output_path,
    fast=False,
    mode=black.Mode(is_pyi=args.output.name.endswith("pyi")),
    write_back=black.WriteBack.YES,
)
isort.api.sort_file(output_path)
