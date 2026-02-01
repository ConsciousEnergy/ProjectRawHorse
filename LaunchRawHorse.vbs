' ================================================================
' Project RawHorse - VBS Launcher (Windows)
' Double-click this file or create a shortcut with a custom icon
' ================================================================
'
' To create a desktop shortcut with custom icon:
' 1. Right-click this file → Create Shortcut
' 2. Move shortcut to Desktop
' 3. Right-click shortcut → Properties → Change Icon
' 4. Browse to PRHLogo.ico in this folder
' ================================================================

Option Explicit

Dim WshShell, fso, scriptDir, batFile

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
WshShell.CurrentDirectory = scriptDir

' Determine which batch file to run
' Prefer START.bat (guided) over RUN.bat (simple)
If fso.FileExists(scriptDir & "\START.bat") Then
    batFile = scriptDir & "\START.bat"
ElseIf fso.FileExists(scriptDir & "\RUN.bat") Then
    batFile = scriptDir & "\RUN.bat"
Else
    MsgBox "Could not find START.bat or RUN.bat in:" & vbCrLf & scriptDir, vbCritical, "Project RawHorse - Error"
    WScript.Quit 1
End If

' Run the batch file (1 = show window, False = don't wait)
WshShell.Run Chr(34) & batFile & Chr(34), 1, False

' Clean up
Set WshShell = Nothing
Set fso = Nothing
