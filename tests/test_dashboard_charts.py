from app.chart_data import build_bar_points, build_donut_segments


def test_build_bar_points_normalizes_values_and_labels():
    result = build_bar_points([("Jan", 10), ("Feb", 20), ("Mar", 5)])
    assert result.labels == ["Jan", "Feb", "Mar"]
    assert result.values == [10.0, 20.0, 5.0]
    assert result.maximum == 20.0


def test_build_bar_points_handles_empty_data():
    result = build_bar_points([])
    assert result.labels == []
    assert result.values == []
    assert result.maximum == 1.0


def test_build_donut_segments_calculates_percentages():
    result = build_donut_segments([("Present", 75), ("Absent", 25)])
    assert result.labels == ["Present", "Absent"]
    assert result.values == [75.0, 25.0]
    assert result.total == 100.0
    assert [round(item[2], 2) for item in result.segments] == [270.0, 90.0]
