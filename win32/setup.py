# Copy compile.bat and setup.py to root directory and run compile.bat

from distutils.core import setup
import py2exe
import sys
import glob

setup(
      name="opendict",
      version="0.6.8",
      zipfile=None,
      package_dir = {"": "lib"},
      windows = [{
            "script":"opendict.py",
            "icon_resources": [(1, "win32/opendict.ico")]
            }],
      data_files=[("pixmaps", glob.glob("pixmaps/\\*.png"))],
)
