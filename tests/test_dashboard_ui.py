from pathlib import Path


DASHBOARD_PY = Path(__file__).resolve().parents[1] / "app" / "professional_dashboard.py"


def test_dashboard_has_professional_summary_and_quick_actions():
    source = DASHBOARD_PY.read_text(encoding="utf-8")

    assert 'objectName("dashboardWelcome")' in source
    assert 'objectName("dashboardQuickActions")' in source
    assert 'objectName("dashboardMetric")' in source
    assert 'objectName("dashboardSection")' in source


def test_dashboard_styles_define_the_new_visual_language():
    source = DASHBOARD_PY.read_text(encoding="utf-8")

    assert "QFrame#dashboardWelcome" in source
    assert "QFrame#dashboardQuickActions" in source
    assert "QFrame#dashboardMetric" in source
    assert "QFrame#dashboardSection" in source
