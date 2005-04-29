rem Copy compile.bat and setup.py to root directory and run compile.bat
C:\Python24\python.exe setup.py py2exe --packages encodings
rem Use this to get controls with the Windows XP appearance
rem C:\Python24\python.exe setup.manifest.py py2exe --packages encodings
copy copying.html dist
