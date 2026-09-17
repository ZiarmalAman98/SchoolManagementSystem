from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BarPoints:
    labels: list[str]
    values: list[float]
    maximum: float


@dataclass(frozen=True)
class DonutSegments:
    labels: list[str]
    values: list[float]
    total: float
    segments: list[tuple[str, float, float]]


def build_bar_points(items: list[tuple[str, float]]) -> BarPoints:
    labels = [str(label) for label, _ in items]
    values = [float(value) for _, value in items]
    return BarPoints(labels, values, max(values) if values else 1.0)


def build_donut_segments(items: list[tuple[str, float]]) -> DonutSegments:
    labels = [str(label) for label, _ in items]
    values = [max(float(value), 0.0) for _, value in items]
    total = sum(values)
    segments: list[tuple[str, float, float]] = []
    if total:
        for label, value in zip(labels, values):
            segments.append((label, value, value / total * 360.0))
    return DonutSegments(labels, values, total, segments)
