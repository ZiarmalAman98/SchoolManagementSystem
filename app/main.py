from __future__ import annotations

import csv
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QDate, QLocale, QPoint, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap
from PySide6.QtPrintSupport import QPrintPreviewDialog
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from .config import APP_NAME, APP_VERSION, LOGS_DIR, REPORTS_DIR, SCHOOL_LOGO_PATH, ensure_app_directories
from .database import Activity, Database, Fee, Payment, Student, Teacher, User, check_password, hash_password
from .i18n import tr


logging.basicConfig(
    filename=str(LOGS_DIR / "application.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


NAV_ITEMS = [
    ("dashboard", "⌂"),
    ("students", "♙"),
    ("teachers", "◇"),
    ("finance", "₳"),
    ("reports", "▤"),
    ("users", "♙"),
    ("settings", "⚙"),
]


def money(value: float) -> str:
    return f"{value:,.0f} AFN"


def make_logo_pixmap(size: int = 64) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#dcecff"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 18, 18)
    painter.setBrush(QColor("#2979ff"))
    painter.drawRoundedRect(size * 0.28, size * 0.2, size * 0.44, size * 0.6, 8, 8)
    painter.setBrush(QColor("#eaf3ff"))
    painter.drawRect(size * 0.36, size * 0.34, size * 0.28, size * 0.06)
    painter.drawRect(size * 0.36, size * 0.47, size * 0.28, size * 0.06)
    painter.end()
    return pixmap


def load_school_logo(size: int = 64) -> QPixmap:
    if SCHOOL_LOGO_PATH.exists():
        pixmap = QPixmap(str(SCHOOL_LOGO_PATH))
        if not pixmap.isNull():
            return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return make_logo_pixmap(size)


class Card(QFrame):
    def __init__(self, object_name: str = "card", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)


class StatCard(Card):
    def __init__(self, title: str, value: str, detail: str, accent: str, icon: str) -> None:
        super().__init__()
        self.setMinimumHeight(132)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        top = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("muted")
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(34, 34)
        icon_label.setStyleSheet(f"background: {accent}; color: white; border-radius: 10px; font-size: 17px;")
        top.addWidget(title_label)
        top.addStretch()
        top.addWidget(icon_label)
        layout.addLayout(top)
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        layout.addWidget(value_label)
        detail_label = QLabel(detail)
        detail_label.setObjectName("positive")
        layout.addWidget(detail_label)


class Toast(QLabel):
    def __init__(self, parent: QWidget, message: str, error: bool = False) -> None:
        super().__init__(parent)
        self.setText(message)
        self.setObjectName("toastError" if error else "toast")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(42)
        self.setStyleSheet(
            f"padding: 10px 18px; border-radius: 12px; color: white; "
            f"background: {'#c73b55' if error else '#16856a'}; font-weight: 600;"
        )
        self.adjustSize()
        self.show()
        QTimer.singleShot(3200, self.deleteLater)


class LoginWindow(QWidget):
    logged_in = Signal(object)
    language_changed = Signal(str)

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.language = db.setting("language", "ps")
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(960, 620)
        self.setObjectName("loginWindow")
        self._build()
        self._apply_direction()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        brand = QWidget()
        brand.setObjectName("loginBrand")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(60, 64, 60, 54)
        logo = QLabel()
        logo.setPixmap(load_school_logo(92))
        logo.setFixedSize(92, 92)
        brand_layout.addWidget(logo)
        brand_layout.addSpacing(40)
        eyebrow = QLabel("SCHOOL OPERATIONS")
        eyebrow.setObjectName("eyebrow")
        brand_layout.addWidget(eyebrow)
        title = QLabel("Modern school\nmanagement.")
        title.setObjectName("loginTitle")
        brand_layout.addWidget(title)
        subtitle = QLabel("One calm workspace for students,\npeople, finance and daily decisions.")
        subtitle.setObjectName("loginSubtitle")
        brand_layout.addWidget(subtitle)
        brand_layout.addStretch()
        footer = QLabel(f"Offline-first · v{APP_VERSION}")
        footer.setObjectName("loginFooter")
        brand_layout.addWidget(footer)
        root.addWidget(brand, 1)

        form_wrap = QWidget()
        form_layout = QVBoxLayout(form_wrap)
        form_layout.setContentsMargins(72, 58, 72, 58)
        form_layout.setSpacing(14)
        form_layout.addStretch()
        heading = QLabel()
        heading.setObjectName("formTitle")
        heading.setText(tr(self.language, "welcome"))
        form_layout.addWidget(heading)
        intro = QLabel("Sign in to continue to your school workspace.")
        intro.setObjectName("muted")
        form_layout.addWidget(intro)
        form_layout.addSpacing(22)

        self.username = QLineEdit()
        self.username.setPlaceholderText("admin")
        self.username.setMinimumHeight(48)
        self.username.setObjectName("loginInput")
        form_layout.addWidget(QLabel(tr(self.language, "username")))
        form_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("••••••••")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(48)
        self.password.setObjectName("loginInput")
        self.password.returnPressed.connect(self.login)
        form_layout.addWidget(QLabel(tr(self.language, "password")))
        form_layout.addWidget(self.password)

        options = QHBoxLayout()
        self.remember = QCheckBox(tr(self.language, "remember"))
        self.remember.setObjectName("rememberCheck")
        options.addWidget(self.remember)
        options.addStretch()
        options.addWidget(QLabel(tr(self.language, "language")))
        self.language_combo = QComboBox()
        self.language_combo.addItem("پښتو", "ps")
        self.language_combo.addItem("English", "en")
        self.language_combo.setCurrentIndex(0 if self.language == "ps" else 1)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        options.addWidget(self.language_combo)
        form_layout.addLayout(options)
        form_layout.addSpacing(10)

        self.login_button = QPushButton(tr(self.language, "login"))
        self.login_button.setObjectName("primaryButton")
        self.login_button.setMinimumHeight(50)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)
        exit_button = QPushButton("Exit application")
        exit_button.setObjectName("ghostButton")
        exit_button.clicked.connect(QApplication.instance().quit)
        form_layout.addWidget(exit_button)
        hint = QLabel("Demo access: admin / admin123")
        hint.setObjectName("hint")
        form_layout.addWidget(hint)
        form_layout.addStretch()
        root.addWidget(form_wrap, 1)

    def _apply_direction(self) -> None:
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.language == "ps" else Qt.LayoutDirection.LeftToRight)

    def change_language(self, index: int) -> None:
        self.language = self.language_combo.itemData(index)
        self.db.set_settings({"language": self.language})
        self._apply_direction()
        self.findChild(QLabel, "formTitle").setText(tr(self.language, "welcome"))
        self.login_button.setText(tr(self.language, "login"))
        self.remember.setText(tr(self.language, "remember"))

    def login(self) -> None:
        username = self.username.text().strip()
        password = self.password.text()
        if not username or not password:
            Toast(self, "Please enter your username and password.", True)
            return
        with self.db.Session.begin() as session:
            user = session.scalar(select(User).where(User.username == username))
            if not user or user.status != "Active" or not check_password(password, user.password_hash):
                Toast(self, "The username or password is not correct.", True)
                return
            user.last_login = datetime.now()
            self.db.log(session, "LOGIN", "Authentication", f"{user.username} signed in")
            default_password = bool(user.is_default_password)
        self.logged_in.emit({"id": user.id, "username": user.username, "name": user.full_name, "role": user.role, "default_password": default_password})


class ChangePasswordDialog(QDialog):
    def __init__(self, db: Database, user_id: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self.setWindowTitle("Change your password")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.current = QLineEdit()
        self.current.setEchoMode(QLineEdit.EchoMode.Password)
        self.new = QLineEdit()
        self.new.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Current password", self.current)
        form.addRow("New password", self.new)
        form.addRow("Confirm password", self.confirm)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self) -> None:
        if len(self.new.text()) < 8:
            QMessageBox.warning(self, "Password too short", "Use at least 8 characters.")
            return
        if self.new.text() != self.confirm.text():
            QMessageBox.warning(self, "Passwords do not match", "The confirmation must match the new password.")
            return
        with self.db.Session.begin() as session:
            user = session.get(User, self.user_id)
            if not user or not check_password(self.current.text(), user.password_hash):
                QMessageBox.warning(self, "Could not change password", "The current password is not correct.")
                return
            user.password_hash = hash_password(self.new.text())
            user.is_default_password = 0
            self.db.log(session, "PASSWORD_CHANGED", "Users", f"Password changed for {user.username}")
        self.accept()


class BasePage(QWidget):
    toast_parent: QWidget | None = None

    def notify(self, message: str, error: bool = False) -> None:
        if self.toast_parent:
            Toast(self.toast_parent, message, error)


class DashboardPage(BasePage):
    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__()
        self.db = db
        self.main_window = main_window
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        heading = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        heading.addWidget(self.title)
        heading.addStretch()
        refresh = QPushButton("↻  Refresh")
        refresh.setObjectName("ghostButton")
        refresh.clicked.connect(self.refresh)
        heading.addWidget(refresh)
        layout.addLayout(heading)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("muted")
        layout.addWidget(self.subtitle)
        self.stats = QGridLayout()
        self.stats.setHorizontalSpacing(14)
        self.stats.setVerticalSpacing(14)
        layout.addLayout(self.stats)
        lower = QHBoxLayout()
        lower.setSpacing(18)
        activity_card = Card()
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(22, 20, 22, 18)
        activity_heading = QHBoxLayout()
        self.activity_title = QLabel()
        self.activity_title.setObjectName("sectionTitle")
        activity_heading.addWidget(self.activity_title)
        activity_heading.addStretch()
        activity_heading.addWidget(QLabel("LIVE"))
        activity_layout.addLayout(activity_heading)
        self.activity_list = QListWidget()
        self.activity_list.setObjectName("activityList")
        activity_layout.addWidget(self.activity_list)
        lower.addWidget(activity_card, 3)

        pulse_card = Card()
        pulse_layout = QVBoxLayout(pulse_card)
        pulse_layout.setContentsMargins(22, 20, 22, 18)
        pulse_layout.addWidget(QLabel("Daily pulse", objectName="sectionTitle"))
        self.pulse_label = QLabel()
        self.pulse_label.setWordWrap(True)
        self.pulse_label.setObjectName("pulseText")
        pulse_layout.addWidget(self.pulse_label)
        pulse_layout.addStretch()
        quick = QPushButton("＋  Add a student")
        quick.setObjectName("primaryButton")
        quick.clicked.connect(lambda: self.main_window.show_page("students", add=True))
        pulse_layout.addWidget(quick)
        lower.addWidget(pulse_card, 2)
        layout.addLayout(lower)
        layout.addStretch()

    def refresh(self) -> None:
        with self.db.Session() as session:
            student_count = session.scalar(select(func.count(Student.id))) or 0
            teacher_count = session.scalar(select(func.count(Teacher.id))) or 0
            pending = session.scalar(select(func.coalesce(func.sum(Fee.total_amount - Fee.paid_amount), 0)).where(Fee.total_amount > Fee.paid_amount)) or 0
            today_income = session.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.payment_date == date.today())) or 0
            activities = session.scalars(select(Activity).order_by(Activity.created_at.desc()).limit(6)).all()
        self.title.setText(f"{tr(self.main_window.language, 'welcome')}, {self.main_window.current_user['name'].split()[0]}")
        self.subtitle.setText(f"{tr(self.main_window.language, 'school_overview')}  ·  {date.today():%d %b %Y}")
        self.activity_title.setText(tr(self.main_window.language, "recent_activity"))
        self._clear_layout(self.stats)
        cards = [
            (tr(self.main_window.language, "total_students"), str(student_count), "↑ 12% this term", "#2979ff", "♙"),
            (tr(self.main_window.language, "total_teachers"), str(teacher_count), "All active", "#7d5cff", "◇"),
            (tr(self.main_window.language, "pending_fees"), money(float(pending)), "Needs follow-up", "#e99a2f", "₳"),
            (tr(self.main_window.language, "today_income"), money(float(today_income)), "Collected today", "#159a7c", "↗"),
        ]
        for index, card_data in enumerate(cards):
            self.stats.addWidget(StatCard(*card_data), 0, index)
        self.activity_list.clear()
        for activity in activities:
            item = QListWidgetItem(f"{activity.description}\n{activity.created_at:%H:%M}  ·  {activity.module}")
            item.setData(Qt.ItemDataRole.UserRole, activity.id)
            self.activity_list.addItem(item)
        self.pulse_label.setText(
            "Attendance is ready for today. Fees are in a healthy collection cycle, "
            "and the most recent activity has been synchronized locally."
        )

    @staticmethod
    def _clear_layout(layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class RecordsPage(BasePage):
    columns: list[str] = []

    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.toast_parent = main_window
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(18)
        top = QHBoxLayout()
        self.heading = QLabel()
        self.heading.setObjectName("pageTitle")
        top.addWidget(self.heading)
        top.addStretch()
        self.search = QLineEdit()
        self.search.setObjectName("searchInput")
        self.search.setPlaceholderText("⌕  Search records")
        self.search.setMinimumWidth(300)
        self.search.textChanged.connect(self.refresh)
        top.addWidget(self.search)
        self.add_button = QPushButton("＋  Add record")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.add_record)
        top.addWidget(self.add_button)
        outer.addLayout(top)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("muted")
        outer.addWidget(self.subtitle)
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.edit_selected)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        card_layout.addWidget(self.table)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(16, 10, 16, 12)
        self.count_label = QLabel()
        self.count_label.setObjectName("muted")
        bottom.addWidget(self.count_label)
        bottom.addStretch()
        refresh = QPushButton("↻  Refresh")
        refresh.setObjectName("ghostButton")
        refresh.clicked.connect(self.refresh)
        bottom.addWidget(refresh)
        edit = QPushButton("Edit selected")
        edit.setObjectName("ghostButton")
        edit.clicked.connect(self.edit_selected)
        bottom.addWidget(edit)
        delete = QPushButton("Delete selected")
        delete.setObjectName("dangerButton")
        delete.clicked.connect(self.delete_selected)
        bottom.addWidget(delete)
        card_layout.addLayout(bottom)
        outer.addWidget(card)

    def selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def edit_selected(self) -> None:
        identifier = self.selected_id()
        if identifier is None:
            self.notify("Select a record first.", True)
            return
        self.edit_record(identifier)

    def delete_selected(self) -> None:
        identifier = self.selected_id()
        if identifier is None:
            self.notify("Select a record first.", True)
            return
        if QMessageBox.question(self, "Confirm deletion", "Delete the selected record? This cannot be undone.") != QMessageBox.StandardButton.Yes:
            return
        self.delete_record(identifier)

    def set_row(self, row: int, values: list[str], identifier: int) -> None:
        self.table.insertRow(row)
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 0:
                item.setData(Qt.ItemDataRole.UserRole, identifier)
            self.table.setItem(row, column, item)

    def refresh(self) -> None:
        raise NotImplementedError

    def add_record(self) -> None:
        raise NotImplementedError

    def edit_record(self, identifier: int) -> None:
        raise NotImplementedError

    def delete_record(self, identifier: int) -> None:
        raise NotImplementedError


class StudentDialog(QDialog):
    def __init__(self, db: Database, student: Student | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.student = student
        self.setWindowTitle("Edit student" if student else "Add student")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.first_name = QLineEdit(student.first_name if student else "")
        self.father_name = QLineEdit(student.father_name if student else "")
        self.admission = QLineEdit(student.admission_number if student else "")
        self.class_name = QComboBox()
        self.class_name.addItems([f"Grade {i}" for i in range(1, 13)])
        if student:
            self.class_name.setCurrentText(student.class_name)
        self.section = QComboBox()
        self.section.addItems(["A", "B", "C", "D"])
        if student:
            self.section.setCurrentText(student.section)
        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female"])
        if student:
            self.gender.setCurrentText(student.gender)
        self.phone = QLineEdit(student.phone if student else "")
        form.addRow("Student name *", self.first_name)
        form.addRow("Father name *", self.father_name)
        form.addRow("Admission number *", self.admission)
        form.addRow("Class", self.class_name)
        form.addRow("Section", self.section)
        form.addRow("Gender", self.gender)
        form.addRow("Phone", self.phone)
        layout.addLayout(form)
        hint = QLabel("Required fields are marked with *. Admission number must be unique.")
        hint.setObjectName("hint")
        layout.addWidget(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self) -> None:
        if not self.first_name.text().strip() or not self.father_name.text().strip() or not self.admission.text().strip():
            QMessageBox.warning(self, "Missing information", "Student name, father name and admission number are required.")
            return
        try:
            with self.db.Session.begin() as session:
                if self.student:
                    record = session.get(Student, self.student.id)
                else:
                    record = Student(
                        student_code=self.db.next_code(session, Student, "student_code", "STU"),
                        admission_number=self.admission.text().strip(),
                        first_name=self.first_name.text().strip(),
                        father_name=self.father_name.text().strip(),
                        class_name=self.class_name.currentText(),
                        section=self.section.currentText(),
                        gender=self.gender.currentText(),
                        phone=self.phone.text().strip(),
                    )
                    session.add(record)
                if not record:
                    return
                record.first_name = self.first_name.text().strip()
                record.father_name = self.father_name.text().strip()
                record.admission_number = self.admission.text().strip()
                record.class_name = self.class_name.currentText()
                record.section = self.section.currentText()
                record.gender = self.gender.currentText()
                record.phone = self.phone.text().strip()
                self.db.log(session, "UPDATE" if self.student else "CREATE", "Students", f"{record.first_name} saved")
            self.accept()
        except IntegrityError:
            QMessageBox.warning(self, "Duplicate admission number", "This admission number is already in use.")


class StudentsPage(RecordsPage):
    columns = ["ID", "Student", "Father name", "Class", "Section", "Phone", "Status"]

    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__(db, main_window)
        self.heading.setText(tr(main_window.language, "students"))
        self.subtitle.setText("Search, review and maintain student records with local database persistence.")
        self.refresh()

    def refresh(self) -> None:
        query = self.search.text().strip().lower()
        with self.db.Session() as session:
            statement = select(Student).order_by(Student.id.desc())
            if query:
                statement = statement.where(
                    or_(
                        func.lower(Student.first_name).contains(query),
                        func.lower(Student.father_name).contains(query),
                        func.lower(Student.admission_number).contains(query),
                        func.lower(Student.student_code).contains(query),
                    )
                )
            records = session.scalars(statement).all()
        self.table.setRowCount(0)
        for row, student in enumerate(records):
            self.set_row(row, [student.student_code, student.first_name, student.father_name, student.class_name, student.section, student.phone or "—", student.status], student.id)
        self.count_label.setText(f"{len(records)} students")

    def add_record(self) -> None:
        dialog = StudentDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.notify("Student saved successfully.")

    def edit_record(self, identifier: int) -> None:
        with self.db.Session() as session:
            student = session.get(Student, identifier)
            if not student:
                return
            data = Student(
                id=student.id,
                student_code=student.student_code,
                admission_number=student.admission_number,
                first_name=student.first_name,
                father_name=student.father_name,
                class_name=student.class_name,
                section=student.section,
                gender=student.gender,
                phone=student.phone,
                status=student.status,
                admission_date=student.admission_date,
            )
        if StudentDialog(self.db, data, self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.notify("Student updated successfully.")

    def delete_record(self, identifier: int) -> None:
        with self.db.Session.begin() as session:
            student = session.get(Student, identifier)
            if student:
                self.db.log(session, "DELETE", "Students", f"{student.first_name} deleted")
                session.delete(student)
        self.refresh()
        self.notify("Student deleted.")


class TeacherDialog(QDialog):
    def __init__(self, db: Database, teacher: Teacher | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.teacher = teacher
        self.setWindowTitle("Edit teacher" if teacher else "Add teacher")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit(teacher.name if teacher else "")
        self.subject = QLineEdit(teacher.subject if teacher else "")
        self.phone = QLineEdit(teacher.phone if teacher else "")
        self.qualification = QLineEdit(teacher.qualification if teacher else "")
        form.addRow("Full name *", self.name)
        form.addRow("Primary subject *", self.subject)
        form.addRow("Phone", self.phone)
        form.addRow("Qualification", self.qualification)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self) -> None:
        if not self.name.text().strip() or not self.subject.text().strip():
            QMessageBox.warning(self, "Missing information", "Full name and primary subject are required.")
            return
        with self.db.Session.begin() as session:
            if self.teacher:
                record = session.get(Teacher, self.teacher.id)
            else:
                record = Teacher(
                    teacher_code=self.db.next_code(session, Teacher, "teacher_code", "TCH"),
                    name=self.name.text().strip(),
                    subject=self.subject.text().strip(),
                )
                session.add(record)
            if not record:
                return
            record.name = self.name.text().strip()
            record.subject = self.subject.text().strip()
            record.phone = self.phone.text().strip()
            record.qualification = self.qualification.text().strip()
            self.db.log(session, "UPDATE" if self.teacher else "CREATE", "Teachers", f"{record.name} saved")
        self.accept()


class TeachersPage(RecordsPage):
    columns = ["ID", "Teacher", "Subject", "Qualification", "Phone", "Status"]

    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__(db, main_window)
        self.heading.setText(tr(main_window.language, "teachers"))
        self.subtitle.setText("Keep teaching staff, qualifications and contact details current.")
        self.refresh()

    def refresh(self) -> None:
        query = self.search.text().strip().lower()
        with self.db.Session() as session:
            statement = select(Teacher).order_by(Teacher.id.desc())
            if query:
                statement = statement.where(
                    or_(
                        func.lower(Teacher.name).contains(query),
                        func.lower(Teacher.subject).contains(query),
                        func.lower(Teacher.teacher_code).contains(query),
                    )
                )
            records = session.scalars(statement).all()
        self.table.setRowCount(0)
        for row, teacher in enumerate(records):
            self.set_row(row, [teacher.teacher_code, teacher.name, teacher.subject, teacher.qualification or "—", teacher.phone or "—", teacher.status], teacher.id)
        self.count_label.setText(f"{len(records)} teachers")

    def add_record(self) -> None:
        if TeacherDialog(self.db, parent=self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.notify("Teacher saved successfully.")

    def edit_record(self, identifier: int) -> None:
        with self.db.Session() as session:
            teacher = session.get(Teacher, identifier)
            if not teacher:
                return
            data = Teacher(id=teacher.id, teacher_code=teacher.teacher_code, name=teacher.name, subject=teacher.subject, phone=teacher.phone, qualification=teacher.qualification, status=teacher.status)
        if TeacherDialog(self.db, data, self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.notify("Teacher updated successfully.")

    def delete_record(self, identifier: int) -> None:
        with self.db.Session.begin() as session:
            teacher = session.get(Teacher, identifier)
            if teacher:
                self.db.log(session, "DELETE", "Teachers", f"{teacher.name} deleted")
                session.delete(teacher)
        self.refresh()
        self.notify("Teacher deleted.")


class PaymentDialog(QDialog):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Record payment")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.student = QLineEdit()
        self.fee_type = QComboBox()
        self.fee_type.addItems(["Monthly Fee", "Admission Fee", "Exam Fee", "Transport Fee", "Library Fee", "Other Fee"])
        self.amount = QSpinBox()
        self.amount.setRange(1, 10_000_000)
        self.amount.setSuffix(" AFN")
        self.method = QComboBox()
        self.method.addItems(["Cash", "Bank Transfer", "Mobile Money"])
        form.addRow("Student *", self.student)
        form.addRow("Fee type", self.fee_type)
        form.addRow("Amount *", self.amount)
        form.addRow("Payment method", self.method)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self) -> None:
        if not self.student.text().strip() or self.amount.value() <= 0:
            QMessageBox.warning(self, "Missing information", "Student and a positive amount are required.")
            return
        with self.db.Session.begin() as session:
            payment = Payment(
                payment_code=self.db.next_code(session, Payment, "payment_code", "PAY"),
                receipt_number=self.db.next_code(session, Payment, "receipt_number", "REC"),
                student_name=self.student.text().strip(),
                fee_type=self.fee_type.currentText(),
                amount=float(self.amount.value()),
                payment_method=self.method.currentText(),
            )
            session.add(payment)
            self.db.log(session, "PAYMENT", "Finance", f"{payment.receipt_number} received from {payment.student_name}")
        self.accept()


class FinancePage(BasePage):
    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.toast_parent = main_window
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QHBoxLayout()
        title = QLabel(tr(self.main_window.language, "finance"))
        title.setObjectName("pageTitle")
        heading.addWidget(title)
        heading.addStretch()
        record = QPushButton("＋  Record payment")
        record.setObjectName("primaryButton")
        record.clicked.connect(self.add_payment)
        heading.addWidget(record)
        layout.addLayout(heading)
        sub = QLabel("Track collection, outstanding balances and recent receipts in AFN.")
        sub.setObjectName("muted")
        layout.addWidget(sub)
        self.summary = QGridLayout()
        self.summary.setSpacing(14)
        layout.addLayout(self.summary)
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Receipt", "Student", "Fee type", "Amount", "Method", "Date"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        card_layout.addWidget(self.table)
        layout.addWidget(card)

    def refresh(self) -> None:
        with self.db.Session() as session:
            total_fees = session.scalar(select(func.coalesce(func.sum(Fee.total_amount), 0))) or 0
            paid = session.scalar(select(func.coalesce(func.sum(Payment.amount), 0))) or 0
            pending = float(total_fees) - float(paid)
            payments = session.scalars(select(Payment).order_by(Payment.payment_date.desc(), Payment.id.desc()).limit(20)).all()
        while self.summary.count():
            item = self.summary.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.summary.addWidget(StatCard("Total fees", money(float(total_fees)), "Current records", "#2979ff", "₳"), 0, 0)
        self.summary.addWidget(StatCard("Collected", money(float(paid)), "Received payments", "#159a7c", "↗"), 0, 1)
        self.summary.addWidget(StatCard("Outstanding", money(max(pending, 0)), "Requires follow-up", "#e99a2f", "!"), 0, 2)
        self.table.setRowCount(0)
        for row, payment in enumerate(payments):
            self.table.insertRow(row)
            values = [payment.receipt_number, payment.student_name, payment.fee_type, money(payment.amount), payment.payment_method, payment.payment_date.isoformat()]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

    def add_payment(self) -> None:
        if PaymentDialog(self.db, self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.notify("Payment recorded. Receipt number generated.")


class ReportsPage(BasePage):
    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.toast_parent = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel(tr(main_window.language, "reports"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        sub = QLabel("Export current operational data for your school records.")
        sub.setObjectName("muted")
        layout.addWidget(sub)
        grid = QGridLayout()
        grid.setSpacing(16)
        reports = [
            ("Student directory", "All students with class and contact details", self.export_students),
            ("Teacher directory", "Teaching staff, subjects and qualification", self.export_teachers),
            ("Fee collection", "Fee balances and outstanding amounts", self.export_fees),
            ("Payment receipts", "Recent payment activity and receipts", self.export_payments),
        ]
        for index, (name, description, callback) in enumerate(reports):
            card = Card()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(22, 20, 22, 20)
            card_layout.addWidget(QLabel(name, objectName="sectionTitle"))
            label = QLabel(description)
            label.setObjectName("muted")
            label.setWordWrap(True)
            card_layout.addWidget(label)
            card_layout.addStretch()
            export = QPushButton("Export CSV  →")
            export.setObjectName("ghostButton")
            export.clicked.connect(callback)
            card_layout.addWidget(export)
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)
        pdf_card = Card()
        pdf_layout = QHBoxLayout(pdf_card)
        pdf_layout.setContentsMargins(22, 18, 22, 18)
        pdf_layout.addWidget(QLabel("School operations brief", objectName="sectionTitle"))
        pdf_layout.addWidget(QLabel("Generate a branded PDF snapshot of students, teachers and finance.", objectName="muted"))
        pdf_layout.addStretch()
        pdf = QPushButton("Generate PDF")
        pdf.setObjectName("primaryButton")
        pdf.clicked.connect(self.export_pdf)
        pdf_layout.addWidget(pdf)
        layout.addWidget(pdf_card)
        layout.addStretch()

    def _save_csv(self, name: str, headers: list[str], rows: list[list[str]]) -> None:
        ensure_app_directories()
        path, _ = QFileDialog.getSaveFileName(self, "Save report", str(REPORTS_DIR / name), "CSV files (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)
        self.notify(f"Report exported to {Path(path).name}.")

    def export_students(self) -> None:
        with self.db.Session() as session:
            records = session.scalars(select(Student).order_by(Student.student_code)).all()
        self._save_csv("students.csv", ["ID", "Student", "Father", "Class", "Section", "Phone", "Status"], [[s.student_code, s.first_name, s.father_name, s.class_name, s.section, s.phone, s.status] for s in records])

    def export_teachers(self) -> None:
        with self.db.Session() as session:
            records = session.scalars(select(Teacher).order_by(Teacher.teacher_code)).all()
        self._save_csv("teachers.csv", ["ID", "Teacher", "Subject", "Qualification", "Phone", "Status"], [[t.teacher_code, t.name, t.subject, t.qualification, t.phone, t.status] for t in records])

    def export_fees(self) -> None:
        with self.db.Session() as session:
            records = session.scalars(select(Fee).order_by(Fee.due_date)).all()
        self._save_csv("fees.csv", ["ID", "Student", "Type", "Total", "Paid", "Remaining", "Due", "Status"], [[f.fee_code, f.student_name, f.fee_type, str(f.total_amount), str(f.paid_amount), str(f.total_amount - f.paid_amount), f.due_date.isoformat(), f.status] for f in records])

    def export_payments(self) -> None:
        with self.db.Session() as session:
            records = session.scalars(select(Payment).order_by(Payment.payment_date.desc())).all()
        self._save_csv("payments.csv", ["Receipt", "Student", "Type", "Amount", "Method", "Date"], [[p.receipt_number, p.student_name, p.fee_type, str(p.amount), p.payment_method, p.payment_date.isoformat()] for p in records])

    def export_pdf(self) -> None:
        ensure_app_directories()
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF report", str(REPORTS_DIR / "school_operations_brief.pdf"), "PDF files (*.pdf)")
        if not path:
            return
        with self.db.Session() as session:
            student_count = session.scalar(select(func.count(Student.id))) or 0
            teacher_count = session.scalar(select(func.count(Teacher.id))) or 0
            payments = session.scalars(select(Payment).order_by(Payment.payment_date.desc()).limit(8)).all()
            school = self.db.setting("school_name_english", APP_NAME)
            address = self.db.setting("address", "")
        document = SimpleDocTemplate(path, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
        styles = getSampleStyleSheet()
        story = [Paragraph(school, styles["Title"]), Paragraph(address, styles["Normal"]), Spacer(1, 18)]
        story.append(Paragraph(f"Operations brief · {datetime.now():%d %B %Y}", styles["Heading2"]))
        story.append(Paragraph(f"Students: {student_count} · Teachers: {teacher_count}", styles["Normal"]))
        story.append(Spacer(1, 16))
        data = [["Receipt", "Student", "Type", "Amount", "Date"]] + [[p.receipt_number, p.student_name, p.fee_type, money(p.amount), p.payment_date.isoformat()] for p in payments]
        table = Table(data, colWidths=[72, 150, 100, 80, 75])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#15304b")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d5dfe8")), ("PADDING", (0, 0), (-1, -1), 7)]))
        story.append(table)
        document.build(story)
        self.notify(f"PDF exported to {Path(path).name}.")


class UserDialog(QDialog):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Add user")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.role = QComboBox()
        self.role.addItems(["Administrator", "Principal", "Teacher", "Accountant", "Viewer"])
        form.addRow("Full name *", self.name)
        form.addRow("Username *", self.username)
        form.addRow("Temporary password *", self.password)
        form.addRow("Role", self.role)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self) -> None:
        if not self.name.text().strip() or not self.username.text().strip() or len(self.password.text()) < 8:
            QMessageBox.warning(self, "Missing information", "Name, username and a password of at least 8 characters are required.")
            return
        try:
            with self.db.Session.begin() as session:
                user = User(
                    user_code=self.db.next_code(session, User, "user_code", "USR"),
                    username=self.username.text().strip(),
                    full_name=self.name.text().strip(),
                    password_hash=hash_password(self.password.text()),
                    role=self.role.currentText(),
                    is_default_password=0,
                )
                session.add(user)
                self.db.log(session, "CREATE", "Users", f"{user.username} created")
            self.accept()
        except IntegrityError:
            QMessageBox.warning(self, "Duplicate username", "This username is already in use.")


class UsersPage(BasePage):
    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.toast_parent = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QHBoxLayout()
        title = QLabel(tr(main_window.language, "users"))
        title.setObjectName("pageTitle")
        heading.addWidget(title)
        heading.addStretch()
        add = QPushButton("＋  Add user")
        add.setObjectName("primaryButton")
        add.clicked.connect(self.add_user)
        heading.addWidget(add)
        layout.addLayout(heading)
        sub = QLabel("Access is role-based. Passwords are stored as secure hashes, never plain text.")
        sub.setObjectName("muted")
        layout.addWidget(sub)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Username", "Role", "Last login"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        with self.db.Session() as session:
            users = session.scalars(select(User).order_by(User.id)).all()
        self.table.setRowCount(0)
        for row, user in enumerate(users):
            self.table.insertRow(row)
            values = [user.user_code, user.full_name, user.username, user.role, user.last_login.strftime("%d %b %Y %H:%M") if user.last_login else "Never"]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

    def add_user(self) -> None:
        if UserDialog(self.db, self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.notify("User created with role permissions.")


class SettingsPage(BasePage):
    def __init__(self, db: Database, main_window: "MainWindow") -> None:
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.toast_parent = main_window
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel(tr(self.main_window.language, "settings"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        sub = QLabel("School identity, language, theme and local data protection.")
        sub.setObjectName("muted")
        layout.addWidget(sub)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 12, 0)
        identity = Card()
        identity_layout = QVBoxLayout(identity)
        identity_layout.setContentsMargins(24, 20, 24, 24)
        identity_layout.addWidget(QLabel(tr(self.main_window.language, "school_information"), objectName="sectionTitle"))
        form = QFormLayout()
        self.school_name = QLineEdit(self.db.setting("school_name_english"))
        self.school_name_pashto = QLineEdit(self.db.setting("school_name_pashto"))
        self.address = QLineEdit(self.db.setting("address"))
        self.phone = QLineEdit(self.db.setting("phone"))
        self.email = QLineEdit(self.db.setting("email"))
        self.academic_year = QLineEdit(self.db.setting("academic_year"))
        form.addRow("School name (English)", self.school_name)
        form.addRow("School name (Pashto)", self.school_name_pashto)
        form.addRow("Address", self.address)
        form.addRow("Phone", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Academic year", self.academic_year)
        identity_layout.addLayout(form)
        logo_row = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(load_school_logo(70))
        logo.setFixedSize(80, 80)
        logo_row.addWidget(logo)
        logo_row.addWidget(QLabel("School logo is used on dashboards and generated reports.", objectName="muted"))
        logo_row.addStretch()
        upload = QPushButton("Upload logo")
        upload.setObjectName("ghostButton")
        upload.clicked.connect(self.upload_logo)
        logo_row.addWidget(upload)
        identity_layout.addLayout(logo_row)
        content_layout.addWidget(identity)
        preferences = Card()
        pref_layout = QFormLayout(preferences)
        pref_layout.setContentsMargins(24, 20, 24, 20)
        self.language = QComboBox()
        self.language.addItem("پښتو", "ps")
        self.language.addItem("English", "en")
        self.language.setCurrentIndex(0 if self.main_window.language == "ps" else 1)
        self.theme = QComboBox()
        self.theme.addItems(["Light", "Dark"])
        self.theme.setCurrentText(self.db.setting("theme", "light").title())
        pref_layout.addRow("Interface language", self.language)
        pref_layout.addRow("Theme", self.theme)
        content_layout.addWidget(preferences)
        backup = Card()
        backup_layout = QHBoxLayout(backup)
        backup_layout.setContentsMargins(24, 20, 24, 20)
        backup_layout.addWidget(QLabel("Local backup", objectName="sectionTitle"))
        backup_layout.addWidget(QLabel("Create a safe copy of the SQLite database in the backup folder.", objectName="muted"))
        backup_layout.addStretch()
        create = QPushButton("Create backup")
        create.setObjectName("primaryButton")
        create.clicked.connect(self.create_backup)
        backup_layout.addWidget(create)
        content_layout.addWidget(backup)
        save = QPushButton("Save settings")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save_settings)
        content_layout.addWidget(save)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def save_settings(self) -> None:
        values = {
            "school_name_english": self.school_name.text().strip(),
            "school_name_pashto": self.school_name_pashto.text().strip(),
            "address": self.address.text().strip(),
            "phone": self.phone.text().strip(),
            "email": self.email.text().strip(),
            "academic_year": self.academic_year.text().strip(),
            "language": self.language.currentData(),
            "theme": self.theme.currentText().lower(),
        }
        self.db.set_settings(values)
        self.main_window.set_language(values["language"])
        self.main_window.apply_theme(values["theme"])
        self.notify("Settings saved successfully.")

    def upload_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose school logo", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if not path:
            return
        from PIL import Image

        try:
            with Image.open(path) as image:
                image.convert("RGBA").save(SCHOOL_LOGO_PATH, "PNG")
            self.notify("School logo updated.")
        except Exception:
            self.notify("The selected image could not be used.", True)

    def create_backup(self) -> None:
        path = self.db.backup()
        self.notify(f"Backup created: {path.name}")


class MainWindow(QMainWindow):
    def __init__(self, db: Database, current_user: dict[str, object]) -> None:
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.language = db.setting("language", "ps")
        self.setWindowTitle(f"{APP_NAME} · {current_user['name']}")
        self.setMinimumSize(1180, 740)
        self.resize(1440, 900)
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        self._build()
        self.apply_theme(db.setting("theme", "light"))
        if current_user.get("default_password"):
            QTimer.singleShot(400, self.force_password_change)

    def _build(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.sidebar = self._build_sidebar()
        root.addWidget(self.sidebar)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 22, 34, 26)
        content_layout.setSpacing(20)
        header = QHBoxLayout()
        self.breadcrumb = QLabel("Dashboard")
        self.breadcrumb.setObjectName("breadcrumb")
        header.addWidget(self.breadcrumb)
        header.addStretch()
        global_search = QLineEdit()
        global_search.setPlaceholderText("⌕  Search across school records")
        global_search.setObjectName("globalSearch")
        global_search.setMinimumWidth(300)
        global_search.returnPressed.connect(lambda: self.global_search(global_search.text()))
        header.addWidget(global_search)
        self.user_badge = QPushButton(f"{self.current_user['name']}  ·  {self.current_user['role']}")
        self.user_badge.setObjectName("userBadge")
        self.user_badge.clicked.connect(self.force_password_change)
        header.addWidget(self.user_badge)
        content_layout.addLayout(header)
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        root.addWidget(content, 1)
        self.addAction(self._shortcut("Ctrl+Q", QApplication.instance().quit))
        self.addAction(self._shortcut("F5", self.refresh_current))
        self.show_page("dashboard")

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(252)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 20)
        layout.setSpacing(8)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(load_school_logo(42))
        logo.setFixedSize(46, 46)
        brand.addWidget(logo)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        brand_text.addWidget(QLabel("MODERN", objectName="brandKicker"))
        brand_text.addWidget(QLabel("School OS", objectName="brandName"))
        brand.addLayout(brand_text)
        layout.addLayout(brand)
        layout.addSpacing(30)
        for key, icon in NAV_ITEMS:
            button = QPushButton(f"{icon}   {tr(self.language, key)}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, page=key: self.show_page(page))
            self.nav_buttons[key] = button
            layout.addWidget(button)
        layout.addStretch()
        help_card = QFrame()
        help_card.setObjectName("sidebarHelp")
        help_layout = QVBoxLayout(help_card)
        help_layout.addWidget(QLabel("Local & secure", objectName="helpTitle"))
        help_layout.addWidget(QLabel("Your school data stays on this computer.", objectName="helpText"))
        layout.addWidget(help_card)
        logout = QPushButton(f"↪   {tr(self.language, 'logout')}")
        logout.setObjectName("logoutButton")
        logout.clicked.connect(self.logout)
        layout.addWidget(logout)
        return sidebar

    def show_page(self, key: str, add: bool = False) -> None:
        if key not in self.pages:
            builders: dict[str, Callable[[], QWidget]] = {
                "dashboard": lambda: DashboardPage(self.db, self),
                "students": lambda: StudentsPage(self.db, self),
                "teachers": lambda: TeachersPage(self.db, self),
                "finance": lambda: FinancePage(self.db, self),
                "reports": lambda: ReportsPage(self.db, self),
                "users": lambda: UsersPage(self.db, self),
                "settings": lambda: SettingsPage(self.db, self),
            }
            self.pages[key] = builders[key]()
            self.stack.addWidget(self.pages[key])
        self.stack.setCurrentWidget(self.pages[key])
        self.breadcrumb.setText(tr(self.language, key))
        for page, button in self.nav_buttons.items():
            button.setChecked(page == key)
        if add and key == "students":
            page = self.pages[key]
            if isinstance(page, StudentsPage):
                page.add_record()

    def refresh_current(self) -> None:
        current = self.stack.currentWidget()
        if hasattr(current, "refresh"):
            current.refresh()

    def global_search(self, text: str) -> None:
        query = text.strip().lower()
        if not query:
            return
        with self.db.Session() as session:
            student = session.scalar(select(Student).where(or_(func.lower(Student.first_name).contains(query), func.lower(Student.student_code).contains(query))).limit(1))
            teacher = session.scalar(select(Teacher).where(or_(func.lower(Teacher.name).contains(query), func.lower(Teacher.teacher_code).contains(query))).limit(1))
        if student:
            self.show_page("students")
            page = self.pages["students"]
            if isinstance(page, StudentsPage):
                page.search.setText(text)
            return
        if teacher:
            self.show_page("teachers")
            page = self.pages["teachers"]
            if isinstance(page, TeachersPage):
                page.search.setText(text)
            return
        Toast(self, f"No student or teacher found for “{text}”.", True)

    def force_password_change(self) -> None:
        dialog = ChangePasswordDialog(self.db, int(self.current_user["id"]), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            Toast(self, "Password changed successfully.")

    def set_language(self, language: str) -> None:
        self.language = language
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language == "ps" else Qt.LayoutDirection.LeftToRight)
        for key, button in self.nav_buttons.items():
            icon = next(icon for nav_key, icon in NAV_ITEMS if nav_key == key)
            button.setText(f"{icon}   {tr(language, key)}")
        for key in list(self.pages):
            self.stack.removeWidget(self.pages[key])
        self.pages.clear()
        self.show_page("dashboard")

    def apply_theme(self, theme: str) -> None:
        QApplication.instance().setStyleSheet(DARK_STYLESHEET if theme == "dark" else LIGHT_STYLESHEET)

    def logout(self) -> None:
        if QMessageBox.question(self, "Sign out", "Sign out of the school workspace?") != QMessageBox.StandardButton.Yes:
            return
        self.close()
        self.login_window = LoginWindow(self.db)
        self.login_window.logged_in.connect(self.open_main)
        self.login_window.show()

    def open_main(self, user: dict[str, object]) -> None:
        self.login_window.close()
        window = MainWindow(self.db, user)
        window.show()
        QApplication.instance().activeWindow()._school_main = window

    @staticmethod
    def _shortcut(sequence: str, callback: Callable[[], None]) -> QAction:
        action = QAction()
        action.setShortcut(QKeySequence(sequence))
        action.triggered.connect(callback)
        return action


LIGHT_STYLESHEET = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #f4f7fb; color: #183047; }
#loginWindow { background: #f4f7fb; }
#loginBrand { background: #112f4b; color: #f5fbff; }
#loginBrand QLabel { color: #f5fbff; }
#loginTitle { font-size: 40px; font-weight: 700; line-height: 1.1; }
#loginSubtitle { color: #b6cbe0; font-size: 15px; line-height: 1.5; }
#loginFooter { color: #8ba8c2; font-size: 12px; }
#eyebrow, #brandKicker { color: #67a5ff; font-size: 11px; font-weight: 700; letter-spacing: 1.6px; }
#formTitle { color: #132e47; font-size: 31px; font-weight: 700; }
#muted, #hint { color: #71879a; }
#hint { font-size: 12px; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 10px; padding: 10px 12px; color: #183047; selection-background-color: #2979ff; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus { border: 2px solid #76aefc; }
#loginInput { padding: 12px 14px; font-size: 14px; }
#primaryButton { background: #2979ff; color: white; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 700; }
#primaryButton:hover { background: #1d66de; }
#ghostButton { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 9px; padding: 9px 14px; color: #28455f; font-weight: 600; }
#ghostButton:hover { background: #eaf3ff; border-color: #9ec3f8; }
#dangerButton { background: #fff1f2; border: 1px solid #f1c7cc; border-radius: 9px; padding: 9px 14px; color: #b2344a; font-weight: 600; }
#sidebar { background: #112f4b; }
#sidebar QLabel { color: #edf7ff; }
#brandName { font-size: 18px; font-weight: 700; }
#navButton, #logoutButton { text-align: left; background: transparent; border: none; border-radius: 10px; padding: 12px 14px; color: #a9c1d5; font-weight: 600; }
#navButton:hover { background: #1a466c; color: #ffffff; }
#navButton:checked { background: #2979ff; color: #ffffff; }
#logoutButton { color: #a9c1d5; }
#logoutButton:hover { background: #1a466c; color: white; }
#sidebarHelp { background: #183f61; border: 1px solid #26577f; border-radius: 12px; padding: 8px; }
#helpTitle { font-weight: 700; }
#helpText { color: #a9c8e0; font-size: 12px; }
#breadcrumb { color: #74899b; font-size: 13px; font-weight: 600; }
#globalSearch, #searchInput { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 20px; padding: 10px 15px; }
#userBadge { background: #e8f1fb; border: 1px solid #d5e3ef; border-radius: 20px; padding: 10px 15px; color: #31506a; font-weight: 600; }
#pageTitle { color: #132e47; font-size: 28px; font-weight: 700; }
#card { background: #ffffff; border: 1px solid #e4ebf2; border-radius: 15px; }
#statValue { color: #132e47; font-size: 27px; font-weight: 700; margin-top: 2px; }
#positive { color: #159a7c; font-size: 12px; font-weight: 600; }
#sectionTitle { color: #193850; font-size: 16px; font-weight: 700; }
#pulseText { color: #5a748b; font-size: 14px; line-height: 1.5; }
#activityList { background: transparent; border: none; }
#activityList::item { padding: 11px 4px; border-bottom: 1px solid #edf1f5; color: #35526a; }
QTableWidget { background: #ffffff; border: none; gridline-color: #edf1f5; alternate-background-color: #f8fafc; selection-background-color: #e5f0ff; selection-color: #183047; }
QHeaderView::section { background: #f7f9fb; color: #71879a; padding: 13px 10px; border: none; border-bottom: 1px solid #e4ebf2; font-weight: 700; }
QTableWidget::item { padding: 8px; border-bottom: 1px solid #edf1f5; }
QScrollArea { border: none; }
QCheckBox { color: #587186; }
QDialog { background: #f4f7fb; }
QDialog QLabel { color: #35526a; }
"""


DARK_STYLESHEET = LIGHT_STYLESHEET.replace("#f4f7fb", "#0e1b29").replace("#ffffff", "#162638").replace("#183047", "#e6f1fb").replace("#132e47", "#edf6ff").replace("#193850", "#edf6ff").replace("#d5e0ea", "#30485c").replace("#e4ebf2", "#253b4e").replace("#f7f9fb", "#1b3043").replace("#edf1f5", "#263b4f").replace("#f8fafc", "#142433").replace("#e8f1fb", "#1a344c").replace("#d5e3ef", "#2b4b63")


def main() -> int:
    ensure_app_directories()
    database = Database()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    app.setStyleSheet(LIGHT_STYLESHEET)
    locale = QLocale(QLocale.Language.English, QLocale.Country.Afghanistan)
    QLocale.setDefault(locale)
    login = LoginWindow(database)
    windows: list[MainWindow] = []

    def open_main(user: dict[str, object]) -> None:
        login.close()
        window = MainWindow(database, user)
        windows.append(window)
        window.show()

    login.logged_in.connect(open_main)
    login.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())