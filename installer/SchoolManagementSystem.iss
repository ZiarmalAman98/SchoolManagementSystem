#define MyAppName "Modern School Management System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Modern School Management System"
#define MyAppExeName "SchoolManagementSystem.exe"

[Setup]
AppId={{7D8F59D5-BB04-4D96-BF1D-2E1AF3C9AF0A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SchoolManagementSystem
DefaultGroupName={#MyAppName}
OutputDir=output
OutputBaseFilename=SchoolManagementSystem_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
WizardStyle=modern

[Files]
Source: "..\dist\SchoolManagementSystem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\School Management System"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\School Management System"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch School Management System"; Flags: nowait postinstall skipifsilent