from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from sqlalchemy import func, select

from .database import Payment
from .main import Expense as LegacyExpense
from .main import ReportsPage as BaseReportsPage
from .models_extended import Expense
from .professional_charts import BarChartWidget


class ProfessionalReportsPage(BaseReportsPage):
    """Existing exports plus visual reporting charts."""

    def __init__(self, db, main_window):
        super().__init__(db, main_window)
        self._add_visual_reports()

    def _add_visual_reports(self) -> None:
        chart_card = QFrame()
        chart_card.setObjectName("card")
        row = QHBoxLayout(chart_card)
        row.setContentsMargins(20, 16, 20, 16)
        row.setSpacing(20)

        income_box = QVBoxLayout()
        income_box.addWidget(QLabel("Income trend", objectName="sectionTitle"))
        self.income_chart = BarChartWidget([], [])
        income_box.addWidget(self.income_chart)
        row.addLayout(income_box, 1)

        expense_box = QVBoxLayout()
        expense_box.addWidget(QLabel("Expenses trend", objectName="sectionTitle"))
        self.expense_chart = BarChartWidget([], [])
        expense_box.addWidget(self.expense_chart)
        row.addLayout(expense_box, 1)

        layout = self.layout()
        if layout is not None:
            layout.insertWidget(max(layout.count() - 1, 0), chart_card)
        self.refresh_visuals()

    def refresh_visuals(self) -> None:
        with self.db.Session() as session:
            payment_rows = session.execute(
                select(func.strftime("%Y-%m", Payment.payment_date), func.coalesce(func.sum(Payment.amount), 0))
                .group_by(func.strftime("%Y-%m", Payment.payment_date))
                .order_by(func.strftime("%Y-%m", Payment.payment_date).desc())
                .limit(6)
            ).all()
            expense_rows = session.execute(
                select(func.strftime("%Y-%m", Expense.expense_date), func.coalesce(func.sum(Expense.amount), 0))
                .group_by(func.strftime("%Y-%m", Expense.expense_date))
                .order_by(func.strftime("%Y-%m", Expense.expense_date).desc())
                .limit(6)
            ).all()
        payment_rows.reverse(); expense_rows.reverse()
        self.income_chart.set_data([row[0] or "—" for row in payment_rows], [float(row[1]) for row in payment_rows])
        self.expense_chart.set_data([row[0] or "—" for row in expense_rows], [float(row[1]) for row in expense_rows])

    def refresh(self) -> None:
        super().refresh()
        if hasattr(self, "income_chart"):
            self.refresh_visuals()
