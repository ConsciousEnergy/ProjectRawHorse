' Project RawHorse - VBS Launcher (for custom icon support)
' This VBScript launches RUN.bat and allows Windows to use a custom icon
' To set icon: Right-click → Create Shortcut → Properties → Change Icon → Browse to PRHLogo.ico

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
WshShell.CurrentDirectory = scriptDir

' Run the batch file
WshShell.Run Chr(34) & scriptDir & "\RUN.bat" & Chr(34), 1, False

' Clean up
Set WshShell = Nothing
Set fso = Nothing

