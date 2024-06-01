import inspect
import logging
import re
import types
from collections import OrderedDict, defaultdict
from itertools import chain
from typing import Any, Iterable, cast

from .mtypes import (
    Argument,
    Class,
    Constant,
    Enum,
    Function,
    Method,
    Property,
    PyClass,
    PyType,
    Return,
)
from .register import MobaseRegister

LOGGER = logging.getLogger(__package__)


def magic_split(
    value: str, sep: str = ",", open: str = "(<[", close: str = ")>]"
) -> list[str]:
    """
    Split the value according to the given separator, but keeps together elements
    within the given separator. Useful to split C++ signature function since type names
    can contain special characters...

    Examples:
        - magic_split("a,b,c", sep=",") -> ["a", "b", "c"]
        - magic_split("a<b,c>,d(e,<k,c>),p) -> ["a<b,c>", "d(e,<k,c>)", "p"]

    Args:
        value: String to split.
        sep: Separator to use.
        open: List of opening characters.
        close: List of closing characters. Order must match open.

    Returns: The list of split parts from value.
    """
    i, j = 0, 0
    s: list[int] = []
    r: list[str] = []
    while i < len(value):
        j = i + 1
        while j < len(value):
            c = value[j]

            # Separator found and the stack is empty:
            if c == sep and not s:
                break

            # Check close/open:
            if c in open:
                s.append(open.index(c))
            elif c in close:
                # The stack might be empty if the separator is also an opening element:
                if not s and sep in open and j + 1 == len(value):
                    pass
                else:
                    t = s.pop()
                    if t != close.index(c):
                        raise ValueError(
                            "Found closing element {} for opening element {}.".format(
                                c, open[t]
                            )
                        )
            j += 1
        r.append(value[i:j])
        i = j + 1

    assert not s

    return r


def parse_python_signature(s: str, name: str) -> tuple[PyType, list[Argument]]:
    """
    Parse a pybind11 python signature.

    Args:
        s: The signature to parse.
        name: Name of the function.

    Returns: (RType, Args) where RType is a Type object, and Args is a list of Arg
        objects containing Type.
    """

    m = re.search(rf"{name}\((.*)\)\s*->\s*([^:]+)\s*", s)
    if not m:
        raise ValueError(f"invalid signature: {s}")

    args = magic_split(m.group(1).strip(), ",", open="[", close="]")
    return_type = m.group(2)

    arguments: list[Argument] = []
    for pa in args:
        m = re.search(
            r"(?P<name>[^:]+)\s*:\s*(?P<type>[^=]+)\s*(=\s*(?P<value>[^,]+))?",
            pa.strip(),
        )
        if not m:
            raise ValueError(f"invalid argument: {pa}, {s}")

        matches = m.groupdict()
        type_ = matches["type"]
        if matches["value"] == "None":
            if "None" not in type_ and "MoVariant" not in type_:
                type_ = type_ + " | None"

        arguments.append(Argument(matches["name"], PyType(type_), matches["value"]))

    return PyType(return_type), arguments


def is_enum(e: type) -> bool:
    """Check if the given class is an enumeration.

    Args:
        e: The class object to check.

    Returns: True if the object is an enumeration (boost::python enumeration, not
        python) False otherwise.
    """
    # Yet to find a better way...
    if not isinstance(e, type):
        return False
    return hasattr(e, "__entries")


class Overload:
    """Small class to avoid mypy issues..."""

    return_type: PyType
    arguments: list[Argument]

    def __init__(self, return_type: PyType, arguments: list[Argument]):
        self.return_type = return_type
        self.arguments = arguments


def parse_pybind11_function_docstring(e: type) -> list[Overload]:
    """
    Parse the docstring of the given element.

    Args:
        e: The function to "parse".

    Returns:
        A list of overloads for the given function.
    """
    lines = (e.__doc__ or "").strip().split("\n")

    signatures: list[str]
    if len(lines) == 1:
        signatures = lines
    else:
        signatures = []
        for line in lines:
            m = re.match(rf"^[0-9]+[.]\s+({e.__name__}.*)$", line)
            if m:
                signatures.append(m.group(1).strip())

    # We are going to parse the python and C++ signature, and try to merge
    # them...
    overloads: list[Overload] = []
    for signature in signatures:
        # fix MOBase:: in some places to get proper Python types
        signature = signature.replace("MOBase::", "mobase.").replace("::", ".")

        try:
            return_type, arguments = parse_python_signature(signature, e.__name__)
        except ValueError as err:
            raise ValueError(f"invalid signature: {e.__name__}, {e.__doc__}") from err
        overloads.append(Overload(return_type=return_type, arguments=arguments))

    return overloads


def make_functions(e: type) -> list[Function]:
    overloads = parse_pybind11_function_docstring(e)

    return [
        Function(
            e.__name__,
            Return(overload.return_type),
            overload.arguments,
            has_overloads=len(overloads) > 1,
        )
        for overload in overloads
    ]


def make_class(e: type, register: MobaseRegister) -> Class:
    """
    Constructs a Class object from the given python class.

    Args:
        e: The python class (created from boost) to construct an object for.
        class_register:

    Returns: A Class object corresponding to the given class.
    """

    base_classes_s: list[str] = []

    # Kind of ugly, but...:
    for c in inspect.getmro(e):
        if c != e and c.__module__ == "mobase":
            base_classes_s.append(c.__name__)
        if c.__module__ == "pybind11_builtins":
            break

    first_base = inspect.getmro(e)[1]

    # This contains ALL the parent classes, not the direct ones:
    base_classes: list[Class] = [
        register.make_object(name)
        for name in base_classes_s  # type: ignore
    ]

    # retrieve all the attributes that are not in a base class
    all_attrs = [
        (n, getattr(e, n))
        for n in dir(e)
        if not hasattr(first_base, n) or getattr(first_base, n) is not getattr(e, n)
    ]

    # members to exclude
    EXCLUDED_MEMBERS = [
        "__init_subclass__",
        "__module__",
        "__subclasshook__",
        "__hash__",
        "__getstate__",
        "__setstate__",
        "__index__",
        "__repr__",
    ]
    all_attrs = [a for a in all_attrs if a[0] not in EXCLUDED_MEMBERS]

    # fetch all attributes from the base classes
    base_attrs: dict[str, list[Constant | Property | Method | Class]] = defaultdict(
        list
    )
    for bc in base_classes:
        for a in cast(
            Iterable[Constant | Property | Method | Class],
            chain(bc.constants, bc.methods, bc.properties, bc.inner_classes),
        ):
            base_attrs[a.name].append(a)

    # retrieve the enumerations and classes
    inner_classes = [ic[1] for ic in all_attrs if isinstance(ic[1], type)]

    pinner_classes: list[Class] = [
        cast(Class, register.make_object(f"{e.__qualname__}.{ic.__name__}", ic))
        for ic in inner_classes
    ]

    # find the methods
    raw_methods = [
        m[1] for m in all_attrs if callable(m[1]) and m[1] not in inner_classes
    ]
    raw_methods = sorted(raw_methods, key=lambda m: str(m.__name__))
    raw_methods = [m for m in raw_methods if m.__doc__ is not None]

    # remove __init__
    raw_methods = [
        m for m in raw_methods if not isinstance(m, types.WrapperDescriptorType)
    ]

    methods: list[Method] = []
    for method in raw_methods:
        if method.__doc__ is None:
            continue

        # __eq__ must accept an object in python (and it does with pybind11), so we
        # force the overload
        if method.__name__ in ["__eq__", "__ne__"]:
            overloads = [
                Overload(
                    return_type=PyType("bool"),
                    arguments=[
                        Argument("self", PyType(e.__module__ + "." + e.__qualname__)),
                        Argument("other", PyType("object")),
                    ],
                )
            ]

        # otherwise we parse the docstring
        else:
            overloads = parse_pybind11_function_docstring(method)

        for overload in overloads:
            args = overload.arguments

            # pybind11 seems to be consistent with the naming of "self", so we can
            # mostly rely on it
            static = len(args) == 0 or args[0].name != "self"

            # we need to fix some default values (basically default values that
            # comes from inner enum) and argument
            for arg in overload.arguments:
                if arg.has_default_value():
                    value: str = arg.value  # type: ignore
                    base_name = value.split(".")[0]

                    for base_class in base_classes:
                        for biclass in base_class.inner_classes:
                            if isinstance(biclass, Enum) and biclass.name == base_name:
                                arg._value = (  # pyright: ignore[reportPrivateUsage]
                                    base_class.name + "." + value
                                )

            methods.append(
                Method(
                    method.__name__,
                    Return(overload.return_type),
                    overload.arguments,
                    static=static,
                    has_overloads=len(overloads) > 1,
                )
            )

    # Retrieve the attributes:
    constants: list[Constant] = []
    properties: list[Property] = []
    for name, attr in all_attrs:
        if callable(attr) or isinstance(attr, type):
            continue

        # Maybe we should check an override here (e.g., different value for a constant):
        if name in base_attrs:
            continue

        if isinstance(attr, property):
            properties.append(Property(name, PyType("Any"), attr.fset is None))
        elif not hasattr(attr, "__name__"):
            constants.append(Constant(name, PyType(type(attr).__name__), attr))

    direct_bases: list[Class] = []
    for c in e.__bases__:
        if c.__module__ != "pybind11_builtins":
            b = register.get_object(c.__name__)
            assert isinstance(b, Class)
            direct_bases.append(b)

    # Forcing QWidget base for XWidget classes since these do not show up
    # and we use a trick:
    if e.__name__.endswith("Widget"):
        LOGGER.info(
            "Forcing base {} for class {}.".format(
                "PyQt6.QtWidgets.QWidget", e.__name__
            )
        )
        direct_bases.append(PyClass("PyQt6.QtWidgets", "QWidget"))

    # check if it an enum
    if is_enum(e):
        # all pybind11 enums have a .__entries attribute
        values = cast(dict[str, tuple[int, Any]], e.__entries)  # type: ignore

        # drop the __init__
        methods = [m for m in methods if m.name != "__init__"]

        return Enum(
            e.__module__,
            e.__name__,
            OrderedDict((name, value) for name, (value, _) in values.items()),
            methods=methods,
        )

    return Class(
        e.__module__,
        e.__name__,
        direct_bases,
        methods,
        inner_classes=pinner_classes,
        properties=properties,
        constants=constants,
    )
