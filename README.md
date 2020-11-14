# Mod Organizer 2 - Python stubs generation

This project can be used to generate python stubs (`.pyi` file) for the MO2 python
interface `mobase`.

## Using the stubs

You can install the `stubs` with `pip`:

```bash
pip install mobase-stubs
```

This will install the latest stubs on PyPi which usually corresponds to the latest release of
MO2.
You can install stubs for a specific version of MO2:

```bash
pip install mobase-stubs==2.3.2.*
```

If you want development stubs, you can install them this way:
```bash
# Clone this repository:
git clone https://github.com/ModOrganizer2/pystubs-generation.git

# Install the stubs:
cd pystubs-generation/stubs/setup
pip install .
```

Some words of warning:
- The stubs are as correct as possible, but some errors are expected.
- If you see a `InterfaceNotImplemented` class anywhere in the stubs, it means that
  a proper interface is currently not available.
- Some classes are said (in the stubs) to inherit `QWidget` or `QObject`. This is true
  on the C++ side but NOT on the python side. The inheritance is only added to help with
  auto-completion since these classes also override `__getattr__` to dispatch to the
  underlying `QWidget` or `QObject`. Some things might not work as expected with these
  class (e.g., `isinstance(myObject, QObject)` will return `False`), which is why a
  `_object()` and `_widget()` method is also provided.

## Generating the stubs

The stubs are generated using python by parsing the `mobase` module.
You need the version of python that matches your current MO2 installation: e.g., if you
have a `python38.dll` in your MO2 installation path, then you need **Python 3.8**.

To generate the stubs, you can run:

```
# Change the output folder to whatever you want:
python main.py -c configs\config-2.4.yml ${MO2_INSTALL_PATH}
```

Where `${MO2_INSTALL_PATH}` is the path to your MO2 installation (the one containing `ModOrganizer.exe`).

The stubs are generated under `stubs/setup/mobase-stubs/__init__.pyi`, you
can change the output file by using the `-o` option
The latest stubs are kept under `stubs/setup/mobase-stubs/__init__.pyi`,
and when a new version is released, the stubs are backed-up under
`stubs/x.y.z/mobase.pyi`.

A few options are available for `main.py`:

```
usage: Stubs generator for the MO2 python interface [-h] [-o OUTPUT] [-v] [-c CONFIG] INSTALL_DIR

positional arguments:
  INSTALL_DIR           installation directory of Mod Organizer 2

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file (default stubs/setup/mobase-stubs/__init__.pyi)
  -v, --verbose         verbose mode (all logs go to stderr)
  -c CONFIG, --config CONFIG
                        configuration file
```

The stubs generator will try hard to find a valid stubs for all classes
and methods of `mobase`.
A lot of information is available through the `-v` options. Without it,
only conversions or fixes
considered "strange" will be shown.
For instance, here is the output with the current `config-2.4.yml` file:

```
WARNING: Replacing IOrganizer::FileInfo with FileInfo.
WARNING: Replacing IOrganizer::FileInfo with FileInfo.
WARNING: Replacing IPluginInstaller::EInstallResult with InstallResult.
WARNING: Replacing IPluginInstaller::EInstallResult with InstallResult.
```

As you can see, only a few types were manually fixed (specified in
`config-2.4.yml`).

## Configuration file

The configuration file contains information for the stubs that cannot be
deduced by `main` (or are too complex to deduce), and the documentation for everything.

## Uploading the stubs to pypi

The upload of the stubs to https://pypi.org/project/mobase-stubs/ should be
done automatically when a new Github release is made.

## Extras &mdash; Starts a python interpreter with `mobase`

It is possible to start a (i)python interpret with `mobase` imported by running:

```
python -im generator.loader ${MO2_INSTALL_PATH}
```

This has no real usage except for MO2 developers since most classes from the `mobase` module cannot be instantiated.

# License

The MIT License (MIT)

Copyright (c) 2020, Holt59.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

See [LICENSE](LICENSE).
