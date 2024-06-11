import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Pour une application GUI

executables = [Executable("run.py", base=base)]

setup(
    name="infraDrive",
    version="0.1",
    description="infra drive to manage test benches",
    executables=executables,
)
