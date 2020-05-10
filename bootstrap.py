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
shutil.rmtree(target_path)
os.makedirs(target_path, exist_ok=True)

install_path = Path(args.install)
if install_path.joinpath("bin").exists():
    install_path = install_path.joinpath("bin")

shutil.copyfile(
    install_path.joinpath("plugins", "data", "pythonrunner.dll"),
    target_path.joinpath("mobase.pyd"))
for dll in install_path.iterdir():
    if dll.name.endswith(".dll"):
        shutil.copy2(dll, target_path)

# Warning if PyQt is not installed:
try:
    import PyQt5
except ImportError:
    print("WARNING: You need to install PyQt5 to generate the stubs: pip install PyQt5")

print("Run 'python generate-stubs.py -o stubs\mobase.pyi bin\mobase.pyd' to generate the stubs.")