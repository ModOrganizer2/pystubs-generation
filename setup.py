# -*- encoding: utf-8 -*-

from setuptools import find_namespace_packages, setup

install_requires = ["black", "isort"]

dev_requires = [
    "black",
    "flake8-black",
    "flake8",
    "types-chardet",
]

setup(
    name="mo2-stubs-generator",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", include=["mo2.*"]),
    author="Holt59",
    author_email="capelle.mikael@gmail",
    description="Python stubs generator for mobase (MO2 Python API).",
    long_description=open("README.md").read(),
    url="https://github.com/ModOrganizer2/pystubs-generation",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    license="MIT",
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    entry_points={
        "console_scripts": ["mo2-stubs-generator=mo2.stubs.generator.__main__:main"],
    },
)
