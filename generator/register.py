# -*- encoding: utf-8 -*-

from collections import OrderedDict
from typing import Optional, Dict, Union, List

from . import logger
from .mtypes import Class, Type, CType, Function


class MobaseRegister:
    """ Class that register class. """

    objects: Dict[str, Union[Class, List[Function]]]

    def __init__(self):
        """ Create a new register with the list of objects. """
        self.raw_objects: Dict[str, Union[type]] = OrderedDict()
        self.objects = {}

        self._cpptypes = {}
        self.cpp2py = {}

    def add_object(self, name, object):
        self.raw_objects[name] = object

    def make_object(
        self, name: str, e: Optional[type] = None
    ) -> Union["Class", List["Function"]]:
        """Construct a Function, Class or Enum for the given object.

        Args:
            name: The name of the object to inspect.
            e: The object to inspect, or None to fetch it from the underlying list.

        Returns: A Class object for the given type, or a list of function overloads.
        """
        from .parser import make_enum, make_class, is_enum, make_functions

        if e is None:
            e = self.raw_objects[name]

        if name not in self.raw_objects:
            self.raw_objects[name] = e

        if name not in self.objects:
            if is_enum(e):
                self.objects[name] = make_enum(name, e)
            elif isinstance(e, type):
                self.objects[name] = make_class(name, e, self)
            elif callable(e):
                self.objects[name] = make_functions(name, e)

        return self.objects[name]

    def get_object(self, name: str):
        """
        Retrieve the object if the given name. Fails if no object with this
        name exists (if `make_object(name, ...)` has never been called).

        Args:
            name: Name of the object to retrieve.

        Returns:
            The object with the given name.
        """
        return self.objects[name]

    def register_type(self, ptype: "Type", ctype: "CType"):
        """Register an equivalence between a python name and a C++ name.

        Args:
            python_name: Name of the Python class.
            cpp_name: Name of the C++ class.
        """
        # Register the const equivalent for smart pointers:
        cname = ctype.name
        if ctype.is_smart_pointer():
            if cname.find(" const >") != -1:
                c2name = cname.replace(" const >", ">")
                if c2name in self._cpptypes:
                    ptype = self.cpp2py[c2name]
            # Not the const, replace the const one:
            else:
                c2name = cname.replace(">", " const >")
                if c2name in self._cpptypes and self.cpp2py[c2name].is_object():
                    self._cpptypes[c2name] = ctype
                    self.cpp2py[c2name] = ptype
                    logger.warning(
                        "Replace registration {} [c++] with {} [python] using {}"
                        " information.".format(c2name, ptype.name, cname)  # noqa: E501
                    )

        if cname not in MOBASE_REGISTER.cpp2py:
            self._cpptypes[cname] = ctype
            self.cpp2py[cname] = ptype
            logger.info("Registered {} [c++] as {} [python].".format(cname, ptype.name))

    @property
    def py2cpp(self):
        result = {v.name: [] for v in self.cpp2py.values()}
        for k in self.cpp2py:
            result[self.cpp2py[k].name].append(self._cpptypes[k])
        return result


MOBASE_REGISTER = MobaseRegister()
