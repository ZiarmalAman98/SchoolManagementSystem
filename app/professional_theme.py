from __future__ import annotations

from PySide6.QtWidgets import QApplication


LIGHT_THEME = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #f4f7fb; color: #172b4d; }
#sidebar { background: #ffffff; border-right: 1px solid #e3eaf3; }
#sidebar QLabel { color: #172b4d; }
#brandKicker { color: #2563eb; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; }
#brandName { color: #102a43; font-size: 17px; font-weight: 800; }
#sidebarRole { background: #eef5ff; color: #245bb5; border: 1px solid #dceaff; border-radius: 9px; padding: 7px 10px; font-weight: 700; }
#sidebarScroll { background: transparent; border: none; }
#navButton { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 11px; padding: 10px 13px; color: #64748b; font-weight: 650; }
#navButton:hover { background: #f1f6ff; color: #2563eb; border-color: #e0ebff; }
#navButton:checked { background: #2563eb; color: #ffffff; border-color: #2563eb; }
#navButton:checked:hover { background: #1d4ed8; border-color: #1d4ed8; }
#logoutButton { text-align: left; background: #fff5f5; border: 1px solid #fee0e2; border-radius: 11px; padding: 10px 13px; color: #c2414f; font-weight: 750; }
#logoutButton:hover { background: #ffecee; border-color: #f7c7cc; }
#sidebarHelp { background: #f7faff; border: 1px solid #e2eaf4; border-radius: 13px; padding: 8px; }
#helpTitle { color: #2563eb; font-weight: 800; }
#helpText { color: #718096; font-size: 11px; }
#breadcrumb { color: #7b8ba1; font-weight: 700; }
#globalSearch { background: #ffffff; border: 1px solid #dce5ef; border-radius: 21px; padding: 10px 15px; color: #172b4d; }
#globalSearch:focus { border: 1px solid #8bb7ff; }
#userBadge { background: #ffffff; border: 1px solid #dce5ef; border-radius: 20px; padding: 9px 14px; color: #40566e; font-weight: 700; }
#pageTitle { color: #102a43; font-size: 28px; font-weight: 800; }
#muted { color: #718096; }
#card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 15px; }
#primaryButton { background: #2563eb; color: #ffffff; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 750; }
#primaryButton:hover { background: #1d4ed8; }
#ghostButton { background: #ffffff; border: 1px solid #d8e1eb; border-radius: 9px; padding: 9px 14px; color: #334e68; font-weight: 650; }
#ghostButton:hover { background: #f7faff; border-color: #b8cbea; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #ffffff; border: 1px solid #d8e1eb; border-radius: 10px; padding: 10px 12px; color: #172b4d; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus { border: 1px solid #7aaeff; }
QTableWidget { background: #ffffff; border: 1px solid #e1e8f0; gridline-color: #edf1f5; alternate-background-color: #f9fbfd; selection-background-color: #e7f0ff; selection-color: #183047; border-radius: 12px; }
QHeaderView::section { background: #f5f7fa; color: #60748a; padding: 12px 10px; border: none; border-bottom: 1px solid #e1e8f0; font-weight: 750; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 3px; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

DARK_THEME = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #0f1d2b; color: #e7f1fa; }
#sidebar { background: #132638; border-right: 1px solid #294258; }
#sidebar QLabel { color: #e7f1fa; }
#brandKicker { color: #69a7ff; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; }
#brandName { color: #f2f8fd; font-size: 17px; font-weight: 800; }
#sidebarRole { background: #1c3c59; color: #9bc8ff; border: 1px solid #2a506d; border-radius: 9px; padding: 7px 10px; font-weight: 700; }
#sidebarScroll { background: transparent; border: none; }
#navButton { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 11px; padding: 10px 13px; color: #a9c1d5; font-weight: 650; }
#navButton:hover { background: #1c405c; color: #ffffff; border-color: #28516e; }
#navButton:checked { background: #2979ff; color: #ffffff; border-color: #2979ff; }
#logoutButton { text-align: left; background: #3b2530; border: 1px solid #63333f; border-radius: 11px; padding: 10px 13px; color: #ffb5bd; font-weight: 750; }
#logoutButton:hover { background: #51303a; }
#sidebarHelp { background: #17334b; border: 1px solid #2a506d; border-radius: 13px; padding: 8px; }
#helpTitle { color: #69a7ff; font-weight: 800; }
#helpText { color: #a9c1d5; font-size: 11px; }
#breadcrumb, #muted { color: #91a8bb; }
#globalSearch { background: #162638; border: 1px solid #30485c; border-radius: 21px; padding: 10px 15px; color: #e7f1fa; }
#userBadge { background: #1a344c; border: 1px solid #2b4b63; border-radius: 20px; padding: 9px 14px; color: #cfe4f6; font-weight: 700; }
#pageTitle { color: #edf6ff; font-size: 28px; font-weight: 800; }
#card { background: #162638; border: 1px solid #294054; border-radius: 15px; }
#primaryButton { background: #2979ff; color: #ffffff; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 750; }
#primaryButton:hover { background: #1d66de; }
#ghostButton { background: #1b3043; border: 1px solid #30485c; border-radius: 9px; padding: 9px 14px; color: #d5e6f4; font-weight: 650; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #162638; border: 1px solid #30485c; border-radius: 10px; padding: 10px 12px; color: #e7f1fa; }
QTableWidget { background: #162638; border: 1px solid #294054; gridline-color: #263b4f; alternate-background-color: #142433; selection-background-color: #24445d; selection-color: #ffffff; border-radius: 12px; }
QHeaderView::section { background: #1b3043; color: #aac0d2; padding: 12px 10px; border: none; border-bottom: 1px solid #30485c; font-weight: 750; }
"""


def apply_professional_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(DARK_THEME if theme == "dark" else LIGHT_THEME)
