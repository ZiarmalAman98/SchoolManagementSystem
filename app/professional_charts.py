from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget


class BarChartWidget(QWidget):
    def __init__(self, labels: list[str], values: list[float], parent=None):
        super().__init__(parent)
        self.labels = labels
        self.values = values
        self.setMinimumHeight(220)
        self.setMinimumWidth(420)

    def set_data(self, labels: list[str], values: list[float]) -> None:
        self.labels, self.values = labels, values
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(34, 18, -18, -30)
        painter.setPen(QPen(self.palette().mid().color(), 1))
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
        if not self.values:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "No data available")
            return
        maximum = max(max(self.values), 1.0)
        count = len(self.values)
        slot = rect.width() / count
        bar_width = min(52.0, slot * 0.62)
        for index, value in enumerate(self.values):
            height = (value / maximum) * (rect.height() - 24)
            x = rect.left() + index * slot + (slot - bar_width) / 2
            y = rect.bottom() - height
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.palette().highlight().color()))
            painter.drawRoundedRect(QRectF(x, y, bar_width, height), 6, 6)
            painter.setPen(self.palette().text().color())
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(QRectF(x - 8, y - 20, bar_width + 16, 18), Qt.AlignmentFlag.AlignCenter, f"{value:g}")
            label = self.labels[index][:12] if index < len(self.labels) else ""
            painter.drawText(QRectF(x - 20, rect.bottom() + 6, bar_width + 40, 20), Qt.AlignmentFlag.AlignCenter, label)


class DonutChartWidget(QWidget):
    def __init__(self, labels: list[str], values: list[float], parent=None):
        super().__init__(parent)
        self.labels = labels
        self.values = values
        self.setMinimumHeight(220)
        self.setMinimumWidth(300)

    def set_data(self, labels: list[str], values: list[float]) -> None:
        self.labels, self.values = labels, values
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        total = sum(max(float(v), 0.0) for v in self.values)
        if total <= 0:
            painter.setPen(self.palette().text().color())
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No attendance data")
            return
        size = min(self.width() - 100, self.height() - 30)
        diameter = max(100, size)
        x = 18
        y = (self.height() - diameter) / 2
        colors = [self.palette().highlight().color(), self.palette().link().color(), self.palette().mid().color(), self.palette().text().color()]
        start = 0.0
        for index, value in enumerate(self.values):
            span = max(float(value), 0.0) / total * 360.0
            painter.setPen(QPen(self.palette().base().color(), 1))
            painter.setBrush(QBrush(colors[index % len(colors)]))
            painter.drawPie(QRectF(x, y, diameter, diameter), int(start * 16), int(span * 16))
            start += span
        painter.setBrush(QBrush(self.palette().window().color()))
        painter.setPen(Qt.PenStyle.NoPen)
        hole = diameter * 0.58
        painter.drawEllipse(QRectF(x + (diameter-hole)/2, y + (diameter-hole)/2, hole, hole))
        painter.setPen(self.palette().text().color())
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.drawText(QRectF(x, y + diameter * .42, diameter, 28), Qt.AlignmentFlag.AlignCenter, f"{int(total)}")
        legend_x = x + diameter + 18
        painter.setFont(QFont("Segoe UI", 9))
        for index, (label, value) in enumerate(zip(self.labels, self.values)):
            yy = 28 + index * 30
            painter.setBrush(QBrush(colors[index % len(colors)]))
            painter.drawRoundedRect(QRectF(legend_x, yy, 10, 10), 2, 2)
            painter.setPen(self.palette().text().color())
            pct = value / total * 100 if total else 0
            painter.drawText(QRectF(legend_x + 16, yy - 5, self.width() - legend_x - 18, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{label}: {pct:.0f}%")
