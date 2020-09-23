# -*- encoding: utf-8 -*-

from typing import Optional, List, Any, Dict, Union

from . import logger
from . import utils


class Type:
    """ Class representing a python type. """

    # The `MoVariant` actual type - This should be List["MoVariant"] and
    # Dict[str, "MoVariant"], but mypy (and other type checkers) do not
    # handle recursive definition yet:
    MO_VARIANT = """Union[None, bool, int, str, List[Any], Dict[str, Any]]"""

    name: str

    def __init__(self, name: Union[str, type]):
        # Import only here since we change the path to find them:
        from PyQt5 import QtCore, QtGui, QtWidgets

        if isinstance(name, type):
            name = name.__name__

        self.name = name.strip()

        # We replace QVariant with MoVariant which is valid python type:
        if self.name == "QVariant":
            self.name = "MoVariant"

        # Find PyQt types:
        for m in (QtCore, QtGui, QtWidgets):
            if self.name in dir(m):
                self.name = "{}.{}".format(m.__name__, self.name)

    def typing(self, settings: utils.Settings) -> str:
        """ Returns a valid typing representation for this type. """
        from .register import MOBASE_REGISTER

        # Check if this is a mobase object, in which case we escape:
        if self.name in MOBASE_REGISTER.objects:
            return '"{}"'.format(self.name)

        # Check in existing objects (also inner classes) - This may cause
        # issue with conflicts, but those should not be present:
        for k in MOBASE_REGISTER.objects:
            if k.split(".")[-1] == self.name:
                return '"{}"'.format(k)

        return self.name

    def is_none(self) -> bool:
        """ Check if this type represent None. """
        return self.name.lower() in ("none", "nonetype")

    def is_object(self) -> bool:
        """ Check if this type represent the generic "object" type. """
        return self.name.lower() == "object"

    def is_any(self) -> bool:
        """ Check if this type repesent the typing "Any". """
        return self.name == "Any"

    def __str__(self):
        return "Type({})".format(self.name)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Type):
            return NotImplemented
        return self.name == other.name


class CType(Type):
    """ Class representing a C++ type from boost::python. """

    # List of smart pointer types - Not including pointer that should not
    # be exposed (unique_ptr, weak_ptr):
    SMART_POINTERS = ["std::shared_ptr", "boost::shared_ptr", "QSharedPointer"]

    # Standard conversions (usually, the python signature is sufficient for
    # those, unless we found them inside a tuple):
    STANDARD_TYPES = {
        "short": "int",
        "int": "int",
        "long": "int",
        "float": "float",
        "double": "float",
    }

    # Replacements for typing (without warnings):
    REPLACEMENTS = {
        "QString": "str",
        "QStringList": "List[str]",
        "QWidget *": "PyQt5.QtWidgets.QWidget",
        "QMainWindow *": "PyQt5.QtWidgets.QMainWindow",
        "QObject *": "PyQt5.QtCore.QObject",
        "void *": "object",
        "api::object": "object",
    }

    _optional: bool

    def __init__(self, name: str, optional: bool = False):
        super().__init__(name)
        self._optional = optional

    def _is_not_valid(self, str):
        for x in str:
            if x in "<>():*":
                return True
        return False

    def _try_fix(self, name, settings: utils.Settings):

        from .parser import parse_ctype, magic_split, parse_csig
        from .register import MOBASE_REGISTER

        pname = name

        # Unconverted QFlags are int in python:
        if name.startswith("QFlags"):
            name = "int"

        # If pointer, try to fix the corresponding python name:
        if self.is_pointer():

            newname: Optional[str] = None

            # For display purpose:
            optstr = ""
            if self.is_optional():
                optstr = " [optional]"

            # Check if there is a type registered:
            if self.name in MOBASE_REGISTER.cpp2py:
                newtype = MOBASE_REGISTER.cpp2py[self.name]

                if newtype.is_object():
                    logger.critical(
                        (
                            "Found {} pointer but did not found any corresponding "
                            "python type, the interface is likely missing."
                        ).format(name)
                    )
                    return "InterfaceNotImplemented"

                if self._is_builtin_python_type(newtype):
                    logger.critical(
                        "Found {} which is a pointer to a built-in python type.".format(
                            self.name
                        )
                    )
                    return "InterfaceNotImplemented"

                newname = newtype.name

                # Note: No WARNING here as this is safe:
                logger.info("Replacing {} with {}{}.".format(name, newname, optstr))

            # "Tricky" fix for pointer raw pointer and smart pointers:
            elif self.is_raw_pointer():
                newname = name.strip("*").replace("const", "").strip()
                logger.warning("Replacing {} with {}{}.".format(name, newname, optstr))

            else:
                for ptr in self.SMART_POINTERS:
                    if name.startswith(ptr):
                        newname = name[len(ptr) :][1:-1].replace("const", "").strip()
                        logger.warning(
                            "Replacing {} with {}{}.".format(name, newname, optstr)
                        )

            if newname is not None:
                if self.is_optional():
                    if newname in MOBASE_REGISTER.py2cpp:
                        newname = '"{}"'.format(newname)
                    return "Optional[{}]".format(newname)
                else:
                    return newname

        # Variant:
        for c in ("boost::variant", "std::variant"):
            if name.startswith(c):
                name = name[len(c) :].strip()[1:-1].strip()
                args = [parse_ctype(c).typing(settings) for c in magic_split(name)]
                name = "Union[{}]".format(", ".join(args))

        for c in (
            "std::vector",
            "std::set",
            "std::unordered_set",
            "std::list",
            "QList",
            "QVector",
            "QSet",
        ):
            if name.startswith(c):
                name = name[len(c) :].strip()[1:-1].strip()
                arg = parse_ctype(magic_split(name)[0]).typing(settings)
                name = "List[{}]".format(arg)

        for c in ("std::map", "std::unordered_map", "QMap"):
            if name.startswith(c):
                name = name[len(c) :].strip()[1:-1].strip()
                a1, a2 = [
                    parse_ctype(x).typing(settings) for x in magic_split(name)[:2]
                ]
                name = "Dict[{}, {}]".format(a1, a2)

        for c in ("boost::tuples::tuple", "std::tuple"):
            if name.startswith(c):
                name = name[len(c) :].strip()[1:-1].strip()
                args = [parse_ctype(c).typing(settings) for c in magic_split(name)]
                args = [a for a in args if a != "boost::tuples::null_type"]
                name = "Tuple[{}]".format(", ".join(args))

        # Fix for function...
        if name.startswith("std::function"):
            name = name[13:].strip()[1:-1].strip()
            rtype, vargs = parse_csig(name, "")
            name = "Callable[[{}], {}]".format(
                ", ".join(a.type.typing(settings) for a in vargs),
                rtype.typing(settings),
            )

        if name.find("::") != -1:
            parts = name.split("::")

            # We are going to check if there is an exact python match for
            # this class (replacing :: by .):
            if parts[0] in MOBASE_REGISTER.py2cpp:
                cp: List[Class] = [MOBASE_REGISTER.objects[parts[0]]]  # type: ignore
                for p in parts[1:]:
                    for ic in cp[-1].inner_classes:
                        if ic.name == p:
                            cp.append(ic)
                            break
                if len(cp) == len(parts):
                    name = '"' + ".".join(parts) + '"'

        if pname != name:
            logger.info("Fixed {} to {}. ".format(pname, name))
        else:
            logger.critical(
                "Failed to fix {}, a custom rule is probably required.".format(name)
            )

        return name

    def _is_builtin_python_type(self, t: Type):
        """Check if the given type is a 'raw' python type, i.e., a type that cannot
        be a C++ reference. This is mainly used to report errors when pointers to such
        type are present in the interface."""
        return t.name in ["bool", "int", "float", "str", "list", "std", "dict", "bytes"]

    def typing(self, settings: utils.Settings) -> str:
        """ Returns a valid typing representation for this type. """
        from .register import MOBASE_REGISTER

        name = self.name

        if self.is_none():
            return "None"

        if name in CType.STANDARD_TYPES:
            name = CType.STANDARD_TYPES[name]

        if name in CType.REPLACEMENTS:
            name = CType.REPLACEMENTS[name]

        if name in settings.replacements:
            logger.warning(
                "Replacing {} with {}.".format(name, settings.replacements[name])
            )
            name = settings.replacements[name]

        # If the name contains stuff that should not be there, try some
        # "magic" conversion:
        if self._is_not_valid(name):
            name = self._try_fix(name, settings)

        if name in MOBASE_REGISTER.objects:
            name = '"{}"'.format(name)

        return name

    def is_raw_pointer(self) -> bool:
        """ Check if this type is a raw pointer type. """
        return self.name.endswith("*")

    def is_smart_pointer(self) -> bool:
        """ Check if this type is a smart pointer type. """

        for ptr in self.SMART_POINTERS:
            if self.name.startswith(ptr):
                return True

        return False

    def is_pointer(self) -> bool:
        """ Check if this type corresponds to a pointer type. """
        return self.is_raw_pointer() or self.is_smart_pointer()

    def is_optional(self) -> bool:
        """ Check if this type is optional (i.e., can be None in python). """
        return self._optional

    def is_none(self) -> bool:
        """ Check if this type represent None. """
        return self.name.lower() == "void"

    def is_object(self) -> bool:
        """ Check if this type represent the generic "object" type """
        return self.name.lower() == "_object *"

    def __str__(self) -> str:
        return "CType({})".format(self.name)

    def __repr__(self) -> str:
        return str(self)


class Ret:
    """ Class representing the return value of a function (type and documentation). """

    type: Type
    doc: str

    def __init__(self, type: Type, doc: str = ""):
        self.type = type
        self.doc = doc


class Arg:
    """ Class representing a function argument (type and eventual default value). """

    # Constant representing None since None indicates no default value:
    DEFAULT_NONE = "None"

    name: str
    type: Type
    _value: Optional[str]
    doc: str

    def __init__(
        self, name: str, type: Type, value: Optional[str] = None, doc: str = ""
    ):
        self.name = name
        self.type = type
        self._value = value
        self.doc = doc

    @property
    def value(self) -> Optional[str]:

        value = self._value

        if value is None:
            return None

        # Boost has a tendency to put `mobase.` in front of default values...
        if value is not None and value.startswith("mobase."):
            value = value[7:]

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
        if not isinstance(other, Arg):
            return NotImplemented
        return self.type == other.type


class Exc:

    """ Small class representing exception that can be raised from functions. """

    type: Type
    doc: str

    def __init__(self, type: Type, doc: str = ""):
        self.type = type
        self.doc = doc


class Function:
    """ Class representing a function. """

    name: str
    ret: Ret
    args: List[Arg]
    overloads: bool
    raises: List[Exc]
    doc: str
    deprecated: bool

    def __init__(
        self,
        name: str,
        ret: Ret,
        args: List[Arg],
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
    """ Class representing a method. """

    cls: "Class"
    abstract: Union[str, bool]
    static: bool

    def __init__(
        self,
        name: str,
        ret: Ret,
        args: List[Arg],
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
    """ Class representing a constant. """

    name: str
    type: Optional[Type]
    value: Any
    doc: Optional[str]

    def __init__(
        self, name: str, type: Optional[Type], value: Any, doc: Optional[str] = None
    ):
        self.name = name
        self.type = type

        # Note: The value is not used actually since we can hide it using `...`.
        self.value = value
        self.doc = doc


class Property:
    """ Class representing a property. """

    name: str
    type: Type
    doc: str
    read_only: bool

    def __init__(self, name: str, type: Type, read_only: bool, doc: str = ""):
        self.name = name
        self.type = type
        self.read_only = read_only
        self.doc = doc

    def is_read_only(self):
        return self.read_only


class Class:
    """ Class representing a class. """

    name: str
    bases: List["Class"]
    methods: List[Method]
    constants: List[Constant]
    properties: List[Property]
    inner_classes: List["Class"]
    outer_class: Optional["Class"]
    doc: str
    abstract: bool
    deprecated: bool

    def __init__(
        self,
        name: str,
        bases: List["Class"],
        methods: List[Method],
        constants: List[Constant] = [],
        properties: List[Property] = [],
        inner_classes: List["Class"] = [],
        doc: str = "",
    ):

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
        """ Return the canonical name of this class. """
        name = self.name
        oc = self.outer_class
        while oc is not None:
            name = "{}.{}".format(oc.name, name)
            oc = oc.outer_class

        return name

    @property
    def all_bases(self):
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

    def __str__(self):
        return self.canonical_name


class PyClass(Class):

    """Class use to wrap Python class to be used as parent class for some classes
    in mobase."""

    def __init__(
        self, name: str,
    ):
        super().__init__(name, [], [])
        self.abstract = False


class Enum(Class):
    """ Class representing an enum. """

    def __init__(self, name: str, values: Dict[str, int]):
        # Note: Boost.Python.enum inherits int() not enum.Enum() but for the sake
        # of stubs, I think making them inherit enum.Enum is more appropriate:
        super().__init__(
            name,
            [PyClass("Enum")],
            [
                Method(
                    "__{}__".format(mname),
                    Ret(Type(bool)),
                    [Arg("", Type(name)), Arg("other", Type(int))],
                    static=False,
                )
                for mname in ["and", "or", "rand", "ro"]
            ],
            inner_classes=[],
            constants=[Constant(k, None, v) for k, v in values.items()],
        )

    def is_abstract(self):
        return False
