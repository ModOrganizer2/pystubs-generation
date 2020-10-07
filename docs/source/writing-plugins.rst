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
  Settings can be ``int``, ``bool``, ``str`` or list of ``str``. Here we indicate
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

Examples
--------

This section contains (links to) examples of MO2 Python plugins.
Some of these plugins have been created for educational purpose and are thus very detailed and
easy to understand or get started from.

Tutorial Plugins
................

`This repository <https://github.com/Holt59/modorganizer-python_plugins>`_ contains examples of Python
plugins that were written only to help users write their own plugins.
If you want to start somewhere, this is the place to go.

Official Plugins
................

These plugins are (or will be) included in MO2 releases and are usually maintain by some members of
the MO2 development teams.
These plugins are not as well documented as the ones in the repository above.

- `Basic Games <https://github.com/ModOrganizer2/modorganizer-basic_games>`_ [``IPluginGame``]
    This is the meta-plugin for "basic" games. It is a complex
    plugins and should mostly be investigated if you want to add a game to it.
- `FNIS Tool <https://github.com/ModOrganizer2/modorganizer-fnistool>`_ [``IPluginTool``]:
    Plugin to integrate FNIS into MO2.
- `Preview DDS <https://github.com/ModOrganizer2/modorganizer-preview_dds>`_ [``IPluginPreview``]:
    Plugin to preview DDS files. Quite complex due to the use
    of OpenGL for display.
- `Form 43 Checker <https://github.com/ModOrganizer2/modorganizer-form43_checker>`_ [``IPluginDiagnose``]:
    Plugin that warn users if there are form 43 ESPs (Skyrim ESPs)
    enabled when managing a Skyrim SE instance.
- `Tool Configurator <https://github.com/ModOrganizer2/modorganizer-tool_configurator>`_ [``IPluginTool``]:
    Plugin that allows easier modifications of game settings.
    Mostly contains a complex GUI for managing INI files.
- `Script Extender Plugin Checker <https://github.com/ModOrganizer2/modorganizer-script_extender_plugin_checker>`_ [``IPluginDiagnose``]:
    Plugin that checks Script Extender logs to see
    if some plugins have failed to load and display information to the user if possible.


Unofficial Plugins
..................

These plugins have been created by developpers for MO2 and are usually distributed on Nexus.

- `Merge Plugins Hide <https://github.com/deorder/mo2-plugins>`_ [``IPluginTool``]:
    Hide / unhide plugins that were merged using ``Merge Plugins`` or ``zMerge``.
- `OpenMW Exporter <https://github.com/AnyOldName3/ModOrganizer-to-OpenMW>`_ [``IPluginTool``]:
    A Mod Organizer plugin to export your VFS, plugin selection and load order to OpenMW.
- `Orphaned Script Extender Save Deleter <https://github.com/AnyOldName3/modorganizer-orphaned_script_extender_save_deleter>`_ [``IPluginTool``]:
     Mod Organizer plugin to delete orphaned script extender co-saves.
- `Sync Mod Order <https://github.com/deorder/mo2-plugins>`_ [``IPluginTool``]:
    Synchronize mod order from current profile to another while keeping the (enabled/disabled) state intact.

*Feel free to open an issue or a pull-request if you want to add your own plugin to the list.*