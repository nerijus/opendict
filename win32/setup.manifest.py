# Copy compile.bat and setup.py to root directory and run compile.bat

from distutils.core import setup
import py2exe
import sys
import glob

# The manifest will be inserted as resource into opendict.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store if in a file named
# opendict.exe.manifest, and probably copy it with the data_files
# option.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

################################################################
# arguments for the setup() call

opendict = dict(
    script = "opendict.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="OpenDict"))],
    )

options = {"py2exe": {"compressed": 1,
                      "optimize": 2}}


setup(
    name="OpenDict",
    version="0.6.3",
    options = options,
    zipfile = None,
    package_dir = {"": "lib"},
    windows = [opendict],
    data_files=[("pixmaps", glob.glob("pixmaps/\\*.png"))],
    )
