from pathlib import Path

from app.database import Database, Student, User, check_password
from sqlalchemy import select


def test_first_run_creates_admin_and_demo_data(tmp_path: Path) -> None:
    database = Database(tmp_path / "school.db")
    with database.Session() as session:
        admin = session.scalar(select(User).where(User.username == "admin"))
        students = session.scalars(select(Student)).all()
    assert admin is not None
    assert admin.is_default_password == 1
    assert check_password("admin123", admin.password_hash)
    assert len(students) >= 1


def test_next_code_is_monotonic(tmp_path: Path) -> None:
    database = Database(tmp_path / "school.db")
    with database.Session.begin() as session:
        first = database.next_code(session, Student, "student_code", "STU")
        session.add(Student(student_code=first, admission_number="TEST-001", first_name="Test", father_name="Parent"))
        second = database.next_code(session, Student, "student_code", "STU")
    assert first != second