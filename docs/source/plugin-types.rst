.. _type-of-plugins:

Type of Plugins
===============

Plugins are passive, that is: they react to events emitted by the core application or extend
an existing functionality (like adding support for additional types of installers). Plugins
should integrate with Mod Organizers concepts. While you could write an INI editor that works with
the global INI files instead of the profile specific ones, what would be the point?

Depending on where/how the plugin integrates with MO you need to write a different type of plugin,
in practice this means you need to implement a different interface (inherit from a different base
plugin class from ``mobase``). As mentioned above, plugins are passive: the plugin type decides how/when
MO makes requests to/invokes your plugin.
All plugins however gain access to MOs own plugin interface so all plugins get to make the same requests
to MO.

Installers
----------

| **Interface:** :class:`IPluginInstaller<mobase.IPluginInstaller>`, :class:`IPluginInstallerSimple<mobase.IPluginInstallerSimple>`,
  :class:`IPluginInstallerCustom<mobase.IPluginInstallerCustom>`
| **Examples:** ``installer_bain``, ``installer_bundle``, ``installer_fomod``, ``installer_ncc``, ``installer_quick``, ``installer_manual``.

An installer is invoked when the user tries to install a mod, either by double clicking in the download
view or through the "Install Mod.." button or "Reinstall mod" item from the mod lists context menu.
There are actually two ways to write an installer, *simple* or *complex*:

- With *simple* installers, MO does the unpacking of the file but this works only with standard archive formats.
  The plugin can then select the files and folders that requires extraction, and where to extract them.
- *Complex* installers are more flexible but require a bit more work.

Previewers
----------

| **Interfaces:** :class:`IPluginPreview<mobase.IPluginPreview>`
| **Examples:** ``preview_base``

These plugins add support for previewing files in the data pane.
Right now all image formats supported by Qt are implemented (including `.dds`) but no audio files and
no 3d mesh formats.

Mod Page
--------

*WIP*

| **Interfaces:** :class:`IPluginModPage<mobase.IPluginModPage>`
| **Examples:** ``page_tesalliance``

Mod Page plugins implement interfaces to modding communities where mods can be downloaded, checked
for updates and so on.
This interface is not finished and some of the bits that are do not actually get used. The goal is
that the whole Nexus integration can be implemented through this interface and can then be removed
from the core application. This is a task for the distant future, unless someone wants to volunteer.

Game
----

| **Interfaces:** :class:`IPluginGame<mobase.IPluginGame>`
| **Examples:** ``game_oblivion``, ``game_fallout3``, ``game_falloutnv``, ``game_skyrim``, ...

These plugins (shall eventually) implement all the game specific features and further game plugins are
able to add support for further games.
The plugin is also responsible to help MO determine if (and where) the game is installed in the first place.
Since supporting a game properly requires extensions in many places of the UI.
To allow this without creating one huge plugin interface that involves every aspect of MO,
game plugins can register only the features they need to MO2 using :meth:`registerFeature<mobase.IGameFeatures.registerFeature>`

As an example for a game feature take BSA invalidation: If the game requires BSA invalidation it will implement
this feature.
Wherever the core can support BSA invalidation it will query whether the current game has this feature and if so
query the implementation on specifics (like "How should the invalidation BSA be called" and "what's the right bsa version").
Of course, the goal is for feature interfaces to be as generic as possible without limiting usefulness.

**Note:** The :class:`IPluginGame<mobase.IPluginGame>` interface is complex, and mostly designed for Gamebryo games. If you plan
on writting a game plugin for another type of games, you might be interested by a simpler interface and might
want to check out the `Basic Games <https://github.com/ModOrganizer2/modorganizer-basic_games>`_ meta-plugin.


Tool
----

| **Interfaces:** :class:`IPluginTool<mobase.IPluginTool>`
| **Examples:** ``tool_configurator``, ``tool_inieditor``, ``fnistool``

This is the simplest of plugin interfaces. Such plugins simply place an icon inside the tools submenu and get
invoked when the user clicks it. They are expected to have a user interface of some sort.
These are almost like independent applications except they can access all Mod Organizer interfaces like querying
and modifying the current profile, mod list, load order, use MO to install mods and so on.
A tool plugin can (and should!) integrate its UI as a window inside MO and thus doesn't have to initialize a
windows application itself.

Proxies
-------

| **Interfaces:** :class:`IPluginProxy<mobase.IPluginProxy>`
| **Examples:** ``plugin_python``

Proxy Plugins expose the plugin api to foreign languages. This is what allows you to write plugins using python
in the first place.
The python proxy is easily the most complicated plugin and requires constant updating so if you're considering
writing a Haskell plugin because that is your programming language of choice, I am fairly certain learning python
is easier than writing the haskell proxy. Just saying.
And no, you can not write a proxy for a third language in Python, do not be silly.

*Free Plugins*
--------------

| **Interfaces:** :class:`IPlugin<mobase.IPlugin>`
| **Examples:** ``check_fnis``, ``bsa_extractor``, ``diagnose_basic``, ``tool_inibakery``

"Free" plugins implement none of the interfaces and thus initially do not integrate with MO at all.
They are initialized by MO and get access to the MO interface.
This makes sense if you only want to implement one of the extension interfaces (see below) or register handlers
for events.

Extension Interfaces
--------------------

In Python, these interfaces are similar to other plugin types, but in C++, those do not inherit ``IPlugin`` so
that plugins can implement one or more of these interfaces, in addition to a normal plugin type.

Diagnose
........

| **Interfaces:** :class:`IPluginDiagnose<mobase.IPluginDiagnose>`
| **Examples:** ``diagnose_basic``, ``installer_ncc``, ``plugin_python``, ``script_extender_plugin_checker``

This interface lets the plugin report issues that are then listed in the "Problems" icon in the main window.
If possible the plugin can also provide an automatic or guided fix to the problem.
The ``diagnose_basic`` plugin does nothing but analyze the MO installation and report problems it discovers (like
*"There are files in your overwrite directory."*) but usually a plugin will want to report issues relevant for its
own operation.
For instance, ``installer_ncc`` requires a specific version of .NET and will report a problem if it is not installed.
This should always be the prefered way to communicate problems the user has to fix but should never be used for problems
he cannot fix (i.e. *"This plugin does not work with this game."*).
An empty problem list should always be achievable.

File Mappings
.............

| **Interfaces:** :class:`IPluginFileMapper<mobase.IPluginFileMapper>`
| **Examples:** ``tool_inibakery``, ``game_gamebryo``

This interface allows plugins to add virtual file (or directory) links to the virtual file system in addition to the
mod files.
Profile-local save games, ini-files and load-orders are all implemented this way in MO2.
