; Script generated by the My Inno Setup Extensions Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=OpenDict
AppVerName=OpenDict 0.5.6
AppPublisher=Martynas Jocius
;AppPublisherURL=http://opendict.sourceforge.net
;AppSupportURL=http://opendict.sourceforge.net
;AppUpdatesURL=http://opendict.sourceforge.net
DefaultDirName={pf}\OpenDict
DisableDirPage=no
DefaultGroupName=OpenDict
AllowNoIcons=yes
LicenseFile=C:\Program Files\OpenDict-dev\OpenDict-source\copying.txt
; MessagesFile=compiler:lithuanian.isl

[Tasks]
; NOTE: The following entry contains English phrases ("Create a desktop icon" and "Additional icons"). You are free to translate them into another language if required.
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
; NOTE: The following entry contains English phrases ("Create a Quick Launch icon" and "Additional icons"). You are free to translate them into another language if required.
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\opendict.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\pyexpat.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\_sre.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\_winreg.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\htmlc.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\python23.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\wxc.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\wxmsw24h.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\win32\dist\opendict\zlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\copying.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\OpenDict_LT_instrukcija.txt"; DestDir: "{app}"; Flags: isreadme
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\po\lt\opendict.mo"; DestDir: "{app}\locale\lt\"; Flags: ignoreversion
;Source: "C:\Program Files\OpenDict-dev\OpenDict-source\todo.txt"; DestDir: "{app}"; Flags: ignoreversion
;Source: "C:\Program Files\OpenDict-dev\OpenDict-source\doc\Design.txt"; DestDir: "{app}\doc\"; Flags: ignoreversion
;Source: "C:\Program Files\OpenDict-dev\OpenDict-source\doc\Manual.html"; DestDir: "{app}\doc\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\clear.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\hide.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\logo.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\icon.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\icon.png"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\search.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\right.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\left.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\plugin.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\register.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\group.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion
Source: "C:\Program Files\OpenDict-dev\OpenDict-source\pixmaps\stop.xpm"; DestDir: "{app}\pixmaps\"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\OpenDict"; Filename: "{app}\opendict.exe"
Name: "{userdesktop}\OpenDict"; Filename: "{app}\opendict.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\OpenDict"; Filename: "{app}\opendict.exe"; Tasks: quicklaunchicon

; [Messages]
; MessagesFile=compiler:lithuanian.isl

[Run]
; NOTE: The following entry contains an English phrase ("Launch"). You are free to translate it into another language if required.
Filename: "{app}\opendict.exe"; Description: "Launch OpenDict"; Flags: shellexec postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\OpenDict"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\OpenDict"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\OpenDict\Settings"; ValueType: string; ValueName: "Path"; ValueData: "{app}"
;Root: HKLM; Subkey: "Software\OpenDict"; Flags: uninsdeletekeyifempty
;Root: HKLM; Subkey: "Software\OpenDict"; Flags: uninsdeletekey
;Root: HKLM; Subkey: "Software\OpenDict\Settings"; ValueType: string; ValueName: "Path"; ValueData: "{app}"
