import app.main as core
from app import models_extended  # noqa: F401 - register production domain tables before Database.create_all
from app.professional_dashboard import ProfessionalDashboardPage
from app.professional_modules import MODULES, ProfessionalModulePage, ProfessionalUsersPage
from app.authorization import has_permission

core.DashboardPage = ProfessionalDashboardPage

_ORIGINAL_BUILD_SIDEBAR = core.MainWindow._build_sidebar
_ORIGINAL_SHOW_PAGE = core.MainWindow.show_page

NAV = [
    ("dashboard", "Dashboard"),
    ("students", "Students"),
    ("teachers", "Teachers"),
    ("academics", "Academics"),
    ("classes", "Classes & Sections"),
    ("subjects", "Subjects"),
    ("timetable", "Timetable"),
    ("attendance", "Attendance"),
    ("exams", "Exams"),
    ("results", "Results"),
    ("finance", "Fees & Finance"),
    ("hr", "HR"),
    ("library", "Library"),
    ("transport", "Transport"),
    ("inventory", "Inventory / Store"),
    ("parents", "Parents"),
    ("communication", "Communication"),
    ("events", "Events / Calendar"),
    ("discipline", "Discipline"),
    ("health", "Health / Medical"),
    ("documents", "Documents"),
    ("certificates", "Certificates"),
    ("reports", "Reports"),
    ("users", "Users & Roles"),
    ("settings", "Settings"),
]


def _professional_sidebar(self):
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QWidget, QStyle

    # Build a clean sidebar from scratch. Native Qt icons are used instead of
    # Unicode symbols so icons render consistently on Windows.
    sidebar = QWidget()
    sidebar.setObjectName("sidebar")
    sidebar.setFixedWidth(272)
    outer = QVBoxLayout(sidebar)
    outer.setContentsMargins(18, 22, 14, 18)
    outer.setSpacing(0)

    brand = QHBoxLayout()
    brand.setSpacing(11)
    logo = QLabel()
    logo.setPixmap(core.load_school_logo(44))
    logo.setFixedSize(46, 46)
    brand.addWidget(logo)
    text = QVBoxLayout()
    text.setSpacing(1)
    text.addWidget(QLabel("AMAN AHMADZAI", objectName="brandKicker"))
    text.addWidget(QLabel("School Management", objectName="brandName"))
    brand.addLayout(text)
    outer.addLayout(brand)
    outer.addSpacing(18)

    role = str(self.current_user.get("role", "Viewer"))
    role_label = QLabel(f"{role}  •  Offline"); role_label.setObjectName("sidebarRole")
    outer.addWidget(role_label)
    outer.addSpacing(10)

    scroll = QScrollArea()
    scroll.setObjectName("sidebarScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    nav_host = QWidget()
    nav_layout = QVBoxLayout(nav_host)
    nav_layout.setContentsMargins(0, 0, 4, 0)
    nav_layout.setSpacing(5)

    # Standard Qt icons are available without extra icon packages.
    icon_map = {
        "dashboard": QStyle.StandardPixmap.SP_ComputerIcon,
        "students": QStyle.StandardPixmap.SP_FileDialogListView,
        "teachers": QStyle.StandardPixmap.SP_FileDialogDetailedView,
        "academics": QStyle.StandardPixmap.SP_DirOpenIcon,
        "classes": QStyle.StandardPixmap.SP_DirIcon,
        "subjects": QStyle.StandardPixmap.SP_FileIcon,
        "timetable": QStyle.StandardPixmap.SP_BrowserReload,
        "attendance": QStyle.StandardPixmap.SP_DialogApplyButton,
        "exams": QStyle.StandardPixmap.SP_DialogQuestionButton,
        "results": QStyle.StandardPixmap.SP_DialogYesButton,
        "finance": QStyle.StandardPixmap.SP_DriveHDIcon,
        "hr": QStyle.StandardPixmap.SP_DirHomeIcon,
        "library": QStyle.StandardPixmap.SP_DirOpenIcon,
        "transport": QStyle.StandardPixmap.SP_ArrowRight,
        "inventory": QStyle.StandardPixmap.SP_DriveHDIcon,
        "parents": QStyle.StandardPixmap.SP_FileDialogInfoView,
        "communication": QStyle.StandardPixmap.SP_MessageBoxInformation,
        "events": QStyle.StandardPixmap.SP_FileDialogContentsView,
        "discipline": QStyle.StandardPixmap.SP_MessageBoxWarning,
        "health": QStyle.StandardPixmap.SP_MessageBoxInformation,
        "documents": QStyle.StandardPixmap.SP_FileIcon,
        "certificates": QStyle.StandardPixmap.SP_DialogSaveButton,
        "reports": QStyle.StandardPixmap.SP_FileDialogDetailedView,
        "users": QStyle.StandardPixmap.SP_FileDialogInfoView,
        "settings": QStyle.StandardPixmap.SP_FileDialogDetailedView,
    }

    self.nav_buttons.clear()
    for key, label in NAV:
        if key not in {"dashboard", "settings"} and not has_permission(role, key if key != "finance" else "fees", "view"):
            continue
        button = QPushButton(label)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(44)
        button.setIcon(self.style().standardIcon(icon_map[key]))
        button.setIconSize(QSize(20, 20))
        button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        button.setStyleSheet("")
        button.clicked.connect(lambda checked=False, page=key: self.show_page(page))
        self.nav_buttons[key] = button
        nav_layout.addWidget(button)
    nav_layout.addStretch()
    scroll.setWidget(nav_host)
    outer.addWidget(scroll, 1)
    outer.addSpacing(10)

    help_card = QFrame()
    help_card.setObjectName("sidebarHelp")
    help_layout = QVBoxLayout(help_card)
    help_layout.setContentsMargins(13, 10, 13, 10)
    help_layout.setSpacing(3)
    help_layout.addWidget(QLabel("OFFLINE • SECURE", objectName="helpTitle"))
    help_layout.addWidget(QLabel("School data stays on this computer.", objectName="helpText"))
    outer.addWidget(help_card)
    outer.addSpacing(8)

    logout = QPushButton("Logout")
    logout.setObjectName("logoutButton")
    logout.setCursor(Qt.CursorShape.PointingHandCursor)
    logout.setMinimumHeight(42)
    logout.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
    logout.setIconSize(QSize(19, 19))
    logout.clicked.connect(self.logout)
    outer.addWidget(logout)
    return sidebar


def _professional_show_page(self, key, add=False):
    if key in MODULES:
        if key not in self.pages:
            self.pages[key] = ProfessionalModulePage(self.db, self, key)
            self.stack.addWidget(self.pages[key])
        self.stack.setCurrentWidget(self.pages[key])
        self.breadcrumb.setText(MODULES[key][0])
        for page, button in self.nav_buttons.items(): button.setChecked(page == key)
        return
    if key == "users":
        if key not in self.pages:
            self.pages[key] = ProfessionalUsersPage(self.db, self)
            self.stack.addWidget(self.pages[key])
        self.stack.setCurrentWidget(self.pages[key])
        self.breadcrumb.setText("Users & Roles")
        for page, button in self.nav_buttons.items(): button.setChecked(page == key)
        return
    key_for_auth = "fees" if key == "finance" else key
    if key not in {"dashboard", "settings"} and not has_permission(str(self.current_user.get("role", "Viewer")), key_for_auth, "view"):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Access denied", "Your role does not have permission to open this module.")
        return
    return _ORIGINAL_SHOW_PAGE(self, key, add=add)

core.MainWindow._build_sidebar = _professional_sidebar
core.MainWindow.show_page = _professional_show_page

if __name__ == "__main__":
    raise SystemExit(core.main())
