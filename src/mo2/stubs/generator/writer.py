import logging
from typing import Any, Iterable, TextIO

from typing_extensions import TypeIs

from .mtypes import Class, Constant, Enum, Function, Method, Property, PyTyping
from .utils import Settings

LOGGER = logging.getLogger(__package__)


def is_list_of_functions(e: Any | Iterable[Any]) -> TypeIs[list[Function]]:
    if not isinstance(e, list):
        return False
    return all(isinstance(x, Function) for x in e)


class Writer:
    _output: TextIO
    _settings: Settings

    def __init__(self, package: str, output: TextIO, settings: Settings):
        self._package = package.split(".")
        self._output = output
        self._settings = settings

    def _fix_typing(self, value: str) -> str:
        for pkg in self._package:
            value = value.replace(pkg + ".", "")
        return value

    def _print(
        self,
        *values: object,
        sep: str | None = " ",
        end: str | None = "\n",
        flush: bool = False,
    ) -> None:
        print(*values, sep=sep, end=end, flush=flush, file=self._output)

    def _print_doc(self, doc: str, indent: str):
        """
        Print the given documentation at the given indentation level.

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

    def print_imports(self, imports: list[str | tuple[str, list[str]]]):
        """
        Print the given imports.
        """
        for imp in imports:
            if isinstance(imp, str):
                self._print("import {}".format(imp))
            else:
                self._print("from {} import {}".format(imp[0], ", ".join(imp[1])))
        self._print()

    def print_function(self, fn: Function, indent: str = ""):
        """
        Print the given Function object at the given indentation level.
        """

        if fn.has_overloads():
            self._print("{}@overload".format(indent))

        sig_return_type = ""
        if not fn.ret.type.is_none():
            sig_return_type = " -> " + self._fix_typing(fn.ret.type.typing())
        else:
            sig_return_type = " -> None"

        if isinstance(fn, Method):
            if fn.is_static():
                self._print("{}@staticmethod".format(indent))
            else:
                if fn.is_abstract():
                    self._print("{}@abc.abstractmethod".format(indent))

        python_args: list[str] = []
        for arg in fn.args:
            tmp = "{}: {}".format(arg.name, self._fix_typing(arg.type.typing()))
            if arg.has_default_value():
                tmp += " = {}".format(arg.value)
            python_args.append(tmp)

        self._print(
            "{}def {}({}){}:".format(
                indent, fn.name, ", ".join(python_args), sig_return_type
            ),
            end="",
        )

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
                arg_doc_list = arg.doc.strip().split("\n")
                arg_doc = "\n".join(
                    [arg_doc_list[0]]
                    + ["        " + line_doc for line_doc in arg_doc_list[1:]]
                )
                doc += "    " + arg.name + ": " + arg_doc + "\n"

        if not fn.ret.type.is_none() and fn.ret.doc:
            doc += "\nReturns:\n    " + fn.ret.doc.strip() + "\n"

        if fn.raises:
            doc += "\nRaises:\n"
            for rai in fn.raises:
                doc += (
                    "    "
                    + self._fix_typing(rai.type.typing())
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
        """
        Print the given Property object at the given indentation level.
        """

        if prop.type.is_object() or prop.type.is_any():
            LOGGER.warning(
                "Property {}.{} does not have a specified type.".format(
                    cls.name, prop.name
                )
            )

        self._print("{}@property".format(indent))
        self._print(
            "{}def {}(self) -> {}: ...".format(
                indent, prop.name, self._fix_typing(prop.type.typing())
            )
        )
        if not prop.is_read_only():
            self._print("{}@{}.setter".format(indent, prop.name))
            self._print(
                "{}def {}(self, arg0: {}) -> None: ...".format(
                    indent, prop.name, self._fix_typing(prop.type.typing())
                )
            )
        self._print()

    def print_class(self, cls: Class, indent: str = ""):
        """
        Print the given Class object at the given indentation level.
        """

        bc = ""
        if cls.bases or cls.is_abstract():
            bases: list[str] = [
                bc.canonical_name if bc.package.startswith("mobase") else bc.full_name
                for bc in cls.bases
            ]
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
        for inner_class in cls.inner_classes:
            self.print_class(inner_class, indent=indent + "    ")
            self._print()

        # Constants:
        for constant in cls.constants:
            comment = ""
            if constant.doc:
                comment = "  # {}".format(constant.doc)

            typing = ""
            if constant.type is not None:
                typing = ": {}".format(self._fix_typing(constant.type.typing()))

            # Note: We do not print the value, we use ...
            self._print(
                "{}{}{} = {}{}".format(
                    indent + "    ",
                    constant.name,
                    typing,
                    "...",
                    comment,
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

    def print_typing(self, typ: PyTyping):
        self._print(f"{typ.name} = {typ.typing}")

    def print_constent(self, constant: Constant):
        assert constant.type is not None
        self._print(
            "{}: {} = ...".format(
                constant.name, self._fix_typing(constant.type.typing())
            )
        )

    def print_object(self, e: Class | Constant | list[Function] | PyTyping):
        if isinstance(e, Class):
            self.print_class(e)

        elif is_list_of_functions(e):
            for fn in e:
                self.print_function(fn)

        elif isinstance(e, PyTyping):
            self.print_typing(e)

        else:
            self.print_constent(e)
