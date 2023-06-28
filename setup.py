from cx_Freeze import setup, Executable
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="Practice Application",
    version="1.0",
    description="Изобрёл велосипед",
    executables=[Executable(os.path.join(base_dir, "gui","guiapp.py"))]
)