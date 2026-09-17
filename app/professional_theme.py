from __future__ import annotations

from PySide6.QtWidgets import QApplication


LIGHT_THEME = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #f7f5ff; color: #302642; }
#sidebar { background: #ffffff; border-right: 1px solid #e7def4; }
#sidebar QLabel { color: #302642; }
#brandKicker { color: #7c3aed; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; }
#brandName { color: #35205f; font-size: 17px; font-weight: 800; }
#sidebarRole { background: #f0eaff; color: #6941b4; border: 1px solid #ded0fa; border-radius: 9px; padding: 7px 10px; font-weight: 700; }
#sidebarScroll { background: transparent; border: none; }
#navButton { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 11px; padding: 10px 13px; color: #766a89; font-weight: 650; }
#navButton:hover { background: #f4efff; color: #7c3aed; border-color: #e7ddfb; }
#navButton:checked { background: #7c3aed; color: #ffffff; border-color: #7c3aed; }
#navButton:checked:hover { background: #6d28d9; border-color: #6d28d9; }
#logoutButton { text-align: left; background: #fff4f7; border: 1px solid #f7dce5; border-radius: 11px; padding: 10px 13px; color: #c2416b; font-weight: 750; }
#logoutButton:hover { background: #ffebf1; border-color: #efc4d4; }
#sidebarHelp { background: #faf8ff; border: 1px solid #e8e0f5; border-radius: 13px; padding: 8px; }
#helpTitle { color: #7c3aed; font-weight: 800; }
#helpText { color: #827791; font-size: 11px; }
#breadcrumb { color: #8b7d9d; font-weight: 700; }
#globalSearch { background: #ffffff; border: 1px solid #e2dced; border-radius: 21px; padding: 10px 15px; color: #302642; }
#globalSearch:focus { border: 1px solid #a78bfa; }
#userBadge { background: #ffffff; border: 1px solid #e2dced; border-radius: 20px; padding: 9px 14px; color: #5d5070; font-weight: 700; }
#pageTitle { color: #35205f; font-size: 28px; font-weight: 800; }
#muted { color: #827791; }
#card { background: #ffffff; border: 1px solid #e8e1f2; border-radius: 15px; }
#primaryButton { background: #7c3aed; color: #ffffff; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 750; }
#primaryButton:hover { background: #6d28d9; }
#ghostButton { background: #ffffff; border: 1px solid #ddd5ec; border-radius: 9px; padding: 9px 14px; color: #514368; font-weight: 650; }
#ghostButton:hover { background: #faf8ff; border-color: #c5b5df; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #ffffff; border: 1px solid #ddd5ec; border-radius: 10px; padding: 10px 12px; color: #302642; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus { border: 1px solid #a78bfa; }
QTableWidget { background: #ffffff; border: 1px solid #e5dff0; gridline-color: #f0ebf6; alternate-background-color: #fbfaff; selection-background-color: #eee6ff; selection-color: #35205f; border-radius: 12px; }
QHeaderView::section { background: #f7f4fb; color: #6f6380; padding: 12px 10px; border: none; border-bottom: 1px solid #e5dff0; font-weight: 750; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 3px; }
QScrollBar::handle:vertical { background: #cbbde0; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

DARK_THEME = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #171125; color: #eee9f8; }
#sidebar { background: #211735; border-right: 1px solid #3b2b56; }
#sidebar QLabel { color: #eee9f8; }
#brandKicker { color: #b892ff; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; }
#brandName { color: #faf8ff; font-size: 17px; font-weight: 800; }
#sidebarRole { background: #352451; color: #d2baff; border: 1px solid #4b376b; border-radius: 9px; padding: 7px 10px; font-weight: 700; }
#sidebarScroll { background: transparent; border: none; }
#navButton { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 11px; padding: 10px 13px; color: #b8a9cd; font-weight: 650; }
#navButton:hover { background: #35244f; color: #ffffff; border-color: #4b376b; }
#navButton:checked { background: #8b5cf6; color: #ffffff; border-color: #8b5cf6; }
#logoutButton { text-align: left; background: #3c2532; border: 1px solid #633848; border-radius: 11px; padding: 10px 13px; color: #ffb9c8; font-weight: 750; }
#logoutButton:hover { background: #513040; }
#sidebarHelp { background: #2b1d42; border: 1px solid #4b376b; border-radius: 13px; padding: 8px; }
#helpTitle { color: #b892ff; font-weight: 800; }
#helpText { color: #b8a9cd; font-size: 11px; }
#breadcrumb, #muted { color: #a99abf; }
#globalSearch { background: #251a39; border: 1px solid #46345f; border-radius: 21px; padding: 10px 15px; color: #eee9f8; }
#userBadge { background: #2a1d40; border: 1px solid #46345f; border-radius: 20px; padding: 9px 14px; color: #ddd0ed; font-weight: 700; }
#pageTitle { color: #faf8ff; font-size: 28px; font-weight: 800; }
#card { background: #211735; border: 1px solid #3b2b56; border-radius: 15px; }
#primaryButton { background: #8b5cf6; color: #ffffff; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 750; }
#primaryButton:hover { background: #7c3aed; }
#ghostButton { background: #2b2040; border: 1px solid #46345f; border-radius: 9px; padding: 9px 14px; color: #e4daf2; font-weight: 650; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #251a39; border: 1px solid #46345f; border-radius: 10px; padding: 10px 12px; color: #eee9f8; }
QTableWidget { background: #211735; border: 1px solid #3b2b56; gridline-color: #322546; alternate-background-color: #1d142e; selection-background-color: #3b2860; selection-color: #ffffff; border-radius: 12px; }
QHeaderView::section { background: #2b2040; color: #c6b8d8; padding: 12px 10px; border: none; border-bottom: 1px solid #46345f; font-weight: 750; }
"""


def apply_professional_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(DARK_THEME if theme == "dark" else LIGHT_THEME)
