# -*- encoding: utf-8 -*-

import inspect
import re

from collections import defaultdict, OrderedDict

from typing import List, Tuple, Optional, Dict, Union

from .register import MobaseRegister
from .mtypes import (
    Type,
    CType,
    Class,
    PyClass,
    Enum,
    Arg,
    Ret,
    Method,
    Constant,
    Property,
    Function,
)
from . import logger


def magic_split(value: str, sep=",", open="(<", close=")>"):
    """Split the value according to the given separator, but keeps together elements
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
    s: List[str] = []
    r = []
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

    return r


def parse_ctype(s: str) -> CType:
    """Parse a C++ type from the given string.

    Args:
        s: String to parse.

    Returns: A C++ type parsed from the given string.
    """

    # List of strings that can be removed from the names:
    for d in [
        "__64",
        "__cdecl",
        "__ptr64",
        "{lvalue}",
        "class",
        "struct",
        "enum",
        "unsigned",
    ]:
        s = s.replace(d, "")

    # Remove the namespace remaing:
    for d in ["MOBase", "boost::python"]:
        s = s.replace(d + "::", "")

    # Specific replacement:
    s = s.replace("__int64", "int")
    s = s.replace(" const &", "")
    s = s.replace("&", "")

    return CType(s.strip())


def parse_carg(s: str, has_default: bool) -> Arg:
    """Parse the given C++ argument.

    Args:
        s: The string to parse.
        has_default: Indicates if this argument as a default.

    Returns: An argument parsed from the given string.
    """
    v, d = s, None
    if s.find("=") != -1:
        v, d = [x.strip() for x in s.split("=")]

    if d is None and has_default:
        d = Arg.DEFAULT_NONE

    return Arg("", parse_ctype(v), d)


def parse_csig(s, name) -> Tuple[CType, List[Arg]]:
    """Parse a boost::python C++ signature.

    Args:
        s: The signature to parse.
        name: Name of the function, or "" if the signature correspond to a type.

    Returns: (RType, Args) where RType is a CType object, and Args is a list of Arg
        objects containing CType.
    """
    # Remove the [ and ] which specifies default arguments but are useless since
    # we already have = to tell us - The replacement is weird because the way boost
    # present these is weird, and to avoid breaking default argument such as = []:
    c = s.count("[,")
    s = s.replace("[,", ",")
    s = s.replace("]" * c, "")

    # Split return type/arguments:
    if name:
        rtype_s, args_s = s.split(name)

        # Remove the ( and ).
        args_s = args_s.strip()[1:-1]
    else:
        rtype_s, args_s = magic_split(s, "(", "(<", ")>")

        # Only remove the last ) because the first one is removed by magic_split:
        args_s = args_s.strip()[:-1]

    # Parse return type:
    rtype = parse_ctype(rtype_s.strip())

    # Parse arguments:

    # Strip spaces and remove the first and last ():
    args_s = args_s.strip()
    args_ss = magic_split(args_s, ",", "(<", ")>")
    args = [parse_carg(v, i > len(args_ss) - c - 1) for i, v in enumerate(args_ss)]

    return rtype, args


def parse_psig(s: str, name: str) -> Tuple[Type, List[Arg]]:
    """Parse a boost::python python signature.

    Args:
        s: The signature to parse.
        name: Name of the function.

    Returns: (RType, Args) where RType is a Type object, and Args is a list of Arg
        objects containing Type.
    """

    c = s.count("[,")
    s = s.replace("[,", ",")
    s = s.replace("]" * c, "")

    # This is pretty brutal way of extracting stuff... But most things can be
    # retrieve from the C++ signature, here we are mainly interested in extracting
    # the python type if possible:
    m: re.Match[str] = re.search(
        r"{}\((.*)\)\s*->\s*([^\s]+)\s*:".format(name), s
    )  # type: ignore
    pargs = []
    args = list(filter(bool, m.group(1).strip().split(",")))
    for i, pa in enumerate(args):
        pa = pa.strip()

        # Index of the right bracket:
        irbrack = pa.find(")")

        # The type is within the brackets:
        t = pa[1:irbrack]

        pa = pa[irbrack + 1 :]
        n: str = pa.strip()
        d: Optional[str] = None
        if pa.find("=") != -1:
            n, d = pa.split("=")
            n = n.strip()
            d = d.strip()
        elif i > len(args) - c - 1:
            d = Arg.DEFAULT_NONE
        pargs.append(Arg(n, Type(t), d))
    return Type(m.group(2)), pargs


def find_best_argname(iarg: int, pname: str, cname: str):
    """Find the best name for the ith argument of a function.

    Args:
        iarg: Index of the argument, use for default.
        pname: Name of the argument in the python signature.
        cname: Name of the argument in the C++ signature.

    Returns:
        The best name for the corresponding argument.
    """
    if not cname and not pname:
        return "arg{}".format(iarg + 1)

    return pname


def find_best_type(ptype: Type, ctype: CType) -> Type:
    """Find the best type from the given python and C++ type.


    Args:
        ptype: The python type.
        ctype: The C++ type.

    Returns: The best of the two types.
    """
    from .register import MOBASE_REGISTER

    if ptype.name == ctype.name:
        return ptype
    elif ptype.is_none() and ctype.is_none():
        return ptype

    assert ptype.is_none() == ctype.is_none()

    MOBASE_REGISTER.register_type(ptype, ctype)

    if ptype.is_object():
        if ctype.is_object():
            return ptype
        return ctype

    # Returned pointer are treated differently because they can often be null:
    if ctype.is_pointer():
        return ctype

    return ptype


def find_best_value(pvalue: str, cvalue: str) -> str:
    """Find the best value (default value) from the given python and C++ one.

    WARNING: This currently always return pvalue and only warns the user if
    the two values are not identical.

    Args:
        pvalue: Python default value.
        cvalue: C++ default value.

    Returns: The best of the two values.
    """
    if pvalue != cvalue:
        logger.warning("Mismatch default value: {} {}.".format(pvalue, cvalue))
    return pvalue


def is_enum(e: type) -> bool:
    """Check if the given class is an enumeration.

    Args:
        e: The class object to check.

    Returns: True if the object is an enumeration (boost::python enumeration, not
        python) False otherwize.
    """
    # Yet to find a better way...
    if not isinstance(e, type):
        return False
    return any(
        "{}.{}".format(c.__module__, c.__name__) == "Boost.Python.enum"
        for c in inspect.getmro(e)
    )


def make_enum(fullname: str, e: type) -> Enum:
    """Construct a Enum object from the given class.

    Args:
        fullname: Fully qualified name of the enumeration.
        e: The class representing a boost::python enumeration.

    Returns: An Enum object representing the given enumeration.
    """
    # All boost enums have a .values attributes:
    values = e.values  # type: ignore

    return Enum(
        e.__name__, OrderedDict((values[k].name, k) for k in sorted(values.keys())),
    )


class Overload:

    """ Small class to avoid mypy issues... """

    rtype: Type
    args: List[Arg]

    def __init__(self, rtype, args):
        self.rtype = rtype
        self.args = args


def parse_bpy_function_docstring(e) -> List[Overload]:
    """Parse the docstring of the given element.

    Args:
        e: The function to "parse".

    Returns: A list of overloads for the given function, where each overload is
        a dictionary with a "rtype" entry containing the return type and a "args"
        entry containing the list of arguments.
    """
    lines = e.__doc__.split("\n")

    # Find the various overloads:
    so = [i for i, line in enumerate(lines) if line.strip().startswith(e.__name__)]
    so.append(len(lines))

    # We are going to parse the python and C++ signature, and try to merge
    # them...
    overloads: List[Overload] = []
    for i, j in zip(so[:-1], so[1:]):

        psig = lines[i].strip()
        for k in range(i, j):
            if lines[k].strip().startswith("C++ signature"):
                csig = lines[k + 1].strip()

        prtype, pargs = parse_psig(psig, e.__name__)
        crtype, cargs = parse_csig(csig, e.__name__)

        # Currently there is no way to automatically check so we add [optional]
        # in the doc:
        if e.__doc__.find("[optional]") != -1:
            crtype._optional = True

        assert len(pargs) == len(cargs)

        # Now we need to find the "best" type from both signatures:
        rtype = find_best_type(prtype, crtype)
        args = []
        for iarg, (parg, carg) in enumerate(zip(pargs, cargs)):
            args.append(
                Arg(
                    find_best_argname(iarg, parg.name, carg.name),
                    find_best_type(parg.type, carg.type),  # type: ignore
                    find_best_value(parg.value, carg.value),  # type: ignore
                )
            )  # type: ignore

        overloads.append(Overload(rtype=rtype, args=args))

    return overloads


def make_functions(name: str, e) -> List[Function]:
    overloads = parse_bpy_function_docstring(e)

    return [
        Function(
            e.__name__, Ret(ovld.rtype), ovld.args, has_overloads=len(overloads) > 1,
        )
        for ovld in overloads
    ]


def make_class(fullname: str, e: type, register: MobaseRegister) -> Class:
    """Constructs a Class objecgt from the given python class.

    Args:
        fullname: Name of the class (might be different from __name__ for inner
            classes).
        e: The python class (created from boost) to construct an object for.
        class_register:

    Returns: A Class object corresponding to the given class.
    """

    base_classes_s: List[str] = []

    # Kind of ugly, but...:
    for c in inspect.getmro(e):
        if c != e and c.__module__ == "mobase":
            base_classes_s.append(c.__name__)
        if c.__module__ == "Boost.Python":
            break

    # Keep as a comment but this is/should be fixed in the actual C++ code:
    # Lots of class exposed do not inherit IPlugin while they should:
    # if "IPlugin" not in base_classes_s and e.__name__.startswith("IPlugin") \
    #   and e.__name__ != "IPlugin":
    #     base_classes_s.append("IPlugin")

    # This contains ALL the parent classes, not the direct ones:
    base_classes: List[Class] = [
        register.make_object(name) for name in base_classes_s  # type: ignore
    ]

    # Retrieve all the attributes... The hasattr is required but I don't know why:
    all_attrs = [(n, getattr(e, n)) for n in dir(e) if hasattr(e, n)]

    # Some exclusions:
    EXCLUDED_MEMBERS = [
        "__weakref__",
        "__dict__",
        "__doc__",
        "__instance_size__",
        "__module__",
        "__getattr__",
    ]
    all_attrs = [
        a
        for a in all_attrs
        # Using getattr() here since some attribute do not have name (e.g. constants):
        if a[0] not in EXCLUDED_MEMBERS
    ]

    # Fetch all attributes from the base classes:
    base_attrs: Dict[str, List[Union[Constant, Property, Method, Class]]] = defaultdict(
        list
    )
    for bc in base_classes:
        # Thanks mypy for the naming...
        for a1 in bc.constants:
            base_attrs[a1.name].append(a1)
        for a2 in bc.methods:
            base_attrs[a2.name].append(a2)
        for a3 in bc.properties:
            base_attrs[a3.name].append(a3)
        for a4 in bc.inner_classes:
            base_attrs[a4.name].append(a4)

    # Retrieve the enumerations and classes:
    inner_classes = [
        ic[1]
        for ic in all_attrs
        if isinstance(ic[1], type)
        and ic[1].__name__ != "class"
        and ic[0] not in base_attrs
    ]

    pinner_classes: List[Class] = [
        register.make_object("{}.{}".format(fullname, ic.__name__), ic)  # type: ignore
        for ic in inner_classes
    ]

    # Find the methods:
    methods = [m[1] for m in all_attrs if callable(m[1])]
    methods = sorted(methods, key=lambda m: m.__name__)

    # Filter out methods not provided or implemented:
    methods = [
        m
        for m in methods
        if m.__doc__ is not None and m.__doc__.find("C++ signature") != -1
    ]

    # List of methods that must return bool:
    BOOL_METHODS = ["__eq__", "__lt__", "__le__", "__ne__", "__gt__", "__ge__"]

    pmethods = []
    for method in methods:
        if method.__doc__ is None:
            continue
        overloads = parse_bpy_function_docstring(method)

        # __eq__ must accept an object in python, so we need to add an overload:
        if method.__name__ in ["__eq__", "__ne__"]:
            overloads.append(
                Overload(
                    rtype=Type("bool"),
                    args=[Arg("", Type(e.__name__)), Arg("other", Type("object"))],
                )
            )

        cmethods = []
        for ovld in overloads:
            args = ovld.args

            # This is a very heuristic way of checking if the method is static but I did
            # not find anything better yet...
            static = False
            if len(args) == 0:
                static = True
            elif method.__name__.startswith("__"):  # Special method cannot be static
                static = False
            else:
                arg0_name = args[0].type.name
                if arg0_name in register.cpp2py:
                    arg0_name = register.cpp2py[arg0_name].name
                arg0_name = (
                    arg0_name.replace("*", "")
                    .replace("&", "")
                    .replace("const", "")
                    .strip()
                )

                static = (
                    arg0_name
                    not in [e.__name__, e.__name__ + "Wrapper"] + base_classes_s
                )

            # We need to fix some default values (basically default values that
            # comes from inner enum):
            for arg in ovld.args:
                if arg.has_default_value():
                    value: str = arg.value  # type: ignore
                    bname = value.split(".")[0]
                    for bclass in base_classes:
                        for biclass in bclass.inner_classes:
                            if isinstance(biclass, Enum) and biclass.name == bname:
                                arg._value = bclass.name + "." + value

            pmethod = Method(
                method.__name__,
                Ret(ovld.rtype),
                ovld.args,
                static=static,
                has_overloads=len(overloads) > 1,
            )

            if method.__name__ in BOOL_METHODS:
                pmethod.ret = Ret(Type("bool"))

            cmethods.append(pmethod)

        pmethods.extend(cmethods)

    # Retrieve the attributes:
    constants = []
    properties = []
    for name, attr in all_attrs:
        if callable(attr) or isinstance(attr, type):
            continue

        # Maybe we should check an override here (e.g., different value for a constant):
        if name in base_attrs:
            continue

        if isinstance(attr, property):
            properties.append(Property(name, Type("Any"), attr.fset is None))
        elif not hasattr(attr, "__name__"):
            constants.append(Constant(name, Type(type(attr).__name__), attr))

    direct_bases: List[Class] = []
    for c in e.__bases__:
        if c.__module__ != "Boost.Python":
            direct_bases.append(register.get_object(c.__name__))

    # Forcing QWidget base for XWidget classes since these do not show up
    # and we use a trick:
    if e.__name__.endswith("Widget"):
        logger.info(
            "Forcing base {} for class {}.".format(
                "PyQt5.QtWidgets.QWidget", e.__name__
            )
        )
        direct_bases.append(PyClass("PyQt5.QtWidgets.QWidget"))

    return Class(
        e.__name__,
        direct_bases,
        pmethods,
        inner_classes=pinner_classes,
        properties=properties,
        constants=constants,
    )
