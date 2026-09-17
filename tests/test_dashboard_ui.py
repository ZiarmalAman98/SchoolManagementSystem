from pathlib import Path


MAIN_PY = Path(__file__).resolve().parents[1] / "app" / "main.py"


def test_dashboard_has_professional_summary_and_quick_actions():
    source = MAIN_PY.read_text(encoding="utf-8")

    assert 'objectName("dashboardWelcome")' in source
    assert 'objectName("dashboardQuickActions")' in source
    assert 'objectName("dashboardMetric")' in source
    assert 'objectName("dashboardSection")' in source


def test_dashboard_styles_define_the_new_visual_language():
    source = MAIN_PY.read_text(encoding="utf-8")

    assert "#dashboardWelcome" in source
    assert "#dashboardQuickActions" in source
    assert "#dashboardMetric" in source
    assert "#dashboardSection" in source
