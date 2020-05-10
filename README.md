# Mod Organizer 2 - Python stubs generation

This little project can be used to generate python stubs (`.pyi` file) for the MO2 python
interface `mobase`.

## Using the stubs

If you do not want to generate them, the latest stubs are available under [`stubs/mobase.pyi`](stubs/mobase.pyi).

Some words of warning:
- The stubs are as correct as possible, but some errors are expected.
- If you see a `NotImplemented` class anywhere in the stubs, it means that a proper interface is
    currently not available.

## Generating the stubs

To generate the stubs, you first need to setup the directory:

```
# Note: I only tested with python 3.8:
pip install PyQt5
python bootstrap.py ${MO2_INSTALL_PATH}
```

Where `${MO2_INSTALL_PATH}` is the path to your MO2 installation (the one containing `ModOrganizer.exe`).
This will first install `PyQt5` and then copy the required files from your installation folder to a `bin/`
directory (DLLs, the actual `mobase.pyd` module, etc.).

To generate the stubs, you can then run:

```
python generate-stubs.py -o stubs\mobase.pyi bin\mobase.pyd
```

If you do not specify a `-o` option, output will go to `stdout`, so you should redirect. Warning and "critical"
messages are printed to `stderr`.

A few options are available for `generate-stubs.py`:

```
usage: Stubs generator for the MO2 python interface [-h] [-o OUTPUT] [-v] [-c CONFIG] [mobase]

positional arguments:
  mobase                location of the mobase module (.pyd)

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

The configuration file contains information for the stubs that cannot be deduced by `generate-stubs` (or are too
complex to deduce). In particular:

- list of names to ignore - can be used to hide name or to ignore object for which stubs cannot be generated (currently
    only stubs for classes can be generated, so functions are ignored);
- list of methods to override - can be used to override method signatures for methods that are too complex (see below);
- list of property types - should be used to specify the types of the property since these cannot be deduced.

An example of configuration file is [`config.json`](config.json), and an empty configuration is provided ([`empty.json`](empty.json))
to show what happens with an empty configuration.