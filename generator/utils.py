# -*- encoding: utf-8 -*-

from collections import OrderedDict, defaultdict
from typing import List, Dict, Any, Tuple, TextIO, Optional, Union, NamedTuple, Set

from . import logger
from . import register
from . import mtypes

import yaml


class Settings:
    class FunctionSettings(NamedTuple):

        doc: str
        args: Optional[List["mtypes.Arg"]] = None
        ret: Optional["mtypes.Ret"] = None
        raises: List["mtypes.Exc"] = []
        static: Optional[bool] = None
        abstract: Optional[bool] = None
        deprecated: bool = False

    register: "register.MobaseRegister"

    # Name to ignore:
    _ignore_names: List[str]

    # Extra replacements (with warnings):
    _replacements: Dict[str, str]

    # Content of mobase:
    _mobase: Dict[str, Dict[str, Any]]

    def __init__(
        self, register: "register.MobaseRegister", fp: Optional[TextIO] = None
    ):

        self.register = register

        if fp is None:
            self._ignore_names = []
            self._replacements = {}
            self._mobase = {}
        else:
            data = yaml.load(fp, yaml.FullLoader)
            assert data["version"] == 1

            self._ignore_names = data.get("ignores", [])
            self._replacements = data.get("replacements", {})
            self._mobase = data.get("mobase", {})

    @property
    def ignore_names(self) -> List[str]:
        return self._ignore_names

    @property
    def replacements(self) -> Dict[str, str]:
        return self._replacements

    @property
    def mobase(self) -> Dict[str, Dict[str, Any]]:
        return self._mobase

    def _get_class_settings(self, canonical_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve the settings for the given class.

        Args:
            canonical_name: Canonical name of the class.

        Returns:
            The settings for the corresponding class, or None if the
            settings where not found.
        """
        parts = canonical_name.split(".")
        base: Dict[str, Any] = self._mobase
        for part in parts:
            if part in base:
                base = base[part]
            else:
                return None
        return base

    def _parse_function_settings(
        self, settings: Union[str, Dict[str, Any]]
    ) -> "FunctionSettings":
        """Parse settings for a function or method.

        Args:
            settings: Settings corresponding to a function.

        Returns:
            The parsed settings for the function.
        """
        FunctionSettings = Settings.FunctionSettings

        if settings is None:
            return FunctionSettings("")

        if isinstance(settings, str):
            return FunctionSettings(settings)

        doc = settings.get("__doc__", "")
        static = settings.get("static", None)
        abstract = settings.get("abstract", None)
        deprecated = settings.get("deprecated", False)

        # Arguments:
        args: Optional[List[mtypes.Arg]] = None

        # If "args" is in settings, it can either be None (args: ) or
        # a list of args:
        if "args" in settings:
            args = []
            if settings["args"] is not None:

                # For each argument, we either have a None value (name: ),
                # or a string (name: Description) or a dictionary that can contain
                # __doc__ and type.
                for aname, avalue in settings["args"].items():
                    t: mtypes.Type = mtypes.Type("None")
                    d: str = ""
                    if avalue is None:
                        pass
                    elif isinstance(avalue, str):
                        d = avalue
                    else:
                        d = avalue.get("__doc__", "")
                        t = mtypes.Type(avalue.get("type", "None"))
                    args.append(mtypes.Arg(aname, t, doc=d))

        ret: Optional[mtypes.Ret] = None
        if "returns" in settings and settings["returns"] is not None:
            if isinstance(settings["returns"], str):
                ret = mtypes.Ret(mtypes.Type("None"), settings["returns"])
            else:
                ret = mtypes.Ret(
                    mtypes.Type(settings["returns"].get("type", "None")),
                    settings["returns"].get("__doc__", ""),
                )

        excs: List[mtypes.Exc] = []
        if "raises" in settings and settings["raises"] is not None:
            for r, v in settings["raises"].items():
                if v is None:
                    v = ""
                excs.append(mtypes.Exc(mtypes.Type(r), v))

        return FunctionSettings(doc, args, ret, excs, static, abstract, deprecated)

    def patch_functions(self, fns: List["mtypes.Function"]):
        for i, fn in enumerate(fns):

            # Find the name in settings:
            if fn.has_overloads():
                sname = "{}.{}".format(fn.name, i + 1)
            else:
                sname = fn.name

            # If the name is in the settings:
            if sname in self._mobase:
                fsettings = self._parse_function_settings(self._mobase[sname])

                # Force raises:
                fn.raises = fsettings.raises

                # Check the args:
                if fsettings.args is not None:
                    if len(fsettings.args) != len(fn.args):
                        logger.warn(
                            "Mismatch number of arguments for function mobase.{}."
                            .format(sname)  # noqa
                        )

                    for sarg, marg in zip(fsettings.args, fn.args):
                        marg.doc = sarg.doc
                        if not sarg.type.is_none():
                            marg.type = sarg.type

                # Check the return type:
                if fsettings.ret is not None:

                    # Force the doc anyway:
                    fn.ret.doc = fsettings.ret.doc

                    # Update the type if specified:
                    if not fsettings.ret.type.is_none():
                        fn.ret.type = fsettings.ret.type

                # Force the doc:
                fn.doc = fsettings.doc

                # Force depreciation:
                fn.deprecated = fsettings.deprecated

            else:
                logger.warn("Missing settings for function mobase.{}.".format(sname))

    def patch_class(self, cls: "mtypes.Class"):
        """Patch the given class using the given overwrites.

        See config.json for some examples of valid overwrites.

        Args:
            cls: The class to patch.
            settings: The settings.
        """

        logger.info("Patching class {}.".format(cls.name))

        # Find the class in mobase:
        csettings = self._get_class_settings(cls.canonical_name)

        if csettings is None:
            logger.warn("Class {} not found in settings.".format(cls.canonical_name))
            return

        if "__doc__" in csettings and csettings["__doc__"] is not None:
            cls.doc = csettings["__doc__"]
        csettings.pop("__doc__", None)

        # Check bases:
        if "__bases__" in csettings:
            for bc in csettings["__bases__"]:
                if bc.startswith("PyQt"):
                    cls.bases.append(mtypes.PyClass(bc))
                else:
                    cls.bases.append(self.register.get_object(bc))
            del csettings["__bases__"]

        if "__abstract__" in csettings and csettings["__abstract__"]:
            cls.abstract = True
            del csettings["__abstract__"]

        # Patch properties - Everything should be in config since property are poorly
        # documented by boost::python.
        properties: Dict[str, Any] = csettings.pop("properties[]", {})
        for prop in cls.properties:
            if prop.name in properties:
                sprop = properties[prop.name]

                # If we have a type:
                if "type" in sprop:
                    prop.type = mtypes.Type(sprop["type"])
                else:
                    logger.warn(
                        "Missing type for property {}.{}.".format(
                            cls.canonical_name, prop.name
                        )
                    )

                # If we have a description:
                if "desc" in sprop:

                    # If desc is None, we do not warn user, because the entry is in
                    # settings, just empty:
                    if sprop["desc"] is not None:
                        prop.doc = sprop["desc"]

                else:
                    logger.warn(
                        "Missing description for property {}.{}.".format(
                            cls.canonical_name, prop.name
                        )
                    )

        # Patch signals - Everything should be in config since signals are not really
        # exposed by boost::python.
        signals: List[str] = csettings.pop("signals[]", [])
        for signal in signals:
            cls.constants.append(
                mtypes.Constant(signal, mtypes.Type("pyqtSignal"), None)
            )

        # List of all items in csettings:
        keys = {k: False for k in csettings}

        # Group method by name:
        methods: Dict[str, List[mtypes.Method]] = defaultdict(list)
        for m in cls.methods:
            methods[m.name].append(m)

        for k, ms in methods.items():
            for i, m in enumerate(ms):

                # Find the name in settings:
                if m.has_overloads():
                    sname = "{}.{}".format(m.name, i + 1)
                else:
                    sname = m.name

                missing_settings: Set[str] = set()

                # If the name is in the settings:
                if sname in csettings:
                    keys[sname] = True
                    fsettings = self._parse_function_settings(csettings[sname])

                    # Force raises:
                    m.raises = fsettings.raises

                    # Force static:
                    if fsettings.static is not None:
                        if m.is_static() != fsettings.static:
                            logger.warn(
                                "Forcing method {}.{} to be {}.".format(
                                    cls.canonical_name,
                                    sname,
                                    "static" if fsettings.static else "non static",
                                )
                            )
                        m.static = fsettings.static

                    if fsettings.abstract is not None:
                        m.abstract = fsettings.abstract

                    # Check the args:
                    if fsettings.args is not None:
                        margs = m.args if m.is_static() else m.args[1:]
                        if len(fsettings.args) != len(margs):
                            logger.warn(
                                "Mismatch number of arguments for method {}.{}.".format(
                                    cls.canonical_name, sname
                                )
                            )

                        for sarg, marg in zip(fsettings.args, margs):
                            marg.doc = sarg.doc
                            marg.name = sarg.name
                            if not sarg.type.is_none():
                                marg.type = sarg.type

                    # Check the return type:
                    if fsettings.ret is not None:

                        # Force the doc anyway:
                        m.ret.doc = fsettings.ret.doc

                        # Update the type if specified:
                        if not fsettings.ret.type.is_none():
                            m.ret.type = fsettings.ret.type

                    # Force the doc:
                    m.doc = fsettings.doc

                    # Force deprecated:
                    m.deprecated = fsettings.deprecated

                # Only warn for "normal" methods:
                elif not m.name.startswith("__"):
                    missing_settings.add(sname)

            # Remove the deprecated methods:
            noverloads = 0
            for m in ms:
                overriden: bool = False
                for bc in cls.all_bases:
                    for bm in bc.methods:
                        if bm.name == "__init__" or bm.name != m.name:
                            continue
                        if len(bm.args) == len(m.args) and all(
                            ba.type == ma.type
                            for ba, ma in zip(bm.args[1:], m.args[1:])
                        ):
                            overriden = True
                if m.is_deprecated() or overriden:
                    cls.methods.remove(m)
                else:
                    noverloads += 1

            for m in ms:
                m.overloads = noverloads > 1

            if noverloads > 0 and missing_settings:
                for sname in missing_settings:
                    logger.warn(
                        "Missing settings for method {}.{}.".format(
                            cls.canonical_name, sname
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
        missings = [k for k, v in keys.items() if not v]
        if missings:
            logger.warn(
                "The following members were found in settings but not in the actual"
                " class {}: {}.".format(cls.canonical_name, ", ".join(missings))  # noqa
            )


def clean_class(cls: "mtypes.Class", settings: Settings):
    """Clean the given class object.

    Args:
        cls: The class object to clean.
        settings: The settings.
    """
    from .register import MOBASE_REGISTER

    # Remove duplicate methods (based on name and argument types):
    methods: Dict[
        Tuple[str, Tuple[mtypes.Arg, ...]], List[mtypes.Method]
    ] = OrderedDict()
    methods_by_name = defaultdict(list)
    for m in cls.methods:
        k = (m.name, tuple(m.args[1:]))
        if k not in methods:
            methods[k] = []
        methods[k].append(m)
        methods_by_name[m.name].append(m)

    clean_methods: List[mtypes.Method] = []
    for name, args in methods:
        ms = methods[name, args]
        method: mtypes.Method = ms[0]
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
            if arg0_name in MOBASE_REGISTER.cpp2py:
                arg0_name = MOBASE_REGISTER.cpp2py[arg0_name].name
            if arg0_name in [cls.name, "object"]:
                clean_methods.append(method)
            else:
                logger.info(
                    "Removing {}({}) from {} (already in base {}).".format(
                        name,
                        ", ".join(a.type.typing(settings) for a in args),
                        cls.name,
                        method.args[0].type.typing(settings),
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
    if isinstance(cls, mtypes.Enum):
        newc = [c for c in cls.constants if c.name.isupper()]
        if newc:
            cls.constants = newc

    # Clean inner classes:
    for ic in cls.inner_classes:
        clean_class(ic, settings)
