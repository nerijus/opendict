rem Copy compile.bat and setup.py to root directory and run compile.bat
C:\Python27\python.exe setup.py py2exe --packages encodings
rem Use this to get controls with the Windows XP appearance
rem C:\Python27\python.exe setup.manifest.py py2exe --packages encodings
copy copying.html dist
rem echo don't forget to copy msvcr71.dll from wxPython/distrib/msw/ to dist
rem echo before making a release
rem copy C:\Python27\msvcr71.dll dist
