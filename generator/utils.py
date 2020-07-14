# -*- encoding: utf-8 -*-

import json

from collections import OrderedDict, defaultdict
from typing import List, Dict, Any, Tuple

from . import logger
from .mtypes import Class, Enum, Arg, Type, Method, Constant


# This is a 100% static class:
class Settings:

    # Name to ignore:
    IGNORE_NAMES: List[str] = []

    # Extra replacements (with warnings):
    REPLACEMENTS: Dict[str, str] = {}

    # Overwrites:
    OVERWRITES: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def load_from_file(fp):
        data = json.load(fp)
        Settings.IGNORE_NAMES.extend(data.get("ignores", []))
        Settings.REPLACEMENTS.update(data.get("replacements", {}))
        Settings.OVERWRITES.update(data.get("overwrites", {}))

    @staticmethod
    def parse_method(cls: "Class", name: str, config: Dict[str, Any]):
        args = []
        if not config["static"]:
            args.append(Arg("", Type(cls.name)))
        for arg in config["args"]:
            if isinstance(arg, str):
                args.append(Arg("", Type(arg)))
            elif isinstance(arg, dict):
                args.append(Arg("", Type(arg["type"]), arg["default"]))
            else:
                args.append(Arg("", Type(arg[0]), arg[1]))
        return Method(
            cls.name,
            name,
            Type(config["rtype"]),
            args,
            config["static"],
            config["overloads"],
        )  # type: ignore


def clean_class(cls: Class):
    """ Clean the given class object.

    Args:
        cls: The class object to clean.
    """
    from .register import MOBASE_REGISTER

    # Remove duplicate methods (based on name and argument types):
    methods: Dict[Tuple[str, Tuple[Arg, ...]], List[Method]] = OrderedDict()
    methods_by_name = defaultdict(list)
    for m in cls.methods:
        k = (m.name, tuple(m.args[1:]))
        if k not in methods:
            methods[k] = []
        methods[k].append(m)
        methods_by_name[m.name].append(m)

    clean_methods: List[Method] = []
    for name, args in methods:
        ms = methods[name, args]
        method: Method = ms[0]
        if len(ms) > 1:

            # If we have more than two methods, there is a problem...
            assert len(methods[name, args]) == 2
            assert (
                ms[0].rtype.is_none()
                or ms[1].rtype.is_none()
                or ms[0].rtype.name == ms[1].rtype.name
            )

            if ms[0].rtype.is_none():
                # If both are None, we need to take the first one because the second
                # one does not contains the name of the arguments, for whatever reason.
                if ms[1].rtype.is_none():
                    method = ms[0]
                else:
                    method = ms[1]
            else:
                method = ms[0]

            # If those were the only two, we need to remove the overload:
            if len(methods_by_name[name]) == 2:
                method.overloads = False

        # Filter methods from parent class:
        if method.is_static():
            clean_methods.append(method)
        else:
            arg0_name = method.args[0].type.name
            if arg0_name in MOBASE_REGISTER.cpp2py:
                arg0_name = MOBASE_REGISTER.cpp2py[arg0_name].name
            if arg0_name in [cls.name, "object"]:
                clean_methods.append(method)
            else:
                logger.info(
                    "Removing {}({}) from {} (already in base {}).".format(
                        name,
                        ", ".join(a.type.typing() for a in args),
                        cls.name,
                        method.args[0].type.typing(),
                    )
                )

    # We need to filter-out __eq__(X, object) and __ne__(X, object) because these won't
    # be filtered since the first arg is not of the right type:
    for name in ("__eq__", "__ne__"):
        fns = [m for m in clean_methods if m.name == name]
        if len(fns) == 1 and fns[0].args[1].type.is_object():
            clean_methods.remove(fns[0])

    cls.methods = clean_methods

    # Remove all non-uppercases enum names - This is a temporary fix to avoid breaking
    # old plugins that uses old enum values:
    if isinstance(cls, Enum):
        newc = [c for c in cls.constants if c.name.isupper()]
        if newc:
            cls.constants = newc

    # Clean inner classes:
    for ic in cls.inner_classes:
        clean_class(ic)


def patch_class(cls: Class, overwrites: Dict[str, Dict[str, Any]]):
    """ Patch the given class using the given overwrites.

    See config.json for some examples of valid overwrites.

    Args:
        cls: The class to patch.
        overwrites: The overwrite dictionary.
    """

    logger.info("Patching class {}.".format(cls.name))

    if cls.canonical_name in overwrites:

        ow = overwrites[cls.canonical_name]

        if "[bases]" in ow:
            cls.bases = ow["[bases]"]

        methods = []
        for m in cls.methods:
            if m.name in ow:
                if not ow[m.name]:
                    continue
                m = Settings.parse_method(cls, m.name, ow[m.name])
            methods.append(m)
        cls.methods = methods

        properties: Dict[str, str] = ow.get("[properties]", {})
        for prop in cls.properties:
            if prop.name in properties:
                prop.type = Type(properties[prop.name])

        signals: List[str] = ow.get("[signals]", [])
        for signal in signals:
            name = signal.split("[")[0]
            cls.constants.append(
                Constant(name, Type("pyqtSignal"), None, comment=signal)
            )

    # Patch inner classes:
    for ic in cls.inner_classes:
        patch_class(ic, overwrites)
