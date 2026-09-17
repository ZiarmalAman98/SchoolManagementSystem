from __future__ import annotations

from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

MODERN_LOGIN_MIN_WIDTH = 1080

LOGIN_STYLE = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; }
#loginWindow { background: #f7f5ff; }
#loginBrand { background: #35205f; border-right: 1px solid #4b2d7d; }
#loginBrand QLabel { color: #faf8ff; }
#loginTitle { font-size: 42px; font-weight: 800; color: #ffffff; }
#loginSubtitle { color: #d9ccf5; font-size: 15px; line-height: 1.5; }
#eyebrow { color: #c7a7ff; font-size: 10px; font-weight: 800; letter-spacing: 1.8px; }
#loginFooter { color: #b9a9d5; font-size: 12px; }
#loginFormPanel { background: #ffffff; }
#formTitle { color: #35205f; font-size: 30px; font-weight: 800; }
#loginIntro { color: #7b6e91; font-size: 13px; }
#fieldLabel { color: #514368; font-size: 12px; font-weight: 700; }
#loginInput { background: #ffffff; border: 1px solid #ddd5ec; border-radius: 12px; padding: 12px 14px; color: #302642; font-size: 14px; }
#loginInput:hover { border-color: #c5b5df; }
#loginInput:focus { border: 2px solid #8b5cf6; }
#passwordToggle { background: #f6f2ff; border: 1px solid #ddd5ec; border-radius: 10px; color: #604b7e; font-weight: 700; padding: 0 12px; }
#passwordToggle:hover { background: #eee6ff; color: #7048d8; }
#loginButton { background: #7c3aed; color: #ffffff; border: none; border-radius: 12px; padding: 13px 18px; font-size: 14px; font-weight: 800; }
#loginButton:hover { background: #6d28d9; }
#loginButton:pressed { background: #5b21b6; }
#exitButton { background: #ffffff; color: #665978; border: 1px solid #ddd5ec; border-radius: 11px; padding: 11px 18px; font-weight: 650; }
#exitButton:hover { background: #faf8ff; }
#loginBadge { background: #f0eaff; color: #6941b4; border: 1px solid #ded0fa; border-radius: 9px; padding: 7px 10px; font-size: 11px; font-weight: 700; }
#rememberCheck { color: #665978; }
#hint { color: #9b91a9; font-size: 11px; }
QComboBox { background: #ffffff; border: 1px solid #ddd5ec; border-radius: 8px; padding: 7px 9px; color: #514368; }
"""

LOGOUT_STYLE = """
#logoutButton { text-align: left; background: #fff4f7; border: 1px solid #f7dce5; border-radius: 11px; padding: 10px 13px; color: #c2416b; font-weight: 750; }
#logoutButton:hover { background: #ffebf1; border-color: #efc4d4; }
#logoutButton:pressed { background: #ffdde8; }
"""


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("fieldLabel")
    return label


def modern_login_build(self) -> None:
    from .config import APP_VERSION
    from .main import load_school_logo
    from .i18n import tr

    self.setMinimumSize(MODERN_LOGIN_MIN_WIDTH, 680)
    self.setStyleSheet(LOGIN_STYLE)
    root = QHBoxLayout(self)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    brand = QWidget(); brand.setObjectName("loginBrand")
    brand_layout = QVBoxLayout(brand); brand_layout.setContentsMargins(68, 58, 68, 48)
    logo = QLabel(); logo.setPixmap(load_school_logo(88)); logo.setFixedSize(92, 92); brand_layout.addWidget(logo)
    brand_layout.addSpacing(42)
    eyebrow = QLabel("AMAN AHMADZAI  •  SCHOOL OS"); eyebrow.setObjectName("eyebrow"); brand_layout.addWidget(eyebrow)
    brand_layout.addSpacing(12)
    title = QLabel("A smarter school\nstarts here."); title.setObjectName("loginTitle"); brand_layout.addWidget(title)
    brand_layout.addSpacing(15)
    subtitle = QLabel("Manage students, teachers, academics,\nattendance and finance from one secure\noffline workspace."); subtitle.setObjectName("loginSubtitle"); brand_layout.addWidget(subtitle)
    brand_layout.addStretch()
    badge = QLabel("●  OFFLINE • YOUR DATA STAYS ON THIS PC"); badge.setObjectName("loginBadge"); brand_layout.addWidget(badge)
    brand_layout.addSpacing(12)
    footer = QLabel(f"School Management System  ·  v{APP_VERSION}"); footer.setObjectName("loginFooter"); brand_layout.addWidget(footer)
    root.addWidget(brand, 5)

    panel = QWidget(); panel.setObjectName("loginFormPanel")
    form = QVBoxLayout(panel); form.setContentsMargins(86, 56, 86, 56); form.setSpacing(10); form.addStretch()
    heading = QLabel(tr(self.language, "welcome")); heading.setObjectName("formTitle"); form.addWidget(heading)
    intro = QLabel("Sign in to continue to your school workspace."); intro.setObjectName("loginIntro"); form.addWidget(intro); form.addSpacing(24)
    form.addWidget(_field_label(tr(self.language, "username")))
    self.username = QLineEdit(); self.username.setPlaceholderText("Enter username"); self.username.setMinimumHeight(50); self.username.setObjectName("loginInput"); self.username.setClearButtonEnabled(True); form.addWidget(self.username); form.addSpacing(8)
    form.addWidget(_field_label(tr(self.language, "password")))
    password_row = QHBoxLayout(); password_row.setSpacing(7)
    self.password = QLineEdit(); self.password.setPlaceholderText("Enter password"); self.password.setEchoMode(QLineEdit.EchoMode.Password); self.password.setMinimumHeight(50); self.password.setObjectName("loginInput"); self.password.returnPressed.connect(self.login); password_row.addWidget(self.password, 1)
    toggle = QPushButton("Show"); toggle.setObjectName("passwordToggle"); toggle.setMinimumHeight(50); toggle.setCheckable(True)
    toggle.toggled.connect(lambda checked: (self.password.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password), toggle.setText("Hide" if checked else "Show")))
    password_row.addWidget(toggle); form.addLayout(password_row); form.addSpacing(8)
    options = QHBoxLayout()
    self.remember = QCheckBox(tr(self.language, "remember")); self.remember.setObjectName("rememberCheck"); options.addWidget(self.remember); options.addStretch(); options.addWidget(QLabel(tr(self.language, "language")))
    self.language_combo = QComboBox(); self.language_combo.addItem("پښتو", "ps"); self.language_combo.addItem("English", "en"); self.language_combo.setCurrentIndex(0 if self.language == "ps" else 1); self.language_combo.currentIndexChanged.connect(self.change_language); options.addWidget(self.language_combo); form.addLayout(options); form.addSpacing(12)
    self.login_button = QPushButton(tr(self.language, "login")); self.login_button.setObjectName("loginButton"); self.login_button.setMinimumHeight(52); self.login_button.clicked.connect(self.login); form.addWidget(self.login_button)
    exit_button = QPushButton("Exit application"); exit_button.setObjectName("exitButton"); exit_button.setMinimumHeight(44); exit_button.clicked.connect(QApplication.instance().quit); form.addWidget(exit_button)
    hint = QLabel("Demo access: admin / admin123"); hint.setObjectName("hint"); form.addWidget(hint); form.addStretch()
    root.addWidget(panel, 4)
    self._apply_direction()


def modern_logout(self) -> None:
    answer = QMessageBox.question(self, "Sign out", "Are you sure you want to sign out of the school workspace?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if answer != QMessageBox.StandardButton.Yes:
        return
    try:
        with self.db.Session.begin() as session:
            username = str(self.current_user.get("username", ""))
            self.db.log(session, "LOGOUT", "Authentication", f"{username} signed out")
    except Exception:
        pass
    self.close()
    from .main import LoginWindow
    self.login_window = LoginWindow(self.db)
    self.login_window.logged_in.connect(self.open_main)
    self.login_window.show()
