Writing Plugins
===============

Getting started
---------------

Now that you know which type of plugin you need, you can start writing your own plugin.
There is two way to write a Python plugin:

- :ref:`single-file-plugin`: You use a single ``.py`` file that you put directly in the ``plugins``
  folder of the MO2 installation.
- :ref:`module-plugin`: You create a Python package (folder) with a ``__init__.py`` file that you
  put in the ``plugins`` folder of the MO2 installation.

Most examples of plugins will be module plugins.

.. _single-file-plugin:

Single file plugins
...................

Prior to version 2.3, this was the only way of creating a Python plugin. You simply need
to create a ``myplugin.py`` file in the ``plugins`` folder of Mod Organizer 2 with a content
similar to:

.. code-block:: python

    import mobase

    class MyPlugin(...):
        ...

    def createPlugin() -> mobase.IPlugin:
        return MyPlugin()

We will see later on how to create the actual ``MyPlugin`` class.
The ``createPlugin`` function is the function that is called by Mod Organizer 2 to instantiate
the plugin.

You can also provide multiple plugins by using ``createPlugins`` instead of ``createPlugin``:

.. code-block:: python

    from typing import List

    import mobase

    class MyPlugin1(...):
        ...

    class MyPlugin2(...):
        ...


    def createPlugins() -> List[mobase.IPlugin]:
        return [MyPlugin1(), MyPlugin2()]

**Note:** If you provide neither ``createPlugin()`` nor ``createPlugins``, MO2 will display
an error message in the logs.

**Note:** If you add a return type-hint to ``createPlugin()`` or ``createPlugins`` (``->``), ``mypy``
will type-check the function and warn you if one of your plugins is invalid, e.g. if you
forgot to implement a required method.

If you need to provide other files with your ``.py`` (assets or other Python files), you can
put them in the ``plugins/data``, but this is deprecated since MO2 2.3, and you should instead
create a Python module plugin.

.. _module-plugin:

Module Plugins
..............

Module plugins were introduced in MO2 2.3 and are shipped as whole folder containg a python module.
The minimum content of the folder is a ``__init__.py`` file with ``createPlugin`` or ``createPlugins``
function.

A minimal module plugin could be as follows:

.. code-block:: bash

    plugins/               # MO2 plugins folder
        myplugin/
            __init__.py
            plugin.py

In ``plugin.py``, you could define your plugin:

.. code-block:: python

    # plugin.py

    import mobase

    class MyPlugin(...):
        ...

And in ``__init__.py``, you should write ``createPlugin``:

.. code-block:: python

    # __init__.py

    import mobase  # For type-checking createPlugin().

    from .plugin import MyPlugin  # Always use relative import:

    def createPlugin() -> mobase.IPlugin:
        return MyPlugin()

Similar to single-file plugins, you can expose ``createPlugins`` instead of ``createPlugin``
to instantiate multiple plugins.

**Note:** The name of the folder does not have to be a valid python package, and you should
always use relative imports within the module (``import .xxx``) instead of absolute ones.

Writing the plugin
------------------

``IPlugin`` interface
.....................

In the code snippets above, the ``MyPlugin`` class was not implemented.
Depending on the :ref:`type of plugins<type-of-plugins>` that you want to create, you will
need to extend a different class.

.. code-block:: python

    class MyTool(mobase.IPluginTool):  # Create a Tool plugin
        ...

    class MyPreview(mobase.IPluginPreview):  # Create a preview plugin
        ...

Each plugin class has its own abstract methods that you need to implement but all the classes
also extend ``IPlugin``, so you need to implement the methods from :class:`IPlugin<mobase.IPlugin>`:

.. code-block:: python

    from typing import List

    import mobase

    class MyPlugin(...):  # The base class depends on the actual type of plugin

        _organizer: mobase.IOrganizer

        def __init__(self):
            super().__init__()  # You need to call this manually.

        def init(self, organizer: mobase.IOrganizer):
            self._organizer = organizer
            return True

        def name(self) -> str:
            return ""

        def author(self) -> str:
            return "Tannin"

        def description(self) -> str:
            return self._tr("Gives a friendly greeting")

        def version(self) -> mobase.VersionInfo:
            return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)

        def isActive(self) -> bool:
            return self._organizer.pluginSetting(self.name(), "enabled")

        def settings(self) -> List[mobase.PluginSetting]:
            return [
                mobase.PluginSetting("enabled", "enable this plugin", True)
            ]

Most of these are pretty simple to understand:

- ``name``: Returns the name of the plugin. The name of the plugin is used to
  fetch settings, and in many places, so this should not change between versions.
- ``author``: Returns the name of the plugin author (you!).
- ``description``: Returns the description of the plugin.
- ``version``: Returns the version of the plugin. See :class:`VersionInfo<mobase.VersionInfo>` for
  more details.
- ``isActive``: Returns ``True`` if the plugin is active, ``False`` otherwise. This
  usually returns ``True``, unless you want to check for something to dynamically
  enable the plugin. You can also use a plugin setting to allow users to disable
  your plugins.
- ``settings``: Returns the list of settings (that user can modify) for this plugin.
  Settings can be ``int```, ``bool``, ``str`` or list of ``str``. Here we indicate
  that we have a "enabled" setting that user could use to disable the plugin (and
  we use it in ``isActive``).


The ``__init__`` method is the normal Python constructor for our plugin, called when doing
``MyPlugin()``.
You should always call ``super().__init__()`` explicitly when extending MO2 classes (due to
a "bug" in ``boost.python``).

The ``init`` method is called by MO2 to initialize the plugin. The given argument, ``organizer``,
is an instance of :class:`IOrganizer<mobase.IOrganizer>` which is the class used to interface with MO2.
Here, we use it in the ``isActive()`` method to retrieve the "enabled" setting for our plugin.
See :class:`IOrganizer<mobase.IOrganizer>` for more details.