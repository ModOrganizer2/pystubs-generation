FAQ
===

.. toctree::
   :maxdepth: 4

1. Why is MO2 throwing an exception when I try to create a type inheriting one of MO2 class?
............................................................................................

This often happens if you forget to call ``super().__init__()`` with the right arguments.
Even if the list of arguments is empty (as in the example), it must be called due to a "bug"
in ``boost::python``:

.. code-block:: python

    class MySaveGame(mobase.ISaveGame):
        def __init__(self):
            super().__init__()  # Mandatory!

2. How can I be sure to implement all the required methods when creating a plugin?
..................................................................................

It is kind of annoying to create a MO2 python plugin that kind of works and have it crash
at some point simply because there plugin is missing a function implementation.
You can have ``mypy`` warn you for such issue by typing the ``createPlugin`` or ``createPlugins``
functions:

.. code-block:: python

    import typing

    # A plugin that is missing something (e.g. display()).
    class MyPlugin(mobase.IPluginTool): ...

    # If you type-hint `createPlugin` by adding `-> mobase.IPlugin`,
    # `mypy` will warn you that `MyPlugin` is an incomplete class.
    def createPlugin() -> mobase.IPlugin:
        return MyPlugin()

    # You can also type-hint `createPlugins`:
    def createPlugins() -> typing.List[mobase.IPlugin]:
        return [MyPlugin()]


3. Why are my ``isinstance(x, QObject)`` and ``isinstance(y, QWidget)`` not working?
....................................................................................

Some classes from ``mobase`` are said to inherit ``QObject`` and ``QWidget``  in the
stubs, such as :class:`mobase.IDownloadManager`.
This is not the case in practice due to limitation in Python and ``boost::python``.
The bases are in the stubs to allow for auto-completion and typing, which is then
simulated in the real ``mobase`` by overriding ``__getattr__`` and delegating to
the underlying ``QObject`` or ``QWidget``.