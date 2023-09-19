# -*- encoding: utf-8 -*-

from __future__ import annotations

from collections import OrderedDict

from .mtypes import Class, Function, PyTyping


class MobaseRegister:
    """
    Class that register classes.
    """

    objects: dict[str, Class | list[Function] | PyTyping]

    def __init__(self) -> None:
        self.raw_objects: dict[str, type] = OrderedDict()
        self.objects = {}

    def add_object(self, name: str, object: type) -> None:
        self.raw_objects[name] = object

    def make_object(
        self, name: str, e: type | None = None
    ) -> Class | list[Function] | PyTyping:
        """
        Construct a Function, Class or Enum for the given object.

        Args:
            name: The name of the object to inspect.
            e: The object to inspect, or None to fetch it from the underlying list.

        Returns:
            A Class object for the given type, or a list of function overloads.
        """
        from .parser import make_class, make_functions

        if e is None:
            e = self.raw_objects[name]

        if name not in self.raw_objects:
            self.raw_objects[name] = e

        if name not in self.objects:
            if isinstance(e, type):
                self.objects[name] = make_class(e, self)
            elif callable(e):
                self.objects[name] = make_functions(e)

            # typing stuff
            elif type(e).__module__ == "types" or type(e).__module__ == "typing":
                self.objects[name] = PyTyping(name, e)

        return self.objects[name]

    def get_object(self, name: str) -> Class | list[Function] | PyTyping:
        """
        Retrieve the object if the given name. Fails if no object with this
        name exists (if `make_object(name, ...)` has never been called).

        Args:
            name: Name of the object to retrieve.

        Returns:
            The object with the given name.
        """
        return self.objects[name]
