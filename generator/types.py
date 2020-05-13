# -*- encoding: utf-8 -*-

from typing import Optional, List, Any, Dict

from . import logger


class Type:
    """ Class representing a python type. """

    # The `MoVariant` actual type:
    MO_VARIANT = """Union[bool, int, str, List["MoVariant"], Dict[str, "MoVariant"]]"""

    name: str

    def __init__(self, name: str):
        # Import only here since we change the path to find them:
        from PyQt5 import QtCore, QtGui, QtWidgets

        self.name = name.strip()

        # We replace QVariant with MoVariant which is valid python type:
        if self.name == "QVariant":
            self.name = "MoVariant"

        # Find PyQt types:
        for m in (QtCore, QtGui, QtWidgets):
            if self.name in dir(m):
                self.name = "{}.{}".format(m.__name__, self.name)

    def typing(self) -> str:
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
        return self.name.lower() == "none"

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

    def _try_fix(self, name):

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
                args = [parse_ctype(c).typing() for c in magic_split(name)]
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
                arg = parse_ctype(magic_split(name)[0]).typing()
                name = "List[{}]".format(arg)

        for c in ("std::map", "std::unordered_map", "QMap"):
            if name.startswith(c):
                name = name[len(c) :].strip()[1:-1].strip()
                a1, a2 = [parse_ctype(x).typing() for x in magic_split(name)[:2]]
                name = "Dict[{}, {}]".format(a1, a2)

        for c in ("boost::tuples::tuple", "std::tuple"):
            if name.startswith(c):
                name = name[len(c) :].strip()[1:-1].strip()
                args = [parse_ctype(c).typing() for c in magic_split(name)]
                args = [a for a in args if a != "boost::tuples::null_type"]
                name = "Tuple[{}]".format(", ".join(args))

        # Fix for function...
        if name.startswith("std::function"):
            name = name[13:].strip()[1:-1].strip()
            rtype, args = parse_csig(name, "")
            name = "Callable[[{}], {}]".format(
                ", ".join(a.type.typing() for a in args), rtype.typing()
            )

        if pname != name:
            logger.info("Fixed {} to {}. ".format(pname, name))
        else:
            logger.critical(
                "Failed to fix {}, a custom rule is probably required.".format(name)
            )

        return name

    def _is_builtin_python_type(self, t: Type):
        """ Check if the given type is a 'raw' python type, i.e., a type that cannot
        be a C++ reference. This is mainly used to report errors when pointers to such
        type are present in the interface. """
        return t.name in ["bool", "int", "float", "str", "list", "std", "dict", "bytes"]

    def typing(self) -> str:
        """ Returns a valid typing representation for this type. """
        from .register import MOBASE_REGISTER
        from .utils import Settings

        name = self.name

        if self.is_none():
            return "None"

        if name in CType.STANDARD_TYPES:
            name = CType.STANDARD_TYPES[name]

        if name in CType.REPLACEMENTS:
            name = CType.REPLACEMENTS[name]

        if name in Settings.REPLACEMENTS:
            logger.warning(
                "Replacing {} with {}.".format(name, Settings.REPLACEMENTS[name])
            )
            name = Settings.REPLACEMENTS[name]

        # If the name contains stuff that should not be there, try some
        # "magic" conversion:
        if self._is_not_valid(name):
            name = self._try_fix(name)

        if name in MOBASE_REGISTER.py2cpp:
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


class Arg:
    """ Class representing a function argument (type and eventual default value). """

    # Constant representing None since None indicates no default value:
    DEFAULT_NONE = "None"

    type: Type
    _value: Optional[str]

    def __init__(self, type: Type, value: Optional[str] = None):
        self.type = type
        self._value = value

    @property
    def value(self) -> Optional[str]:
        from .register import MOBASE_REGISTER

        value = self._value

        if value is None:
            return None

        # Boost has a tendency to put `mobase.` in front of default values...
        if value is not None and value.startswith("mobase."):
            value = value[7:]

        # I have issues with inner classes, so we need to prepend manually...
        if value.find(".") != -1:
            parts = value.split(".")
            tvalue = ".".join(parts[:-1])
            for k in MOBASE_REGISTER.objects:
                if k != tvalue and k.endswith(tvalue) and k[-len(tvalue) - 1] == ".":
                    value = "{}.{}".format(k, parts[-1])

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


class Function:
    """ Class representing a function. """

    name: str
    rtype: Type
    args: List[Arg]
    overloads: bool

    def __init__(
        self, name: str, rtype: Type, args: List[Arg], has_overloads: bool = False
    ):
        self.name = name
        self.rtype = rtype
        self.args = args
        self.overloads = has_overloads

    def has_overloads(self):
        return self.overloads


class Method(Function):
    """ Class representing a method. """

    class_name: str
    static: bool

    def __init__(
        self,
        cls: str,
        name: str,
        rtype: Type,
        args: List[Arg],
        static: bool,
        has_overloads: bool = False,
    ):
        super().__init__(name, rtype, args, has_overloads)
        self.class_name = cls
        self.static = static

    def is_static(self):
        return self.static

    def is_special(self):
        return self.name.startswith("__")

    def is_constructor(self):
        return self.name == "__init__"


class Constant:
    """ Class representing a constant. """

    name: str
    type: Type
    value: Any
    comment: Optional[str]

    def __init__(
        self, name: str, type: Type, value: Any, comment: Optional[str] = None
    ):
        self.name = name
        self.type = type

        # Note: The value is not used actually since we can hide it using `...`.
        self.value = value
        self.comment = comment


class Property:
    """ Class representing a property. """

    name: str
    type: Type
    read_only: bool

    def __init__(self, name: str, type: Type, read_only: bool):
        self.name = name
        self.type = type
        self.read_only = read_only

    def is_read_only(self):
        return self.read_only


class Class:
    """ Class representing a class. """

    name: str
    bases: List[str]
    methods: List[Method]
    constants: List[Constant]
    properties: List[Property]
    inner_classes: List["Class"]

    def __init__(
        self,
        name: str,
        bases: List[str],
        methods: List[Method],
        constants: List[Constant] = [],
        properties: List[Property] = [],
        inner_classes: List["Class"] = [],
    ):

        self.name = name
        self.bases = bases
        self.methods = methods
        self.properties = properties
        self.constants = constants
        self.inner_classes = inner_classes


class Enum(Class):
    """ Class representing an enum. """

    def __init__(self, name: str, values: Dict[str, int]):
        # Note: Boost.Python.enum inherits int() not enum.Enum() but for the sake
        # of stubs, I think making them inherit enum.Enum is more appropriate:
        super().__init__(
            name,
            ["Enum"],
            [],
            inner_classes=[],
            constants=[Constant(k, None, v) for k, v in values.items()],
        )
