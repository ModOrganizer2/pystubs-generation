# -*- encoding: utf-8 -*-

import argparse
import logging
import sys

from pathlib import Path

from generator import logger
from generator.loader import load_mobase
from generator.register import MOBASE_REGISTER
from generator.parser import is_enum
from generator.mtypes import Type, Class, Enum
from generator.utils import Settings, clean_class, patch_class
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
    type=argparse.FileType("w"),
    default=sys.stdout,
    help="output file (output to stdout if not specified)",
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

if args.verbose:
    logger.setLevel(logging.INFO)

# Load settings from the configuration:
if args.config is not None:
    Settings.load_from_file(args.config)

# Load mobase (cannot simply do "import mobase"):
mobase = load_mobase(Path(args.install_dir))

# Create the writer:
writer = Writer(args.output)
writer.print_imports(
    [
        ("enum", ["Enum"]),
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
            ],
        ),
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
    ]
)

# Needs to define the MVariant type:
writer._print("MoVariant = {}".format(Type.MO_VARIANT))
writer._print()

# This is a class to represent interface not implemented:
writer.print_class(Class("InterfaceNotImplemented", [], []))
writer._print()

# List of objects:
objects = []

for name in dir(mobase):
    if name.startswith("__"):
        continue

    if name in Settings.IGNORE_NAMES:
        continue

    # if name not in ["GuessedString"]:
    #     continue

    objects.append((name, getattr(mobase, name)))

# Enum first, and then alphabetical. Might cause issue with base classes, so
# maybe create a kind of dependency...
# For argument or return types, this should not be an issue since we quote
# everything from mobase.
objects = sorted(objects, key=lambda e: (not is_enum(e[1]), e[0]))

for n, o in objects:
    MOBASE_REGISTER.add_object(n, o)

for n, o in objects:

    # Only supports generation for class currently:
    if not isinstance(o, type):
        logger.critical(
            "Cannot generated stubs for {}, unsupported object type.".format(n)
        )
        continue

    # Create the corresponding object:
    c = MOBASE_REGISTER.make_object(n, o)

    # Clean the class (e.g., remove duplicates methods due to wrappers):
    clean_class(c)

    # Fix the class if required:
    patch_class(c, Settings.OVERWRITES)

    # Print the class:
    writer.print_class(c)
    if isinstance(c, Enum):
        writer._print()
    writer._print()
