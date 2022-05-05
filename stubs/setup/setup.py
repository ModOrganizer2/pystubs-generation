"""Python setup script.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-10-06 10:55:36
:last modified by: Stefan Lehmann
:last modified time: 2019-07-23 10:27:04

"""
import io
import os
import re
from collections import defaultdict
from pathlib import Path

from setuptools import setup


def read(*names, **kwargs):
    try:
        with io.open(
            os.path.join(os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8"),
        ) as fp:
            return fp.read()
    except IOError:
        return ""


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def find_package_data(path: str):
    package_data: dict[str, list[str]] = defaultdict(lambda: [])
    for stubfile in Path(path).glob("**/*.pyi"):
        package_data[stubfile.parent.as_posix().replace("/", ".")].append(stubfile.name)
    return dict(package_data)


long_description = read("README.md")

package_data = find_package_data("mobase-stubs")

setup(
    name="mobase-stubs",
    url="https://github.com/ModOrganizer2/mo2-pystubs-generation",
    author="Holt59",
    author_email="capelle.mikael@gmail.com",
    description="PEP561 stub files for the mobase python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=find_version("mobase-stubs", "__init__.pyi"),
    packages=list(package_data.keys()),
    package_data=package_data,
    install_requires=[],
    python_requires="==3.10.*",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
    ],
)
