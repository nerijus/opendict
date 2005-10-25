rem Copy compile.bat and setup.py to root directory and run compile.bat
C:\Python24\python.exe setup.py py2exe --packages encodings
rem Use this to get controls with the Windows XP appearance
rem C:\Python24\python.exe setup.manifest.py py2exe --packages encodings
copy copying.html dist
echo don't forget to copy msvcr71.dll from wxPython/distrib/msw/ to dist
echo before making a release
copy C:\Python24\msvcr71.dll dist
