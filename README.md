# Modern School Management System

An offline-first Windows desktop school operations system built with Python,
PySide6 and SQLite. It is designed for a school office that needs a reliable
daily workspace without an internet connection or cloud database.

## Included foundation

- Native PySide6 desktop interface with a modern sidebar, dashboard cards,
  accessible tables, search, light/dark themes and Pashto/English direction
  switching.
- Local SQLite database stored below `%LOCALAPPDATA%\SchoolManagementSystem\`.
- Secure bcrypt password hashes and an administrator login.
- Real CRUD for students and teachers.
- Real payment recording with generated payment and receipt numbers.
- Dashboard statistics backed by the database.
- CSV exports and a branded PDF operations brief.
- Local database backup.
- School identity and logo settings.
- User creation with role labels and forced first-login password change.

## Development setup

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The application also runs on Linux for development:

```bash
python3 run.py
```

## Default login

- Username: `admin`
- Password: `admin123`

The first successful login asks the administrator to replace the default
password with a private password of at least eight characters.

## Data locations

On Windows, active mutable data is never stored beside the installed program:

- Database: `%LOCALAPPDATA%\SchoolManagementSystem\data\school.db`
- Logo: `%LOCALAPPDATA%\SchoolManagementSystem\images\school_logo.png`
- Reports: `%LOCALAPPDATA%\SchoolManagementSystem\reports\`
- Backups: `%LOCALAPPDATA%\SchoolManagementSystem\backups\`
- Logs: `%LOCALAPPDATA%\SchoolManagementSystem\logs\`

## Build the Windows executable

Run `build.bat` on Windows. The one-folder build is written to:

`dist\SchoolManagementSystem\SchoolManagementSystem.exe`

To create the installer, install Inno Setup 6 and run `build_installer.bat`.
The installer is written to:

`installer\output\SchoolManagementSystem_Setup.exe`

Updates do not remove the database, images or backups because those files live
under the user data directory.

## Test

```bash
pytest -q
```

## Product direction

The application foundation is intentionally organized around reusable database,
branding, authentication and reporting services. Additional school modules can
be added without moving user data or replacing the database.