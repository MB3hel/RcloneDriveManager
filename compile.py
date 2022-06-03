"""
This script is used during development to compile ui and qrc files into python source files
"""

import subprocess
import os

script_dir = os.path.dirname(os.path.realpath(__file__))
uic = ""
rcc = ""



# Find UIC and RCC
if uic == "" and rcc == "":
    try:
        import PySide6
        uic = "pyside6-uic"
        rcc = "pyside6-rcc"
    except ImportError:
        pass

if uic == "" and rcc == "":
    try:
        import PySide2
        uic = "pyside2-uic"
        rcc = "pyside2-rcc"
    except ImportError:
        pass


if uic == "" and rcc == "":
    print("No Pyside UIC and RCC found. Exiting.")
    exit(1)

# Remove old generated files
for dirpath, dirnames, filenames in os.walk(os.path.join(script_dir, "app")):
    for src_file in filenames:
        if src_file.endswith('.py') and (src_file.startswith("ui_") or src_file.endswith("_rc.py")):
            print("[Deleting]: {0}".format(src_file))
            os.remove(os.path.join(dirpath, src_file))

# Compile UI files
for dirpath, dirnames, filenames in os.walk(os.path.join(script_dir, "ui")):
    for src_file in filenames:
        if src_file.endswith('.ui'):
            dest_file = "ui_" + src_file.replace(".ui", ".py")
            src_path = os.path.join(dirpath, src_file)
            dest_path = os.path.join(script_dir, "src", dest_file)
            print("[Compiling]: {0} --> {1}".format(src_file, dest_file))
            subprocess.run([uic, src_path, "-o", dest_path])

# Compile QRC files
for dirpath, dirnames, filenames in os.walk(os.path.join(script_dir, "res")):
    for src_file in filenames:
        if src_file.endswith('.qrc'):
            dest_file = src_file.replace(".qrc", "") + "_rc.py"
            src_path = os.path.join(dirpath, src_file)
            dest_path = os.path.join(script_dir, "src", dest_file)
            print("[Compiling]: {0} --> {1}".format(src_file, dest_file))
            subprocess.run([rcc, src_path, "-o", dest_path])
