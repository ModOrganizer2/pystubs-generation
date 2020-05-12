# Mod Organizer 2 - Python stubs generation

This little project can be used to generate python stubs (`.pyi` file) for the MO2 python
interface `mobase`.

## Using the stubs

If you do not want to generate them, the generated stubs are available under [`stubs/`](stubs/) for latest
versions of MO2.

Some words of warning:
- The stubs are as correct as possible, but some errors are expected.
- If you see a `InterfaceNotImplemented` class anywhere in the stubs, it means that a proper interface is
    currently not available.
- Some classes are said (in the stubs) to inherit `QWidget` or `QObject`. This is true on the C++ side but NOT
    on the python side. The inheritance is only added to help with auto-completion since these classes also
    override `__getattr__` to dispatch to the underlying `QWidget` or `QObject`. Some things might not work as
    expected with these class (e.g., `isintance(myObject, QObject)` will return `False`), which is why a
    `_object()` and `_widget()` method is also provided.

### Visual Studio Code

The `mobase` stubs can be used with [Visual Studio Code](https://code.visualstudio.com/) to enable auto-completion and eventually linting using `mypy`:
- To use the stubs for auto-completion, you can use the
[`python.autoComplete.extraPaths`](https://code.visualstudio.com/docs/python/editing#_enable-intellisense-for-custom-package-locations)
setting.
- If you want them to work with `mypy`, the easiest way is to create a `setup.cfg` file at the root of your
project (or any file that `mypy` recognize) and set the `mypy_path` property, see
[`mypy` documentation](https://mypy.readthedocs.io/en/stable/config_file.html#import-discovery).

## Generating the stubs

The stubs are generated using python by parsing the `mobase` module.
You need the version of python that matches your current MO2 installation: e.g., if you have a `python38.dll` in
your MO2 installation path, then you need **python 3.8**.

To generate the stubs, you can run:

```
python main.py -o stubs\mobase.pyi ${MO2_INSTALL_PATH}
```

Where `${MO2_INSTALL_PATH}` is the path to your MO2 installation (the one containing `ModOrganizer.exe`).

If you do not specify a `-o` option, output will go to `stdout`, so you should redirect. Warning and "critical"
messages are printed to `stderr`.

A few options are available for `main.py`:

```
usage: Stubs generator for the MO2 python interface [-h] [-o OUTPUT] [-v] [-c CONFIG] INSTALL_DIR

positional arguments:
  INSTALL_DIR           installation directory of Mod Organizer 2

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file (output to stdout if not specified)
  -v, --verbose         verbose mode (all logs go to stderr)
  -c CONFIG, --config CONFIG
                        configuration file
```

The stubs generator will try hard to find a valid stubs for all classes and methods of `mobase`.
A lot of information is available through the `-v` options. Without it, only conversions or fixes
considered "strange" will be outputed. For instance, here is the output with the current `config.json`
file:

```
WARNING: Replacing IOrganizer::FileInfo with FileInfo.
WARNING: Replacing IOrganizer::FileInfo with FileInfo.
WARNING: Replacing IPluginInstaller::EInstallResult with InstallResult.
WARNING: Replacing IPluginInstaller::EInstallResult with InstallResult.
CRITICAL: Found bool * which is a pointer to a built-in python type.
```

As you can see, only a few types were manually fixed (specified in `config.json`), but a `bool *`
parameter was found, which is not valid, so this would require a change in the actual C++ bindings.

## Configuration file

The configuration file contains information for the stubs that cannot be deduced by `main` (or are too
complex to deduce). In particular:

- list of names to ignore - can be used to hide name or to ignore object for which stubs cannot be generated (currently
    only stubs for classes can be generated, so functions are ignored);
- list of methods to override - can be used to override method signatures for methods that are too complex (see below);
- list of property types - should be used to specify the types of the property since these cannot be deduced;
- list of bases - should be used to override the bases of a class (e.g., to add `QObject`);
- list of Qt signals - should be used to indicate available signals (new ones).

An example of configuration file is [`config.json`](config.json), and an empty configuration is provided ([`empty.json`](empty.json))
to show what happens with an empty configuration.