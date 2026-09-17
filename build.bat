@echo off
setlocal
cd /d "%~dp0"

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

if exist .venv\Scripts\python.exe (
  set PYTHON=.venv\Scripts\python.exe
) else if exist ..\.pythonlibs\Scripts\python.exe (
  set PYTHON=..\.pythonlibs\Scripts\python.exe
) else (
  set PYTHON=python
)

echo Installing requirements...
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo Building Windows executable...
%PYTHON% -m PyInstaller SchoolManagementSystem.spec --clean
if errorlevel 1 goto :fail

if exist dist\SchoolManagementSystem\SchoolManagementSystem.exe (
  echo.
  echo SUCCESS
  echo EXE: %CD%\dist\SchoolManagementSystem\SchoolManagementSystem.exe
  exit /b 0
)

:fail
echo.
echo BUILD FAILED
exit /b 1