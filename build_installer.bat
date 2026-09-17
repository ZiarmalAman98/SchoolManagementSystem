@echo off
setlocal
cd /d "%~dp0"
call build.bat
if errorlevel 1 exit /b 1

where ISCC >nul 2>nul
if errorlevel 1 (
  echo Inno Setup Compiler (ISCC.exe) was not found.
  echo Install Inno Setup 6, then run this file again.
  exit /b 1
)

ISCC installer\SchoolManagementSystem.iss
if errorlevel 1 exit /b 1
echo Installer created at %CD%\installer\output\SchoolManagementSystem_Setup.exe