# setup.py
from distutils.core import setup
import py2exe
import sys

sys.path = ["C:\\Program files\\OpenDict-dev\Opendict-source\lib"] + sys.path
#sys.argv[1] = "py2exe"

setup(name="opendict",
      scripts=["../opendict.py"],
)
