from app.modern_ui import LOGIN_STYLE, LOGOUT_STYLE, MODERN_LOGIN_MIN_WIDTH


def test_modern_login_contract():
    assert MODERN_LOGIN_MIN_WIDTH >= 1000
    assert "#loginInput" in LOGIN_STYLE
    assert "#loginButton" in LOGIN_STYLE
    assert "#passwordToggle" in LOGIN_STYLE


def test_modern_logout_contract():
    assert "#logoutButton" in LOGOUT_STYLE
    assert "QMessageBox" in LOGOUT_STYLE
