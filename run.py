import app.main as core
from app import models_extended  # noqa: F401 - register production domain tables before Database.create_all
from app.professional_dashboard import ProfessionalDashboardPage
from app.professional_modules import MODULES, ProfessionalModulePage, ProfessionalUsersPage
from app.authorization import has_permission

core.DashboardPage = ProfessionalDashboardPage

# Keep the original pages, but expose the complete school-management navigation
# and apply role-based visibility at the application shell.
_ORIGINAL_BUILD_SIDEBAR = core.MainWindow._build_sidebar
_ORIGINAL_SHOW_PAGE = core.MainWindow.show_page

NAV = [
    ("dashboard", "⌂", "Dashboard"),
    ("students", "♙", "Students"),
    ("teachers", "◇", "Teachers"),
    ("academics", "▦", "Academics"),
    ("classes", "▤", "Classes & Sections"),
    ("subjects", "◈", "Subjects"),
    ("timetable", "◫", "Timetable"),
    ("attendance", "✓", "Attendance"),
    ("exams", "▣", "Exams"),
    ("results", "★", "Results"),
    ("finance", "₳", "Fees & Finance"),
    ("hr", "♙", "HR"),
    ("library", "▥", "Library"),
    ("transport", "▱", "Transport"),
    ("inventory", "▤", "Inventory / Store"),
    ("parents", "♧", "Parents"),
    ("communication", "✉", "Communication"),
    ("events", "◷", "Events / Calendar"),
    ("discipline", "⚑", "Discipline"),
    ("health", "+", "Health / Medical"),
    ("documents", "▱", "Documents"),
    ("certificates", "◇", "Certificates"),
    ("reports", "▤", "Reports"),
    ("users", "♙", "Users & Roles"),
    ("settings", "⚙", "Settings"),
]


def _professional_sidebar(self):
    # Reuse the existing styling by temporarily replacing the old navigation list.
    old = core.NAV_ITEMS
    core.NAV_ITEMS = [(key, icon) for key, icon, _ in NAV if key in {"dashboard", "students", "teachers", "finance", "reports", "users", "settings"}]
    try:
        sidebar = _ORIGINAL_BUILD_SIDEBAR(self)
    finally:
        core.NAV_ITEMS = old
    # Rebuild the sidebar buttons with the complete, role-filtered navigation.
    layout = sidebar.layout()
    while layout.count():
        item = layout.takeAt(0)
        if item.widget(): item.widget().deleteLater()
        elif item.layout():
            child = item.layout()
            while child.count():
                child_item = child.takeAt(0)
                if child_item.widget(): child_item.widget().deleteLater()
    from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
    from app.main import load_school_logo, tr
    brand = QHBoxLayout(); logo = QLabel(); logo.setPixmap(load_school_logo(42)); logo.setFixedSize(46,46); brand.addWidget(logo)
    text = QVBoxLayout(); text.setSpacing(0); text.addWidget(QLabel("AMAN AHMADZAI", objectName="brandKicker")); text.addWidget(QLabel("School Management", objectName="brandName")); brand.addLayout(text); layout.addLayout(brand); layout.addSpacing(20)
    role = str(self.current_user.get("role", "Viewer"))
    self.nav_buttons.clear()
    for key, icon, label in NAV:
        if key not in {"dashboard", "settings"} and not has_permission(role, key if key != "finance" else "fees", "view"):
            continue
        button=QPushButton(f"{icon}   {label}"); button.setObjectName("navButton"); button.setCheckable(True); button.clicked.connect(lambda checked=False,page=key:self.show_page(page)); self.nav_buttons[key]=button; layout.addWidget(button)
    layout.addStretch()
    help_card=QFrame(); help_card.setObjectName("sidebarHelp"); hl=QVBoxLayout(help_card); hl.addWidget(QLabel("OFFLINE • SECURE",objectName="helpTitle")); hl.addWidget(QLabel(f"Role: {role}",objectName="helpText")); layout.addWidget(help_card)
    logout=QPushButton("↪   Logout"); logout.setObjectName("logoutButton"); logout.clicked.connect(self.logout); layout.addWidget(logout)
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
    if key == "finance":
        key_for_auth = "fees"
    else:
        key_for_auth = key
    if key not in {"dashboard", "settings"} and not has_permission(str(self.current_user.get("role","Viewer")), key_for_auth, "view"):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Access denied", "Your role does not have permission to open this module.")
        return
    return _ORIGINAL_SHOW_PAGE(self, key, add=add)

core.MainWindow._build_sidebar = _professional_sidebar
core.MainWindow.show_page = _professional_show_page

if __name__ == "__main__":
    raise SystemExit(core.main())
