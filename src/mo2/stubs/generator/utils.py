# -*- encoding: utf-8 -*-

from __future__ import annotations

from collections import OrderedDict, defaultdict
from typing import TYPE_CHECKING, Final, NamedTuple, TextIO, TypedDict

import yaml

from . import LOGGER
from .mtypes import (
    Argument,
    Class,
    Constant,
    Enum,
    Exception,
    Function,
    Method,
    Property,
    PyClass,
    PyType,
    Return,
)

if TYPE_CHECKING:
    from .register import MobaseRegister


class Settings:
    class YamlFunctionArgument(TypedDict, total=False):
        __doc__: str
        type: str
        desc: str

    class YamlFunctionReturn(TypedDict, total=False):
        __doc__: str
        type: str

    class YamlFunctionSettings(TypedDict, total=False):
        __doc__: str
        abstract: bool
        deprecated: bool

        args: dict[str, Settings.YamlFunctionArgument | str | None]
        returns: str | Settings.YamlFunctionReturn

        raises: dict[str, str]

    class YamlClassProperty(TypedDict):
        type: str
        desc: str

    YamlClassSettings = TypedDict(
        "YamlClassSettings",
        {
            "__doc__": str,
            "__bases__": list[str],
            "__abstract__": bool,
            "properties[]": dict[str, YamlClassProperty],
            "signals[]": dict[str, YamlFunctionSettings],
        },
        total=False,
    )

    class PyFunctionSettings(NamedTuple):

        doc: str
        args: list[Argument] | None = None
        ret: Return | None = None
        raises: list[Exception] = []
        abstract: bool | None = None
        deprecated: bool = False

    register: MobaseRegister

    version: Final[str]

    # Name to ignore:
    _ignore_names: list[str]

    # Extra replacements (with warnings):
    _replacements: dict[str, str]

    # Content of mobase:
    _module: dict[str, dict[str, object]]

    def __init__(
        self,
        register: MobaseRegister,
        fp: TextIO | None = None,
        module: str | None = None,
    ):

        self.register = register

        if fp is None:
            self._ignore_names = []
            self._replacements = {}
            self._version = ""
            self._module = {}
        else:
            data = yaml.load(fp, yaml.FullLoader)
            assert data["version"] == 2, "only settings version 2 are supported"

            # retrieve the module version
            self.version = data["__version__"]

            assert module is not None
            self._module = data.get(module, None) or {}

    def _get_class_settings(self, canonical_name: str) -> YamlClassSettings | None:
        """
        Retrieve the settings for the given class.

        Args:
            canonical_name: Canonical name of the class.

        Returns:
            The settings for the corresponding class, or None if the
            settings where not found.
        """
        parts = canonical_name.split(".")
        base: dict[str, object] = dict(self._module)
        for part in parts:
            if part in base:
                base = base[part]  # type: ignore
            else:
                return None
        return base  # type: ignore

    def _parse_function_settings(
        self, settings: str | YamlFunctionSettings
    ) -> "PyFunctionSettings":
        """
        Parse settings for a function or method.

        Args:
            settings: Settings corresponding to a function.

        Returns:
            The parsed settings for the function.
        """
        if settings is None:
            return Settings.PyFunctionSettings("")

        if isinstance(settings, str):
            return Settings.PyFunctionSettings(settings)

        doc = settings.get("__doc__", "")
        # static = settings.get("static", None)
        abstract = settings.get("abstract", None)
        deprecated = settings.get("deprecated", False)

        # Arguments:
        args: list[Argument] | None = None

        # If "args" is in settings, it can either be None (args: ) or
        # a list of args:
        if "args" in settings:
            args = []
            if settings["args"] is not None:

                # For each argument, we either have a None value (name: ),
                # or a string (name: Description) or a dictionary that can contain
                # __doc__ and type.
                for name, value in settings["args"].items():
                    t: PyType = PyType("None")
                    d: str = ""
                    if value is None:
                        pass
                    elif isinstance(value, str):
                        d = value
                    else:
                        d = value.get("__doc__", "")
                        t = PyType(value.get("type", "None"))
                    args.append(Argument(name, t, doc=d))

        ret: Return | None = None
        if "returns" in settings and settings["returns"] is not None:
            if isinstance(settings["returns"], str):
                ret = Return(PyType("None"), settings["returns"])
            else:
                ret = Return(
                    PyType(settings["returns"].get("type", "None")),
                    settings["returns"].get("__doc__", ""),
                )

        exceptions: list[Exception] = []
        if "raises" in settings and settings["raises"] is not None:
            for r, v in settings["raises"].items():
                if v is None:
                    v = ""
                exceptions.append(Exception(PyType(r), v))

        return Settings.PyFunctionSettings(
            doc, args, ret, exceptions, abstract, deprecated
        )

    def patch_functions(self, fns: list[Function]):
        for i, fn in enumerate(fns):

            # Find the name in settings:
            if fn.has_overloads():
                setting_name = "{}.{}".format(fn.name, i + 1)
            else:
                setting_name = fn.name

            # If the name is in the settings:
            if setting_name in self._module:
                function_settings = self._parse_function_settings(
                    self._module[setting_name]  # type: ignore
                )

                # Force raises:
                fn.raises = function_settings.raises

                # Check the args:
                if function_settings.args is not None:
                    if len(function_settings.args) != len(fn.args):
                        LOGGER.warn(
                            f"Mismatch number of arguments for function "
                            f"mobase.{setting_name}."
                        )

                    for setting_arg, method_arg in zip(function_settings.args, fn.args):
                        method_arg.doc = setting_arg.doc
                        if not setting_arg.type.is_none():
                            method_arg.type = setting_arg.type

                # Check the return type:
                if function_settings.ret is not None:

                    # Force the doc anyway:
                    fn.ret.doc = function_settings.ret.doc

                    # Update the type if specified:
                    if not function_settings.ret.type.is_none():
                        fn.ret.type = function_settings.ret.type

                # Force the doc:
                fn.doc = function_settings.doc

                # Force depreciation:
                fn.deprecated = function_settings.deprecated

            else:
                LOGGER.warn(
                    "Missing settings for function mobase.{}.".format(setting_name)
                )

    def patch_class(self, cls: Class):
        """
        Patch the given class using the given overwrites.

        See config.json for some examples of valid overwrites.

        Args:
            cls: The class to patch.
            settings: The settings.
        """

        LOGGER.info("Patching class {}.".format(cls.name))

        # fix the name
        if cls.name == "IPluginBase":
            cls.name = "IPlugin"

        # Find the class in mobase:
        class_settings = self._get_class_settings(cls.canonical_name)

        if class_settings is None:
            LOGGER.warn("Class {} not found in settings.".format(cls.canonical_name))
            return

        if "__doc__" in class_settings and class_settings["__doc__"] is not None:
            cls.doc = class_settings["__doc__"]
        class_settings.pop("__doc__", None)

        # Check bases:
        if "__bases__" in class_settings:
            for bc in class_settings["__bases__"]:
                if bc.startswith("PyQt"):
                    parts = bc.split(".")
                    cls.bases.append(
                        PyClass(package=".".join(parts[:-1]), name=parts[-1])
                    )
                else:
                    cls.bases.append(self.register.get_object(bc))
            del class_settings["__bases__"]

        if "__abstract__" in class_settings and class_settings["__abstract__"]:
            cls.abstract = True
            del class_settings["__abstract__"]

        # Patch properties - Everything should be in config since property are poorly
        # documented by boost::python.
        properties: dict[str, Settings.YamlClassProperty] = class_settings.pop(
            "properties[]", {}
        )
        for prop in cls.properties:
            if prop.name in properties:
                settings_property = properties[prop.name]

                # If we have a type:
                if "type" in settings_property:
                    prop.type = PyType(settings_property["type"])
                else:
                    LOGGER.warn(
                        "Missing type for property {}.{}.".format(
                            cls.canonical_name, prop.name
                        )
                    )

                # If we have a description:
                if "desc" in settings_property:

                    # If desc is None, we do not warn user, because the entry is in
                    # settings, just empty:
                    if settings_property["desc"] is not None:
                        prop.doc = settings_property["desc"]

                else:
                    LOGGER.warn(
                        "Missing description for property {}.{}.".format(
                            cls.canonical_name, prop.name
                        )
                    )

        # patch signals - Everything should be in config since signals are not really
        # exposed by pybind11.
        signals: list[str] = list(class_settings.pop("signals[]", {}))
        for signal in signals:
            cls.constants.append(Constant(signal, PyType("pyqtSignal"), None))

        # List of all items in class_settings:
        keys = {k: False for k in class_settings}

        # Group method by name:
        methods: dict[str, list[Method]] = defaultdict(list)
        for m in cls.methods:
            methods[m.name].append(m)

        for k, ms in methods.items():
            for i, m in enumerate(ms):

                # Find the name in settings:
                if m.has_overloads():
                    settings_name = "{}.{}".format(m.name, i + 1)
                else:
                    settings_name = m.name

                missing_settings: set[str] = set()

                # If the name is in the settings:
                if settings_name in class_settings:
                    keys[settings_name] = True
                    function_settings = self._parse_function_settings(
                        class_settings[settings_name]  # type: ignore
                    )

                    # Force raises:
                    m.raises = function_settings.raises

                    if function_settings.abstract is not None:
                        m.abstract = function_settings.abstract

                    # Check the args:
                    if function_settings.args is not None:
                        method_arguments = m.args if m.is_static() else m.args[1:]
                        if len(function_settings.args) != len(method_arguments):
                            LOGGER.warn(
                                "Mismatch number of arguments for method {}.{}.".format(
                                    cls.canonical_name, settings_name
                                )
                            )

                        for settings_arg, method_arg in zip(
                            function_settings.args, method_arguments
                        ):
                            method_arg.doc = settings_arg.doc
                            if (
                                not method_arg.name.startswith("arg")
                                and method_arg.name != settings_arg.name
                            ):
                                LOGGER.warn(
                                    (
                                        "Mismatch argument name for method {}.{}: "
                                        "{} {}, using {}."
                                    ).format(
                                        cls.canonical_name,
                                        settings_name,
                                        method_arg.name,
                                        settings_arg.name,
                                        settings_arg.name,
                                    )
                                )

                            method_arg.name = settings_arg.name
                            if not settings_arg.type.is_none():
                                method_arg.type = settings_arg.type

                    # Check the return type:
                    if function_settings.ret is not None:

                        # Force the doc anyway:
                        m.ret.doc = function_settings.ret.doc

                        # Update the type if specified:
                        if not function_settings.ret.type.is_none():
                            m.ret.type = function_settings.ret.type

                    # Force the doc:
                    m.doc = function_settings.doc

                    # Force deprecated:
                    m.deprecated = function_settings.deprecated

                # Only warn for "normal" methods:
                elif not m.name.startswith("__"):
                    missing_settings.add(settings_name)

            # remove the deprecated methods and count overloads
            n_overloads = 0
            for m in ms:
                if m.is_deprecated():
                    cls.methods.remove(m)
                else:
                    n_overloads += 1

            for m in ms:
                m.overloads = n_overloads > 1

            if n_overloads > 0 and missing_settings:
                for settings_name in missing_settings:
                    LOGGER.warn(
                        "Missing settings for method {}.{}.".format(
                            cls.canonical_name, settings_name
                        )
                    )

        # Patch inner classes:
        for ic in cls.inner_classes:
            keys[ic.name] = True
            self.patch_class(ic)

        # Mark the constant:
        for cc in cls.constants:
            keys[cc.name] = True

        # Print items missing in mobase
        missing_items = [k for k, v in keys.items() if not v]
        if missing_items:
            LOGGER.warn(
                "The following members were found in settings but not in the actual"
                " class {}: {}.".format(cls.canonical_name, ", ".join(missing_items))
            )


def clean_class(cls: Class):
    """
    Clean the given class object.

    Args:
        cls: The class object to clean.
    """

    # Remove duplicate methods (based on name and argument types):
    methods: dict[tuple[str, tuple[Argument, ...]], list[Method]] = OrderedDict()
    methods_by_name = defaultdict(list)
    for m in cls.methods:
        k = (m.name, tuple(m.args if m.is_static() else m.args[1:]))
        if k not in methods:
            methods[k] = []
        methods[k].append(m)
        methods_by_name[m.name].append(m)

    clean_methods: list[Method] = []
    for name, args in methods:
        ms = methods[name, args]
        method: Method = ms[0]
        if len(ms) > 1:

            # If we have more than two methods, there is a problem...
            assert len(methods[name, args]) == 2
            assert (
                ms[0].ret.type.is_none()
                or ms[1].ret.type.is_none()
                or ms[0].ret.type.name == ms[1].ret.type.name
            )

            if ms[0].ret.type.is_none():
                # If both are None, we need to take the first one because the second
                # one does not contains the name of the arguments, for whatever reason.
                if ms[1].ret.type.is_none():
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
            # print(arg0_name, [cls.name, cls.canonical_name, cls.full_name, "object"])
            if arg0_name in [cls.full_name, "object"]:
                clean_methods.append(method)
            else:
                LOGGER.info(
                    "Removing {}({}) from {} (already in base {}).".format(
                        name,
                        ", ".join(a.type.typing() for a in method.args),
                        cls.name,
                        method.args[0].type.typing(),
                    )
                )

            if method.name != "__init__":
                # we need to fix the overload from the base class
                for base_class in cls.all_bases:
                    for base_method in base_class.methods:
                        if base_method.name == method.name:
                            # we need to bring all overloads
                            base_method = Method(
                                base_method.name,
                                ret=base_method.ret,
                                args=base_method.args,
                                static=False,
                                has_overloads=True,
                                doc=base_method.doc,
                            )
                            base_method.cls = cls
                            clean_methods.insert(-1, base_method)

                            method.overloads = True

    cls.methods = clean_methods

    # Remove all non-uppercases enum names - This is a temporary fix to avoid breaking
    # old plugins that uses old enum values:
    if isinstance(cls, Enum):
        new_constants = [c for c in cls.constants if c.name.isupper()]
        if new_constants:
            cls.constants = new_constants

        # pybind11 do not properly type arithmetic methods so we fix them here, so we
        # replace every "object" to the type when possible

        cls_type = PyType(cls.canonical_name)
        for method in cls.methods:
            if method.name in ["__eq__", "__ne__"]:
                continue

            for arg in method.args:
                if arg.type.is_object():
                    arg.type = cls_type

            if method.ret.type.is_object():
                method.ret.type = cls_type

        # add two properties name, value
        cls.properties = [
            Property("value", PyType(int), read_only=True),
            Property("name", PyType(str), read_only=True),
        ]

    # Clean inner classes:
    for ic in cls.inner_classes:
        clean_class(ic)
