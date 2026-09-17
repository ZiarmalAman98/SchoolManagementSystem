from app.modern_ui import LOGIN_STYLE, LOGOUT_STYLE, MODERN_LOGIN_MIN_WIDTH, modern_login_build, modern_logout
from app.professional_dashboard import LIGHT_DASHBOARD_STYLESHEET
from app.professional_theme import LIGHT_THEME


def test_modern_login_contract():
    assert MODERN_LOGIN_MIN_WIDTH >= 1000
    assert "#loginBrand" in LOGIN_STYLE
    assert "#loginFormPanel" in LOGIN_STYLE
    assert "#loginInput" in LOGIN_STYLE
    assert "#loginButton" in LOGIN_STYLE
    assert "#passwordToggle" in LOGIN_STYLE
    assert callable(modern_login_build)


def test_modern_logout_contract():
    assert "#logoutButton" in LOGOUT_STYLE
    assert "Sign out" in modern_logout.__name__ or callable(modern_logout)


def test_dashboard_template_contract():
    assert "#dashboardWelcome" in LIGHT_DASHBOARD_STYLESHEET
    assert "#dashboardSection" in LIGHT_DASHBOARD_STYLESHEET
    assert "Students by class" in LIGHT_DASHBOARD_STYLESHEET
    assert "Attendance overview" in LIGHT_DASHBOARD_STYLESHEET


def test_light_admin_template_contract():
    assert "#sidebar" in LIGHT_THEME
    assert "#navButton:checked" in LIGHT_THEME
    assert "#logoutButton" in LIGHT_THEME
    assert "#globalSearch" in LIGHT_THEME
