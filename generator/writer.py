# -*- encoding: utf-8 -*-

from typing import TextIO, List, Union, Tuple

from . import logger
from .mtypes import Function, Class, Method, Property


class Writer:

    _output: TextIO

    def __init__(self, output: TextIO):
        self._output = output

    def _print(self, *args, **kwargs):
        kwargs["file"] = self._output
        print(*args, **kwargs)

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
        if not fn.rtype.is_none():
            srtype = " -> " + fn.rtype.typing()

        largs = []
        for i, arg in enumerate(fn.args):
            tmp = "arg{}: {}".format(i, arg.type.typing())
            if arg.has_default_value():
                tmp += " = {}".format(arg.value)
            largs.append(tmp)

        if isinstance(fn, Method):
            if fn.is_static():
                self._print("{}@staticmethod".format(indent))
            else:
                largs[0] = "self"
        sargs = ", ".join(largs)

        self._print("{}def {}({}){}: pass".format(indent, fn.name, sargs, srtype))

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
            "{}def {}(self) -> {}: pass".format(indent, prop.name, prop.type.typing())
        )
        if not prop.is_read_only():
            self._print("{}@{}.setter".format(indent, prop.name))
            self._print(
                "{}def {}(self, arg0: {}): pass".format(
                    indent, prop.name, prop.type.typing()
                )
            )
        self._print()

    def print_class(self, cls: Class, indent: str = ""):
        """ Print the given Class object at the given indentation level. """

        bc = ""
        if cls.bases:
            bc = "(" + ", ".join(cls.bases) + ")"

        # Class declaration:
        self._print("{}class {}{}:".format(indent, cls.name, bc), end="")

        if not (cls.methods or cls.constants or cls.properties or cls.inner_classes):
            self._print(" pass")
            return
        self._print()

        # Inner classes:
        for iclass in cls.inner_classes:
            self.print_class(iclass, indent=indent + "    ")
            self._print()

        # Constants:
        for constant in cls.constants:
            comment = ""
            if constant.comment:
                comment = "  # {}".format(constant.comment)

            typing = ""
            if constant.type is not None:
                typing = ": {}".format(constant.type.typing())

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
