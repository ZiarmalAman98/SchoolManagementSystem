from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

MODERN_LOGIN_MIN_WIDTH = 1080

LOGIN_STYLE = """
#loginWindow { background: #f5f8fc; }
#loginBrand { background: #102a43; border-right: 1px solid #183c5a; }
#loginBrand QLabel { color: #f7fbff; }
#loginTitle { font-size: 42px; font-weight: 800; color: #ffffff; }
#loginSubtitle { color: #b9cee1; font-size: 15px; line-height: 1.5; }
#eyebrow { color: #6eb1ff; font-size: 10px; font-weight: 800; letter-spacing: 1.8px; }
#loginFooter { color: #91abc0; font-size: 12px; }
#loginFormPanel { background: #ffffff; }
#formTitle { color: #122b43; font-size: 30px; font-weight: 800; }
#loginIntro { color: #71879a; font-size: 13px; }
#fieldLabel { color: #36536b; font-size: 12px; font-weight: 700; }
#loginInput { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 12px; padding: 12px 14px; color: #183047; font-size: 14px; }
#loginInput:focus { border: 2px solid #6aa8f8; }
#passwordToggle { background: #f4f7fa; border: 1px solid #d5e0ea; border-radius: 10px; color: #48657b; font-weight: 700; padding: 0 12px; }
#passwordToggle:hover { background: #eaf3ff; color: #1d66de; }
#loginButton { background: #2979ff; color: #ffffff; border: none; border-radius: 12px; padding: 13px 18px; font-size: 14px; font-weight: 800; }
#loginButton:hover { background: #1d66de; }
#loginButton:pressed { background: #1858c5; }
#exitButton { background: #ffffff; color: #526b80; border: 1px solid #d5e0ea; border-radius: 11px; padding: 11px 18px; font-weight: 650; }
#exitButton:hover { background: #f4f8fc; }
#loginBadge { background: #edf5ff; color: #2864bd; border: 1px solid #d7e7fa; border-radius: 9px; padding: 7px 10px; font-size: 11px; font-weight: 700; }
"""

LOGOUT_STYLE = """
#logoutButton { text-align: left; background: #fff4f4; border: 1px solid #ffd6d6; border-radius: 10px; padding: 10px 12px; color: #c23a4b; font-weight: 750; }
#logoutButton:hover { background: #ffe7e9; border-color: #f2b8bf; }
#logoutButton:pressed { background: #ffdfe2; }
"""


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("fieldLabel")
    return label


def modern_login_build(self) -> None:
    """Build the polished login screen while preserving the existing auth flow."""
    from .config import APP_VERSION
    from .main import load_school_logo
    from .i18n import tr

    self.setMinimumSize(MODERN_LOGIN_MIN_WIDTH, 680)
    self.setStyleSheet(LOGIN_STYLE)

    root = QHBoxLayout(self)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    brand = QWidget()
    brand.setObjectName("loginBrand")
    brand_layout = QVBoxLayout(brand)
    brand_layout.setContentsMargins(68, 58, 68, 48)
    brand_layout.setSpacing(0)

    logo = QLabel()
    logo.setPixmap(load_school_logo(88))
    logo.setFixedSize(92, 92)
    brand_layout.addWidget(logo)
    brand_layout.addSpacing(42)

    eyebrow = QLabel("AMAN AHMADZAI  •  SCHOOL OS")
    eyebrow.setObjectName("eyebrow")
    brand_layout.addWidget(eyebrow)
    brand_layout.addSpacing(12)

    title = QLabel("A smarter school\nstarts here.")
    title.setObjectName("loginTitle")
    brand_layout.addWidget(title)
    brand_layout.addSpacing(15)

    subtitle = QLabel("Manage students, teachers, academics,\nattendance and finance from one secure\noffline workspace.")
    subtitle.setObjectName("loginSubtitle")
    brand_layout.addWidget(subtitle)
    brand_layout.addStretch()

    badge = QLabel("●  OFFLINE • YOUR DATA STAYS ON THIS PC")
    badge.setObjectName("loginBadge")
    brand_layout.addWidget(badge)
    brand_layout.addSpacing(12)
    footer = QLabel(f"School Management System  ·  v{APP_VERSION}")
    footer.setObjectName("loginFooter")
    brand_layout.addWidget(footer)
    root.addWidget(brand, 5)

    panel = QWidget()
    panel.setObjectName("loginFormPanel")
    form = QVBoxLayout(panel)
    form.setContentsMargins(86, 56, 86, 56)
    form.setSpacing(10)
    form.addStretch()

    heading = QLabel(tr(self.language, "welcome"))
    heading.setObjectName("formTitle")
    form.addWidget(heading)
    intro = QLabel("Sign in to continue to your school workspace.")
    intro.setObjectName("loginIntro")
    form.addWidget(intro)
    form.addSpacing(24)

    form.addWidget(_field_label(tr(self.language, "username")))
    self.username = QLineEdit()
    self.username.setPlaceholderText("Enter username")
    self.username.setMinimumHeight(50)
    self.username.setObjectName("loginInput")
    self.username.setClearButtonEnabled(True)
    form.addWidget(self.username)
    form.addSpacing(8)

    form.addWidget(_field_label(tr(self.language, "password")))
    password_row = QHBoxLayout()
    password_row.setSpacing(7)
    self.password = QLineEdit()
    self.password.setPlaceholderText("Enter password")
    self.password.setEchoMode(QLineEdit.EchoMode.Password)
    self.password.setMinimumHeight(50)
    self.password.setObjectName("loginInput")
    self.password.returnPressed.connect(self.login)
    password_row.addWidget(self.password, 1)
    toggle = QPushButton("Show")
    toggle.setObjectName("passwordToggle")
    toggle.setMinimumHeight(50)
    toggle.setCheckable(True)

    def toggle_password(checked: bool) -> None:
        self.password.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
        toggle.setText("Hide" if checked else "Show")

    toggle.toggled.connect(toggle_password)
    password_row.addWidget(toggle)
    form.addLayout(password_row)
    form.addSpacing(8)

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
    form.addLayout(options)
    form.addSpacing(12)

    self.login_button = QPushButton(tr(self.language, "login"))
    self.login_button.setObjectName("loginButton")
    self.login_button.setMinimumHeight(52)
    self.login_button.clicked.connect(self.login)
    form.addWidget(self.login_button)

    exit_button = QPushButton("Exit application")
    exit_button.setObjectName("exitButton")
    exit_button.setMinimumHeight(44)
    exit_button.clicked.connect(QApplication.instance().quit)
    form.addWidget(exit_button)

    hint = QLabel("Demo access: admin / admin123")
    hint.setObjectName("hint")
    form.addWidget(hint)
    form.addStretch()
    root.addWidget(panel, 4)
    self._apply_direction()


def modern_logout(self) -> None:
    """Securely confirm sign-out, close the workspace, and return to login."""
    answer = QMessageBox.question(
        self,
        "Sign out",
        "Are you sure you want to sign out of the school workspace?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if answer != QMessageBox.StandardButton.Yes:
        return

    try:
        with self.db.Session.begin() as session:
            username = str(self.current_user.get("username", ""))
            self.db.log(session, "LOGOUT", "Authentication", f"{username} signed out")
    except Exception:
        pass

    self.close()
    self.login_window = self.__class__.__module__ and None
    from .main import LoginWindow
    self.login_window = LoginWindow(self.db)
    self.login_window.logged_in.connect(self.open_main)
    self.login_window.show()
