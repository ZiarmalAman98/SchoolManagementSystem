from __future__ import annotations

from PySide6.QtWidgets import QApplication


LIGHT_THEME = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #f5f8fc; color: #19324a; }
#sidebar { background: #ffffff; border-right: 1px solid #dce6f0; }
#sidebar QLabel { color: #19324a; }
#brandKicker { color: #2979ff; font-size: 10px; font-weight: 800; letter-spacing: 1.4px; }
#brandName { color: #132e47; font-size: 17px; font-weight: 800; }
#sidebarRole { background: #edf4ff; color: #2864bd; border-radius: 9px; padding: 7px 10px; font-weight: 700; }
#sidebarScroll { background: transparent; }
#navButton { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 10px; padding: 10px 12px; color: #526b80; font-weight: 650; }
#navButton:hover { background: #eef5ff; color: #1d66de; }
#navButton:checked { background: #2979ff; color: #ffffff; border-color: #2979ff; }
#logoutButton { text-align: left; background: #fff4f4; border: 1px solid #ffd6d6; border-radius: 10px; padding: 10px 12px; color: #c23a4b; font-weight: 750; }
#logoutButton:hover { background: #ffe7e9; border-color: #f2b8bf; }
#sidebarHelp { background: #f2f7fc; border: 1px solid #dce7f1; border-radius: 12px; padding: 8px; }
#helpTitle { color: #2979ff; font-weight: 800; }
#helpText { color: #6f8497; font-size: 11px; }
#breadcrumb { color: #71879a; font-weight: 700; }
#globalSearch { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 20px; padding: 10px 15px; }
#userBadge { background: #edf4ff; border: 1px solid #d6e5f7; border-radius: 20px; padding: 9px 14px; color: #31506a; font-weight: 700; }
#pageTitle { color: #132e47; font-size: 28px; font-weight: 800; }
#muted { color: #71879a; }
#card { background: #ffffff; border: 1px solid #e0e8f0; border-radius: 15px; }
#primaryButton { background: #2979ff; color: white; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 750; }
#primaryButton:hover { background: #1d66de; }
#ghostButton { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 9px; padding: 9px 14px; color: #28455f; font-weight: 650; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #ffffff; border: 1px solid #d5e0ea; border-radius: 10px; padding: 10px 12px; color: #19324a; }
QTableWidget { background: #ffffff; border: 1px solid #e0e8f0; gridline-color: #edf1f5; alternate-background-color: #f8fafc; selection-background-color: #e5f0ff; selection-color: #183047; border-radius: 12px; }
QHeaderView::section { background: #f1f5f9; color: #60788d; padding: 12px 10px; border: none; border-bottom: 1px solid #dfe7ef; font-weight: 750; }
"""

DARK_THEME = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #0e1b29; color: #e7f1fa; }
#sidebar { background: #132638; border-right: 1px solid #294258; }
#sidebar QLabel { color: #e7f1fa; }
#brandKicker { color: #69a7ff; font-size: 10px; font-weight: 800; letter-spacing: 1.4px; }
#brandName { color: #f2f8fd; font-size: 17px; font-weight: 800; }
#sidebarRole { background: #1c3c59; color: #9bc8ff; border-radius: 9px; padding: 7px 10px; font-weight: 700; }
#navButton { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 10px; padding: 10px 12px; color: #a9c1d5; font-weight: 650; }
#navButton:hover { background: #1c405c; color: #ffffff; }
#navButton:checked { background: #2979ff; color: #ffffff; border-color: #2979ff; }
#logoutButton { text-align: left; background: #3b2530; border: 1px solid #63333f; border-radius: 10px; padding: 10px 12px; color: #ffb5bd; font-weight: 750; }
#logoutButton:hover { background: #51303a; }
#sidebarHelp { background: #17334b; border: 1px solid #2a506d; border-radius: 12px; padding: 8px; }
#helpTitle { color: #69a7ff; font-weight: 800; }
#helpText { color: #a9c1d5; font-size: 11px; }
#breadcrumb, #muted { color: #91a8bb; }
#globalSearch { background: #162638; border: 1px solid #30485c; border-radius: 20px; padding: 10px 15px; color: #e7f1fa; }
#userBadge { background: #1a344c; border: 1px solid #2b4b63; border-radius: 20px; padding: 9px 14px; color: #cfe4f6; font-weight: 700; }
#pageTitle { color: #edf6ff; font-size: 28px; font-weight: 800; }
#card { background: #162638; border: 1px solid #294054; border-radius: 15px; }
#primaryButton { background: #2979ff; color: white; border: none; border-radius: 10px; padding: 11px 18px; font-weight: 750; }
#ghostButton { background: #1b3043; border: 1px solid #30485c; border-radius: 9px; padding: 9px 14px; color: #d5e6f4; font-weight: 650; }
QLineEdit, QComboBox, QSpinBox, QTextEdit { background: #162638; border: 1px solid #30485c; border-radius: 10px; padding: 10px 12px; color: #e7f1fa; }
QTableWidget { background: #162638; border: 1px solid #294054; gridline-color: #263b4f; alternate-background-color: #142433; selection-background-color: #24445d; selection-color: #ffffff; border-radius: 12px; }
QHeaderView::section { background: #1b3043; color: #aac0d2; padding: 12px 10px; border: none; border-bottom: 1px solid #30485c; font-weight: 750; }
"""


def apply_professional_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(DARK_THEME if theme == "dark" else LIGHT_THEME)
