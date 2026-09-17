from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "Modern School Management System"
SHORT_NAME = "School Management System"
APP_VERSION = "1.0.0"


def app_data_dir() -> Path:
    """Return the per-user Windows data directory.

    LOCALAPPDATA is the correct location for mutable application data on
    Windows. The home directory fallback keeps development on Linux/macOS
    deterministic without ever writing beside the installed executable.
    """

    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / "SchoolManagementSystem"
    return Path.home() / ".local" / "share" / "SchoolManagementSystem"


DATA_DIR = app_data_dir()
DATABASE_DIR = DATA_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "school.db"
IMAGES_DIR = DATA_DIR / "images"
USERS_IMAGE_DIR = IMAGES_DIR / "users"
STUDENTS_IMAGE_DIR = IMAGES_DIR / "students"
TEACHERS_IMAGE_DIR = IMAGES_DIR / "teachers"
DOCUMENTS_DIR = DATA_DIR / "documents"
REPORTS_DIR = DATA_DIR / "reports"
BACKUPS_DIR = DATA_DIR / "backups"
LOGS_DIR = DATA_DIR / "logs"
SCHOOL_LOGO_PATH = IMAGES_DIR / "school_logo.png"


def ensure_app_directories() -> None:
    for directory in (
        DATABASE_DIR,
        IMAGES_DIR,
        USERS_IMAGE_DIR,
        STUDENTS_IMAGE_DIR,
        TEACHERS_IMAGE_DIR,
        DOCUMENTS_DIR,
        REPORTS_DIR,
        BACKUPS_DIR,
        LOGS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)