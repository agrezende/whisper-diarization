import os
import pathlib

# Test symlink support
sourcepath = pathlib.Path("F:\\Temp\\A").absolute()
destination = pathlib.Path("F:\\Temp\\B").absolute()

destination.symlink_to(sourcepath)
