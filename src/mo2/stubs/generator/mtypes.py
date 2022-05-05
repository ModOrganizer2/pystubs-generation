# -*- encoding: utf-8 -*-

from __future__ import annotations

import re


class PyType:
    """
    Class representing a python type.
    """

    # The `MoVariant` actual type - This should be list["MoVariant"] and
    # Dict[str, "MoVariant"], but mypy (and other type checkers) do not
    # handle recursive definition yet:
    MO_VARIANT = """Union[None, bool, int, str, list[Any], dict[str, Any]]"""

    # File/Directory wrappers
    FILE_WRAPPER = """Union[str, PyQt6.QtCore.QFileInfo, Path]"""
    DIRECTORY_WRAPPER = """Union[str, PyQt6.QtCore.QDir, Path]"""

    name: str

    def __init__(self, name: str | type):
        # import only here since we change the path to find them
        from PyQt6 import QtCore, QtGui, QtWidgets

        if isinstance(name, type):
            name = name.__name__

        self.name = name.strip()

        # replace QFlags[xxx] with xxx
        self.name = re.sub(r"QFlags\[([^]]*)\]", r"\1", self.name)

        # find PyQt types
        for m in (QtCore, QtGui, QtWidgets):
            if self.name in dir(m):
                self.name = "{}.{}".format(m.__name__, self.name)

    def typing(self) -> str:
        """
        Returns:
            A valid typing representation for this type.
        """
        # IPluginBase -> IPlugin
        if self.name == "mobase.IPluginBase":
            return "IPlugin"

        return self.name

    def is_none(self) -> bool:
        """
        Check if this type represent None.

        Returns:
            True if this type represents None.
        """
        return self.name.lower() in ("none", "nonetype")

    def is_object(self) -> bool:
        """
        Check if this type represent the generic "object" type.

        Returns:
            True if this type represent the generic object type.
        """
        return self.name.lower() == "object"

    def is_any(self) -> bool:
        """
        Check if this type represent the typing "Any".

        Returns:
            True if this type represent the typing "Any".
        """
        return self.name == "Any"

    def __str__(self):
        return "Type({})".format(self.name)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PyType):
            return NotImplemented
        return self.name == other.name


class Return:
    """
    Class representing the return value of a function (type and documentation).
    """

    type: PyType
    doc: str

    def __init__(self, type: PyType, doc: str = ""):
        self.type = type
        self.doc = doc


class Argument:
    """
    Class representing a function argument (type and eventual default value).
    """

    # Constant representing None since None indicates no default value:
    DEFAULT_NONE = "None"

    name: str
    type: PyType
    _value: str | None
    doc: str

    def __init__(
        self, name: str, type: PyType, value: str | None = None, doc: str = ""
    ):
        self.name = name
        self.type = type
        self._value = value
        self.doc = doc

    @property
    def value(self) -> str | None:

        value = self._value

        if value is None:
            return None

        # pybind11 puts enum in <> so we need to fix
        m = re.match(r"<([^:]+):\s*[0-9]+>", value)
        if m:
            # if this is a mobase enum, we eed to use the upper case version
            if self.type.name.startswith("mobase"):
                value = m.group(1)
                parts = value.split(".")
                value = ".".join(parts[:-1] + [parts[-1].upper()])

            # PyQt -> need to fix
            elif self.type.name.startswith("PyQt"):
                parts = m.group(1).split(".")
                value = f"{self.type.name}.{parts[-1]}"
            else:
                value = m.group(1)

        return value

    def has_default_value(self) -> bool:
        return self.value is not None

    def __str__(self):
        if self.has_default_value():
            return "Arg({}={})".format(self.type, self.value)
        return "Arg({})".format(self.type)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.type)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Argument):
            return NotImplemented
        return self.type == other.type


class Exception:

    """
    Small class representing exception that can be raised from functions.
    """

    type: PyType
    doc: str

    def __init__(self, type: PyType, doc: str = ""):
        self.type = type
        self.doc = doc


class Function:
    """
    Class representing a function.
    """

    name: str
    ret: Return
    args: list[Argument]
    overloads: bool
    raises: list[Exception]
    doc: str
    deprecated: bool

    def __init__(
        self,
        name: str,
        ret: Return,
        args: list[Argument],
        has_overloads: bool = False,
        doc: str = "",
    ):
        self.name = name
        self.ret = ret
        self.args = args
        self.overloads = has_overloads
        self.raises = []
        self.doc = ""
        self.deprecated = False

    def has_overloads(self):
        return self.overloads

    def is_deprecated(self):
        return self.deprecated


class Method(Function):
    """
    Class representing a method.
    """

    cls: Class
    abstract: str | bool
    static: bool

    def __init__(
        self,
        name: str,
        ret: Return,
        args: list[Argument],
        static: bool,
        has_overloads: bool = False,
        doc: str = "",
    ):
        super().__init__(name, ret, args, has_overloads, doc)
        self.static = static
        self.abstract = "auto"

    def is_abstract(self):
        if self.name.startswith("__"):
            return False
        if self.abstract == "auto":
            return self.cls.is_abstract()
        return self.abstract

    def is_static(self):
        return self.static

    def is_special(self):
        return self.name.startswith("__")

    def is_constructor(self):
        return self.name == "__init__"


class Constant:
    """
    Class representing a constant.
    """

    name: str
    type: PyType | None
    value: object
    doc: str | None

    def __init__(
        self, name: str, type: PyType | None, value: object, doc: str | None = None
    ):
        self.name = name
        self.type = type

        # Note: The value is not used actually since we can hide it using `...`.
        self.value = value
        self.doc = doc


class Property:
    """
    Class representing a property.
    """

    name: str
    type: PyType
    doc: str
    read_only: bool

    def __init__(self, name: str, type: PyType, read_only: bool, doc: str = ""):
        self.name = name
        self.type = type
        self.read_only = read_only
        self.doc = doc

    def is_read_only(self):
        return self.read_only


class Class:
    """
    Class representing a class.
    """

    name: str
    bases: list[Class]
    methods: list[Method]
    constants: list[Constant]
    properties: list[Property]
    inner_classes: list[Class]
    outer_class: Class | None
    doc: str
    abstract: bool
    deprecated: bool

    def __init__(
        self,
        package: str,
        name: str,
        bases: list[Class],
        methods: list[Method],
        constants: list[Constant] = [],
        properties: list[Property] = [],
        inner_classes: list[Class] = [],
        doc: str = "",
    ):
        self.package = package
        self.name = name
        self.bases = bases
        self.methods = methods
        self.properties = properties
        self.constants = constants
        self.inner_classes = inner_classes
        self.doc = ""
        self.abstract = False
        self.outer_class = None
        self.deprecated = False

        # Update class in method:
        for m in self.methods:
            m.cls = self
        for ic in self.inner_classes:
            ic.outer_class = self

    def is_abstract(self):
        """
        Returns:
            True if this class is abstract, False otherwise.
        """
        return self.abstract or any(bc.is_abstract() for bc in self.bases)

    @property
    def canonical_name(self):
        """
        Returns:
            The canonical name of this class.
        """
        name = self.name
        oc = self.outer_class
        while oc is not None:
            name = "{}.{}".format(oc.name, name)
            oc = oc.outer_class

        return name

    @property
    def full_name(self):
        """
        Returns:
            The full name of this class, i.e., package.canonical_name.
        """
        if self.package:
            return f"{self.package}.{self.canonical_name}"
        return self.canonical_name

    @property
    def all_bases(self) -> set[Class]:
        """
        Returns:
            All the bases of this class, including bases of bases and so on.
        """
        bases = set(self.bases)
        for b in self.bases:
            bases = bases.union(b.all_bases)
        return bases

    def is_deprecated(self):
        return self.deprecated


class PyClass(Class):

    """
    Class use to wrap Python class to be used as parent class for some classes
    in mobase.
    """

    def __init__(
        self,
        package: str,
        name: str,
    ):
        super().__init__(package, name, [], [])
        self.abstract = False


class Enum(Class):

    """
    Class representing an enum.
    """

    def __init__(
        self, package: str, name: str, values: dict[str, int], methods: list[Method]
    ):
        # Note: Boost.Python.enum inherits int() not enum.Enum() but for the sake
        # of stubs, I think making them inherit enum.Enum is more appropriate:
        super().__init__(
            package,
            name,
            [PyClass("", "Enum")],
            methods,
            inner_classes=[],
            constants=[Constant(k, None, v) for k, v in values.items()],
        )

    def is_abstract(self):
        return False
