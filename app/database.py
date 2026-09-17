from __future__ import annotations

import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

import bcrypt
from sqlalchemy import Date, DateTime, Float, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import BACKUPS_DIR, DATABASE_PATH, ensure_app_directories


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="Administrator", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)
    is_default_password: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    admission_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    father_name: Mapped[str] = mapped_column(String(120), nullable=False)
    class_name: Mapped[str] = mapped_column(String(40), default="Grade 1", nullable=False)
    section: Mapped[str] = mapped_column(String(10), default="A", nullable=False)
    gender: Mapped[str] = mapped_column(String(20), default="Male", nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)
    admission_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    qualification: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Fee(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    student_name: Mapped[str] = mapped_column(String(160), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(80), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Unpaid", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    receipt_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    student_name: Mapped[str] = mapped_column(String(160), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), default="Cash", nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    module: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="", nullable=False)


class Database:
    def __init__(self, path: Path = DATABASE_PATH) -> None:
        ensure_app_directories()
        self.path = path
        self.engine = create_engine(f"sqlite:///{path}", future=True)
        self.Session = sessionmaker(self.engine, expire_on_commit=False, class_=Session)
        Base.metadata.create_all(self.engine)
        self._seed_if_empty()

    def _seed_if_empty(self) -> None:
        with self.Session.begin() as session:
            if session.scalar(select(func.count(User.id))) == 0:
                session.add(
                    User(
                        user_code="USR-000001",
                        username="admin",
                        full_name="System Administrator",
                        password_hash=hash_password("admin123"),
                        role="Super Admin",
                        is_default_password=1,
                    )
                )
            if session.scalar(select(func.count(Setting.key))) == 0:
                defaults = {
                    "school_name_english": "Modern School Management System",
                    "school_name_pashto": "د عصري ښوونځي مدیریت سیستم",
                    "address": "Jalalabad, Nangarhar, Afghanistan",
                    "phone": "+93 700 000 000",
                    "email": "office@modern-school.local",
                    "academic_year": "2026",
                    "currency": "AFN",
                    "theme": "light",
                    "language": "ps",
                }
                session.add_all(Setting(key=k, value=v) for k, v in defaults.items())

            if session.scalar(select(func.count(Student.id))) == 0:
                students = [
                    ("STU-000001", "ADM-2026-001", "Ahmad Khan", "Mohammad Khan", "Grade 10", "A", "Male", "0700123456"),
                    ("STU-000002", "ADM-2026-002", "Mina Rahimi", "Abdul Rahim", "Grade 9", "B", "Female", "0700654321"),
                    ("STU-000003", "ADM-2026-003", "Farid Safi", "Hamid Safi", "Grade 8", "A", "Male", "0700789123"),
                    ("STU-000004", "ADM-2026-004", "Laila Noori", "Jamal Noori", "Grade 11", "A", "Female", "0700112233"),
                    ("STU-000005", "ADM-2026-005", "Samiullah Shinwari", "Wali Shinwari", "Grade 7", "C", "Male", "0700445566"),
                    ("STU-000006", "ADM-2026-006", "Maryam Waziri", "Zahir Waziri", "Grade 6", "B", "Female", "0700998877"),
                ]
                session.add_all(
                    Student(
                        student_code=row[0],
                        admission_number=row[1],
                        first_name=row[2],
                        father_name=row[3],
                        class_name=row[4],
                        section=row[5],
                        gender=row[6],
                        phone=row[7],
                    )
                    for row in students
                )
            if session.scalar(select(func.count(Teacher.id))) == 0:
                teachers = [
                    ("TCH-000001", "Dr. Nasir Ahmad", "Mathematics", "0700111000", "M.Ed Mathematics"),
                    ("TCH-000002", "Sahar Gul", "English", "0700222000", "B.A English Literature"),
                    ("TCH-000003", "Wali Mohammad", "Physics", "0700333000", "M.Sc Physics"),
                    ("TCH-000004", "Shukria Azizi", "Biology", "0700444000", "B.Sc Biology"),
                ]
                session.add_all(
                    Teacher(
                        teacher_code=row[0],
                        name=row[1],
                        subject=row[2],
                        phone=row[3],
                        qualification=row[4],
                    )
                    for row in teachers
                )
            if session.scalar(select(func.count(Fee.id))) == 0:
                session.add_all(
                    [
                        Fee(fee_code="FEE-000001", student_name="Ahmad Khan", fee_type="Monthly Fee", total_amount=2500, paid_amount=2500, due_date=date(2026, 9, 5), status="Paid"),
                        Fee(fee_code="FEE-000002", student_name="Mina Rahimi", fee_type="Monthly Fee", total_amount=2500, paid_amount=1500, due_date=date(2026, 9, 5), status="Partial"),
                        Fee(fee_code="FEE-000003", student_name="Farid Safi", fee_type="Monthly Fee", total_amount=2500, paid_amount=0, due_date=date(2026, 9, 5), status="Overdue"),
                        Fee(fee_code="FEE-000004", student_name="Laila Noori", fee_type="Exam Fee", total_amount=1200, paid_amount=1200, due_date=date(2026, 9, 12), status="Paid"),
                    ]
                )
            if session.scalar(select(func.count(Payment.id))) == 0:
                session.add_all(
                    [
                        Payment(payment_code="PAY-000001", receipt_number="REC-000001", student_name="Ahmad Khan", fee_type="Monthly Fee", amount=2500, payment_method="Cash", payment_date=date(2026, 9, 5)),
                        Payment(payment_code="PAY-000002", receipt_number="REC-000002", student_name="Mina Rahimi", fee_type="Monthly Fee", amount=1500, payment_method="Bank Transfer", payment_date=date(2026, 9, 6)),
                        Payment(payment_code="PAY-000003", receipt_number="REC-000003", student_name="Laila Noori", fee_type="Exam Fee", amount=1200, payment_method="Cash", payment_date=date(2026, 9, 12)),
                    ]
                )
            if session.scalar(select(func.count(Activity.id))) == 0:
                session.add_all(
                    [
                        Activity(action="CREATE", module="Students", description="New student Ahmad Khan admitted"),
                        Activity(action="PAYMENT", module="Finance", description="Payment REC-000003 received from Laila Noori"),
                        Activity(action="UPDATE", module="Attendance", description="Grade 10 attendance marked for today"),
                        Activity(action="CREATE", module="Teachers", description="Teacher Dr. Nasir Ahmad added"),
                    ]
                )

    def session(self) -> Session:
        return self.Session()

    def next_code(self, session: Session, model: type[Any], field: str, prefix: str) -> str:
        values = session.scalars(select(getattr(model, field)).order_by(getattr(model, field).desc())).all()
        largest = 0
        for value in values:
            try:
                largest = max(largest, int(str(value).split("-")[-1]))
            except (TypeError, ValueError):
                continue
        return f"{prefix}-{largest + 1:06d}"

    def log(self, session: Session, action: str, module: str, description: str) -> None:
        session.add(Activity(action=action, module=module, description=description))

    def setting(self, key: str, default: str = "") -> str:
        with self.Session() as session:
            item = session.get(Setting, key)
            return item.value if item else default

    def set_settings(self, values: dict[str, str]) -> None:
        with self.Session.begin() as session:
            for key, value in values.items():
                item = session.get(Setting, key)
                if item:
                    item.value = value
                else:
                    session.add(Setting(key=key, value=value))

    def backup(self) -> Path:
        ensure_app_directories()
        destination = BACKUPS_DIR / f"SchoolBackup_{datetime.now():%Y-%m-%d_%H-%M-%S}.db"
        shutil.copy2(self.path, destination)
        return destination


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False