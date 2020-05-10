# -*- encoding: utf-8 -*-

import argparse
import os
import shutil

from pathlib import Path

parser = argparse.ArgumentParser("Setup for MO2 stubs generation")
parser.add_argument("install", type=str, help="path to the MO2 installation")

args = parser.parse_args()

# We need to copy everything needed for mobase to load:
target_path = Path(__file__).parent.joinpath("bin")
print("Copying required files to '{}'... ".format(target_path))
shutil.rmtree(target_path, ignore_errors=True)
os.makedirs(target_path, exist_ok=True)

install_path = Path(args.install)
if install_path.joinpath("bin").exists():
    install_path = install_path.joinpath("bin")

# We need PyQt5:
shutil.copytree(
    install_path.joinpath("plugins", "data", "PyQt5"),
    target_path.joinpath("PyQt5")
)

# We need some DLLs:
for dll in ["uibase.dll", "python38.dll", "boost_python38-vc142-mt-x64-1_73.dll"]:
    shutil.copy2(install_path.joinpath(dll), target_path)

for qtdll in install_path.joinpath("dlls").iterdir():
    if qtdll.is_file() and qtdll.name.startswith("Qt5"):
        shutil.copy2(qtdll, target_path)

# We need the actual module:
shutil.copyfile(
    install_path.joinpath("plugins", "data", "pythonrunner.dll"),
    target_path.joinpath("mobase.pyd"))

print("Run 'python generate-stubs.py -o stubs\mobase.pyi bin\mobase.pyd' to generate the stubs.")