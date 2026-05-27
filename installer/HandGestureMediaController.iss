; Inno Setup script for Hand Gesture Media Controller
; Build from repository root:
;   iscc installer\HandGestureMediaController.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif

#define MyAppName "Hand Gesture Media Controller"
#define MyAppExeName "HandGestureMediaController.exe"
#define MyAppPublisher "Hand Gesture Media Controller"

[Setup]
AppId={{A4E1A4A2-8B43-4A11-8C3F-68FC7ED8BF9A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\HandGestureMediaController
DefaultGroupName=Hand Gesture Media Controller
AllowNoIcons=yes
OutputDir=dist_installer
OutputBaseFilename=HandGestureMediaController-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\HandGestureMediaController\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Hand Gesture Media Controller"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Hand Gesture Media Controller"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Hand Gesture Media Controller"; Flags: nowait postinstall skipifsilent
