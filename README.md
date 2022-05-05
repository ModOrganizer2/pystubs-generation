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

Some words of warning:

- The stubs are as correct as possible, but some errors are expected.
- Some classes are said (in the stubs) to inherit `QWidget` or `QObject`. This is true
  on the C++ side but NOT on the python side. The inheritance is only added to help with
  auto-completion since these classes also override `__getattr__` to dispatch to the
  underlying `QWidget` or `QObject`. Some things might not work as expected with these
  class (e.g., `isinstance(myObject, QObject)` will return `False`), which is why a
  `_object()` and `_widget()` method is also provided.

## Generating the stubs

The stubs are generated using python by parsing the `mobase` module.
You need the version of python that matches your current MO2 installation: e.g., if you
have a `python310.dll` in your MO2 installation path, then you need **Python 3.10**.

To generate the stubs, you can run:

```bash
# install the package (-e if you want editable mode)
pip install [-e] .

# change the output folder to whatever you want
mo2-stubs-generator -c configs/config-2.4.yml -o mobase-stubs ${MO2_INSTALL_PATH}
```

Where `${MO2_INSTALL_PATH}` is the path to your MO2 installation (the one
containing `ModOrganizer.exe`).

The stubs are generated under `stubs/setup/mobase-stubs` by default, you
can change the output file by using the `-o` option.
The stubs under `stubs/setup/mobase-stubs` should not be committed as these are
generated from the version stubs under `stubs/${VERSION}/mobase-stubs`.

A few options are available for `mo2-stubs-generator`:

```bash
$ mo2-stubs-generator --help
usage: stubs generator for the MO2 python interface [-h] [-o OUTPUT] [-v] [-c CONFIG] INSTALL_DIR

positional arguments:
  INSTALL_DIR           installation directory of Mod Organizer 2

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output folder (default stubs/setup/mobase-stubs)
  -v, --verbose         verbose mode (all logs go to stderr)
  -c CONFIG, --config CONFIG
                        configuration file
```

The stubs generator will try hard to find a valid stubs for all classes
and methods of `mobase`.
A lot of information is available through the `-v` options. Without it,
only conversions or fixes considered "strange" will be shown.

## Configuration file

The configuration file contains information for the stubs that cannot be
deduced by `main` (or are too complex to deduce), and the documentation for everything.

## Uploading the stubs to pypi

The upload of the stubs to [https://pypi.org/project/mobase-stubs/](https://pypi.org/project/mobase-stubs/)
should be done automatically when a new Github tag is pushed.

## Extras &mdash; Using `mobase` in a Python interpreter

It is possible to start a (i)python interpreter with `mobase` imported by running

```bash
python -i -m mo2.stubs.generator.loader ${MO2_INSTALL_PATH}
```

You can also import `mobase` in your code using the following (after installing
this package):

```python
from mo2.stubs.generator import load_mobase

mobase = load_mobase(MO2_INSTALL_PATH)

# the above will probably not give you type-completion in your IDE or typing, so
# you can use the following (if the stubs are installed)
load_mobase(MO2_INSTALL_PATH)
import mobase
import mobase.widgets
```


**Note:** Most classes in `mobase` cannot be instantiated, so this is mostly intended
for MO2 developers.

## License

The MIT License (MIT)

Copyright (c) 2020, Holt59.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

See [LICENSE](LICENSE).
