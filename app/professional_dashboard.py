from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout

from .main import DashboardPage as BaseDashboardPage, StatCard


DASHBOARD_STYLESHEET = """
QFrame#dashboardWelcome {
    background: #112f4b;
    border: 1px solid #1e4b70;
    border-radius: 18px;
}
QLabel#dashboardWelcomeTitle {
    color: #ffffff;
    font-size: 25px;
    font-weight: 700;
}
QLabel#dashboardWelcomeSubtitle {
    color: #b9d0e4;
    font-size: 13px;
}
QPushButton#dashboardRefresh {
    background: #ffffff;
    color: #193850;
    border: none;
    border-radius: 10px;
    padding: 9px 16px;
    font-weight: 700;
}
QPushButton#dashboardRefresh:hover { background: #eaf3ff; }
QLabel#dashboardSectionTitle {
    color: #193850;
    font-size: 16px;
    font-weight: 700;
}
QFrame#dashboardQuickActions, QFrame#dashboardSection {
    background: #ffffff;
    border: 1px solid #e4ebf2;
    border-radius: 16px;
}
QPushButton#dashboardActionButton {
    background: #f5f8fc;
    color: #28455f;
    border: 1px solid #e1e9f1;
    border-radius: 10px;
    padding: 9px 14px;
    font-weight: 650;
}
QPushButton#dashboardActionButton:hover {
    background: #eaf3ff;
    border-color: #9ec3f8;
    color: #1d66de;
}
QLabel#dashboardLiveBadge {
    background: #e8f7f1;
    color: #16856a;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 10px;
    font-weight: 800;
}
QLabel#dashboardPulse {
    color: #5a748b;
    font-size: 14px;
    line-height: 1.5;
}
"""


class ProfessionalDashboardPage(BaseDashboardPage):
    """Modern dashboard presentation layer built on the existing dashboard logic."""

    def _build(self) -> None:
        self.setStyleSheet(DASHBOARD_STYLESHEET)
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

        lower = QHBoxLayout()
        lower.setSpacing(14)

        activity_card = QFrame()
        activity_card.setObjectName("dashboardSection")
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(20, 18, 20, 18)
        activity_heading = QHBoxLayout()
        self.activity_title = QLabel()
        self.activity_title.setObjectName("dashboardSectionTitle")
        activity_heading.addWidget(self.activity_title)
        activity_heading.addStretch()
        live = QLabel("LIVE")
        live.setObjectName("dashboardLiveBadge")
        activity_heading.addWidget(live)
        activity_layout.addLayout(activity_heading)

        self.activity_list = QListWidget()
        self.activity_list.setObjectName("activityList")
        self.activity_list.setMinimumHeight(190)
        activity_layout.addWidget(self.activity_list)
        lower.addWidget(activity_card, 3)

        pulse_card = QFrame()
        pulse_card.setObjectName("dashboardSection")
        pulse_layout = QVBoxLayout(pulse_card)
        pulse_layout.setContentsMargins(20, 18, 20, 18)
        pulse_layout.addWidget(QLabel("Daily pulse", objectName="dashboardSectionTitle"))
        self.pulse_label = QLabel()
        self.pulse_label.setWordWrap(True)
        self.pulse_label.setObjectName("dashboardPulse")
        pulse_layout.addWidget(self.pulse_label)
        pulse_layout.addStretch()
        lower.addWidget(pulse_card, 2)
        layout.addLayout(lower)

    def refresh(self) -> None:
        super().refresh()
        for index in range(self.stats.count()):
            widget = self.stats.itemAt(index).widget()
            if isinstance(widget, StatCard):
                widget.setObjectName("dashboardMetric")
                widget.setStyleSheet(
                    "QFrame#dashboardMetric { background: #ffffff; border: 1px solid #e4ebf2; "
                    "border-radius: 16px; }"
                )
        self.activity_list.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 12px 6px; border-bottom: 1px solid #edf1f5; }"
            "QListWidget::item:selected { background: #eef5ff; color: #183047; border-radius: 8px; }"
        )
