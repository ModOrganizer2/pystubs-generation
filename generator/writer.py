# -*- encoding: utf-8 -*-

from typing import TextIO, List, Union, Tuple

from . import logger
from .mtypes import Function, Class, Method, Property, Enum
from .utils import Settings


class Writer:

    _output: TextIO
    _settings: Settings

    def __init__(self, output: TextIO, settings: Settings):
        self._output = output
        self._settings = settings

    def _print(self, *args, **kwargs):
        kwargs["file"] = self._output
        print(*args, **kwargs)

    def _print_doc(self, doc: str, indent: str):
        """Print the given documentation at the given indentaiton level.

        Args:
            doc: Documentation to print.
            indent: Indentation.
        """
        # Wrap in triple quotes:
        doc = '"""\n' + doc.strip() + '\n"""'
        self._print("\n".join((indent + line).rstrip() for line in doc.split("\n")))

    def print_version(self, version: str):
        self._print('__version__ = "{}"'.format(version))
        self._print()

    def print_imports(self, imports: List[Union[str, Tuple[str, List[str]]]]):
        """ Print the given imports. """
        for imp in imports:
            if isinstance(imp, str):
                self._print("import {}".format(imp))
            else:
                self._print("from {} import {}".format(imp[0], ", ".join(imp[1])))
        self._print()

    def print_function(self, fn: Function, indent: str = ""):
        """ Print the given Function object at the given indentation level. """

        if fn.has_overloads():
            self._print("{}@overload".format(indent))

        srtype = ""
        if not fn.ret.type.is_none():
            srtype = " -> " + fn.ret.type.typing(self._settings)

        fargs = fn.args
        largs: List[str] = []
        if isinstance(fn, Method):
            if fn.is_static():
                self._print("{}@staticmethod".format(indent))
            else:
                if fn.is_abstract():
                    self._print("{}@abc.abstractmethod".format(indent))

                largs.insert(0, "self")
                fargs = fargs[1:]

        for i, arg in enumerate(fargs):
            tmp = "{}: {}".format(arg.name, arg.type.typing(self._settings))
            if arg.has_default_value():
                tmp += " = {}".format(arg.value)
            largs.append(tmp)
        sargs = ", ".join(largs)

        self._print("{}def {}({}){}:".format(indent, fn.name, sargs, srtype), end="")

        # Add the documentation, if any:
        doc = ""

        if fn.doc:
            doc = fn.doc.strip() + "\n"

        args = fn.args
        if isinstance(fn, Method) and not fn.is_static():
            args = args[1:]

        if any(arg.doc for arg in args):
            doc += "\nArgs:\n"
            for arg in args:
                adocl = arg.doc.strip().split("\n")
                adoc = "\n".join([adocl[0]] + ["        " + ldoc for ldoc in adocl[1:]])
                doc += "    " + arg.name + ": " + adoc + "\n"

        if not fn.ret.type.is_none() and fn.ret.doc:
            doc += "\nReturns:\n    " + fn.ret.doc.strip() + "\n"

        if fn.raises:
            doc += "\nRaises:\n"
            for rai in fn.raises:
                doc += (
                    "    "
                    + rai.type.typing(self._settings)
                    + ": "
                    + rai.doc.strip()
                    + "\n"
                )

        if doc:
            self._print()
            self._print_doc(doc, indent + "    ")
            self._print("{}...".format(indent + "    "))
        else:
            self._print(" ...")

        if not isinstance(fn, Method):
            self._print()

    def print_property(self, cls: Class, prop: Property, indent: str):
        """ Print the given Property object at the given indentation level. """

        if prop.type.is_object() or prop.type.is_any():
            logger.warning(
                "Property {}.{} does not have a specified type.".format(
                    cls.name, prop.name
                )
            )

        self._print("{}@property".format(indent))
        self._print(
            "{}def {}(self) -> {}: ...".format(
                indent, prop.name, prop.type.typing(self._settings)
            )
        )
        if not prop.is_read_only():
            self._print("{}@{}.setter".format(indent, prop.name))
            self._print(
                "{}def {}(self, arg0: {}): ...".format(
                    indent, prop.name, prop.type.typing(self._settings)
                )
            )
        self._print()

    def print_class(self, cls: Class, indent: str = ""):
        """ Print the given Class object at the given indentation level. """

        bc = ""
        if cls.bases or cls.is_abstract():
            bases = [str(bc) for bc in cls.bases]
            if cls.is_abstract() and not any(bc.is_abstract() for bc in cls.bases):
                bases.insert(0, "abc.ABC")
            bc = "(" + ", ".join(bases) + ")"

        # Class declaration:
        self._print("{}class {}{}:".format(indent, cls.name, bc), end="")

        if cls.doc:
            self._print()
            self._print_doc(cls.doc, indent + "    ")
            self._print()

        if not (cls.methods or cls.constants or cls.properties or cls.inner_classes):
            if cls.doc:
                self._print("{}...".format(indent + "    "))
            else:
                self._print(" ...")
            return

        if not cls.doc:
            self._print()

        # Inner classes:
        for iclass in cls.inner_classes:
            self.print_class(iclass, indent=indent + "    ")
            self._print()

        # Constants:
        for constant in cls.constants:
            comment = ""
            if constant.doc:
                comment = "  # {}".format(constant.doc)

            typing = ""
            if constant.type is not None:
                typing = ": {}".format(constant.type.typing(self._settings))

            # Note: We do not print the value, we use ...
            self._print(
                "{}{}{} = {}{}".format(
                    indent + "    ", constant.name, typing, "...", comment,
                )
            )

        if cls.constants and (cls.properties or cls.methods):
            self._print()

        # Properties:
        for prop in cls.properties:
            self.print_property(cls, prop, indent=indent + "    ")

        # Methods:
        # Put __init__ first, then special, then by name:
        methods = sorted(
            cls.methods,
            key=lambda m: (m.name != "__init__", not m.is_special(), m.name),
        )
        for method in methods:
            self.print_function(method, indent=indent + "    ")

        if cls.methods:
            self._print()

        if not cls.outer_class:
            if isinstance(cls, Enum):
                self._print()
            self._print()
