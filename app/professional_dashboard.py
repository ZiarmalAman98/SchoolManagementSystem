from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout
from sqlalchemy import func, select

from .main import DashboardPage as BaseDashboardPage, StatCard
from .database import Payment, Student, Teacher
from .models_extended import AttendanceRecord
from .professional_charts import BarChartWidget, DonutChartWidget


LIGHT_DASHBOARD_STYLESHEET = """
QFrame#dashboardWelcome { background: #7c3aed; border: 1px solid #6d28d9; border-radius: 18px; }
QLabel#dashboardWelcomeTitle { color: #ffffff; font-size: 25px; font-weight: 700; }
QLabel#dashboardWelcomeSubtitle { color: #eee6ff; font-size: 13px; }
QPushButton#dashboardRefresh { background: #ffffff; color: #4b2d70; border: none; border-radius: 10px; padding: 9px 16px; font-weight: 700; }
QPushButton#dashboardRefresh:hover { background: #f4efff; }
QLabel#dashboardSectionTitle { color: #493660; font-size: 16px; font-weight: 700; }
QFrame#dashboardQuickActions, QFrame#dashboardSection { background: #ffffff; border: 1px solid #e8e1f2; border-radius: 16px; }
QPushButton#dashboardActionButton { background: #f7f3ff; color: #55436d; border: 1px solid #e8def8; border-radius: 10px; padding: 9px 14px; font-weight: 650; }
QPushButton#dashboardActionButton:hover { background: #eee6ff; border-color: #cdb7f2; color: #6d28d9; }
QLabel#dashboardLiveBadge { background: #f0eaff; color: #7048d8; border-radius: 8px; padding: 4px 8px; font-size: 10px; font-weight: 800; }
QLabel#dashboardPulse { color: #766985; font-size: 14px; }
"""

DARK_DASHBOARD_STYLESHEET = """
QFrame#dashboardWelcome { background: #8b5cf6; border: 1px solid #a78bfa; border-radius: 18px; }
QLabel#dashboardWelcomeTitle { color: #ffffff; font-size: 25px; font-weight: 700; }
QLabel#dashboardWelcomeSubtitle { color: #f0eaff; font-size: 13px; }
QPushButton#dashboardRefresh { background: #f4efff; color: #35205f; border: none; border-radius: 10px; padding: 9px 16px; font-weight: 700; }
QPushButton#dashboardRefresh:hover { background: #e9ddff; }
QLabel#dashboardSectionTitle { color: #f0eaff; font-size: 16px; font-weight: 700; }
QFrame#dashboardQuickActions, QFrame#dashboardSection { background: #211735; border: 1px solid #3b2b56; border-radius: 16px; }
QPushButton#dashboardActionButton { background: #2b2040; color: #ded3ec; border: 1px solid #46345f; border-radius: 10px; padding: 9px 14px; font-weight: 650; }
QPushButton#dashboardActionButton:hover { background: #3b2860; border-color: #6b4ba0; color: #ffffff; }
QLabel#dashboardLiveBadge { background: #3b2860; color: #cbb1ff; border-radius: 8px; padding: 4px 8px; font-size: 10px; font-weight: 800; }
QLabel#dashboardPulse { color: #c3b4d4; font-size: 14px; }
"""


class ProfessionalDashboardPage(BaseDashboardPage):
    """Modern dashboard with live KPI cards and native Qt charts."""

    def _build(self) -> None:
        dark = self.db.setting("theme", "light") == "dark"
        self.setStyleSheet(DARK_DASHBOARD_STYLESHEET if dark else LIGHT_DASHBOARD_STYLESHEET)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        welcome = QFrame()
        welcome.setObjectName("dashboardWelcome")
        welcome_layout = QHBoxLayout(welcome)
        welcome_layout.setContentsMargins(24, 20, 24, 20)
        welcome_text = QVBoxLayout()
        welcome_text.setSpacing(4)
        self.title = QLabel()
        self.title.setObjectName("dashboardWelcomeTitle")
        welcome_text.addWidget(self.title)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("dashboardWelcomeSubtitle")
        welcome_text.addWidget(self.subtitle)
        welcome_layout.addLayout(welcome_text, 1)
        refresh = QPushButton("↻  Refresh")
        refresh.setObjectName("dashboardRefresh")
        refresh.setMinimumHeight(40)
        refresh.clicked.connect(self.refresh)
        welcome_layout.addWidget(refresh)
        layout.addWidget(welcome)

        metrics_header = QHBoxLayout()
        metrics_title = QLabel("School overview")
        metrics_title.setObjectName("dashboardSectionTitle")
        metrics_header.addWidget(metrics_title)
        metrics_header.addStretch()
        layout.addLayout(metrics_header)
        self.stats = QGridLayout()
        self.stats.setHorizontalSpacing(14)
        self.stats.setVerticalSpacing(14)
        layout.addLayout(self.stats)

        actions = QFrame()
        actions.setObjectName("dashboardQuickActions")
        actions_layout = QVBoxLayout(actions)
        actions_layout.setContentsMargins(18, 16, 18, 16)
        actions_layout.setSpacing(12)
        actions_title = QLabel("Quick actions")
        actions_title.setObjectName("dashboardSectionTitle")
        actions_layout.addWidget(actions_title)
        action_grid = QGridLayout()
        action_grid.setHorizontalSpacing(10)
        action_grid.setVerticalSpacing(10)
        quick_actions = [
            ("＋  Add student", "students", True),
            ("＋  Add teacher", "teachers", False),
            ("₳  Record payment", "finance", False),
            ("▤  Open reports", "reports", False),
        ]
        for index, (label, page, add) in enumerate(quick_actions):
            button = QPushButton(label)
            button.setObjectName("dashboardActionButton")
            button.setMinimumHeight(42)
            button.clicked.connect(lambda checked=False, p=page, a=add: self.main_window.show_page(p, add=a))
            action_grid.addWidget(button, index // 4, index % 4)
        actions_layout.addLayout(action_grid)
        layout.addWidget(actions)

        charts = QHBoxLayout()
        charts.setSpacing(14)
        enrollment_card = QFrame(); enrollment_card.setObjectName("dashboardSection")
        enrollment_layout = QVBoxLayout(enrollment_card); enrollment_layout.setContentsMargins(20, 16, 20, 14)
        enrollment_layout.addWidget(QLabel("Students by class", objectName="dashboardSectionTitle"))
        self.enrollment_chart = BarChartWidget([], [])
        enrollment_layout.addWidget(self.enrollment_chart)
        charts.addWidget(enrollment_card, 3)
        attendance_card = QFrame(); attendance_card.setObjectName("dashboardSection")
        attendance_layout = QVBoxLayout(attendance_card); attendance_layout.setContentsMargins(20, 16, 20, 14)
        attendance_layout.addWidget(QLabel("Attendance overview", objectName="dashboardSectionTitle"))
        self.attendance_chart = DonutChartWidget([], [])
        attendance_layout.addWidget(self.attendance_chart)
        charts.addWidget(attendance_card, 2)
        layout.addLayout(charts)

        lower = QHBoxLayout()
        lower.setSpacing(14)
        activity_card = QFrame(); activity_card.setObjectName("dashboardSection")
        activity_layout = QVBoxLayout(activity_card); activity_layout.setContentsMargins(20, 18, 20, 18)
        activity_heading = QHBoxLayout()
        self.activity_title = QLabel(); self.activity_title.setObjectName("dashboardSectionTitle")
        activity_heading.addWidget(self.activity_title); activity_heading.addStretch()
        live = QLabel("LIVE"); live.setObjectName("dashboardLiveBadge"); activity_heading.addWidget(live)
        activity_layout.addLayout(activity_heading)
        self.activity_list = QListWidget(); self.activity_list.setObjectName("activityList"); self.activity_list.setMinimumHeight(160)
        activity_layout.addWidget(self.activity_list); lower.addWidget(activity_card, 3)

        pulse_card = QFrame(); pulse_card.setObjectName("dashboardSection")
        pulse_layout = QVBoxLayout(pulse_card); pulse_layout.setContentsMargins(20, 18, 20, 18)
        pulse_layout.addWidget(QLabel("Daily pulse", objectName="dashboardSectionTitle"))
        self.pulse_label = QLabel(); self.pulse_label.setWordWrap(True); self.pulse_label.setObjectName("dashboardPulse")
        pulse_layout.addWidget(self.pulse_label); pulse_layout.addStretch(); lower.addWidget(pulse_card, 2)
        layout.addLayout(lower)

    def _refresh_charts(self) -> None:
        with self.db.Session() as session:
            class_rows = session.execute(
                select(Student.class_name, func.count(Student.id)).group_by(Student.class_name).order_by(func.count(Student.id).desc()).limit(8)
            ).all()
            attendance_rows = session.execute(
                select(AttendanceRecord.status, func.count(AttendanceRecord.id)).group_by(AttendanceRecord.status)
            ).all()
        labels = [row[0] or "Unassigned" for row in class_rows]
        values = [float(row[1]) for row in class_rows]
        self.enrollment_chart.set_data(labels, values)
        attendance_labels = [row[0] or "Unknown" for row in attendance_rows]
        attendance_values = [float(row[1]) for row in attendance_rows]
        self.attendance_chart.set_data(attendance_labels, attendance_values)

    def refresh(self) -> None:
        super().refresh()
        self._refresh_charts()
        dark = self.db.setting("theme", "light") == "dark"
        metric_bg = "#211735" if dark else "#ffffff"
        metric_border = "#3b2b56" if dark else "#e8e1f2"
        activity_selected = "#3b2860" if dark else "#f0eaff"
        activity_text = "#f0eaff" if dark else "#35205f"
        for index in range(self.stats.count()):
            widget = self.stats.itemAt(index).widget()
            if isinstance(widget, StatCard):
                widget.setObjectName("dashboardMetric")
                widget.setStyleSheet(f"QFrame#dashboardMetric {{ background: {metric_bg}; border: 1px solid {metric_border}; border-radius: 16px; }}")
        self.activity_list.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 12px 6px; border-bottom: 1px solid #eee9f3; }"
            f"QListWidget::item:selected {{ background: {activity_selected}; color: {activity_text}; border-radius: 8px; }}"
        )
