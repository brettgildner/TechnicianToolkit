from __future__ import annotations
from datetime import date
from typing import Optional
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,QDoubleSpinBox,
                               QDateEdit, QDialogButtonBox)
from core.models.expense_line_model import ExpenseLine

"""
This page defines a popup dialog used to add or edit a single expense entry for an expense report. 
It displays form fields for date, destination, mileage, travel costs, meals, lodging, and other 
expense categories, pre-filled when editing an existing entry. The form bundles all user input into 
an ExpenseLine dataclass, allowing the application to easily retrieve and store structured expense 
data.
"""

class ExpenseEntryForm(QDialog):
# Popup dialog to add or edit a single expense entry. Uses ExpenseLine dataclass, not DB.
    def __init__(self, parent, entry: Optional[ExpenseLine] = None):
        super().__init__(parent)

        self.setWindowTitle("Expense Entry")
        self.setModal(True)

        self.entry = entry or ExpenseLine()

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        # --- Date ---
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)

        if isinstance(self.entry.expense_date, date):
            d = self.entry.expense_date
            self.date_edit.setDate(QDate(d.year, d.month, d.day))
        else:
            self.date_edit.setDate(QDate.currentDate())

        # --- Destination ---
        self.dest_edit = QLineEdit(self.entry.destination)

        # Helper
        def money(val: float) -> QDoubleSpinBox:
            w = QDoubleSpinBox()
            w.setRange(0, 1_000_000)
            w.setDecimals(2)
            w.setValue(float(val or 0))
            return w

        # Money widgets
        self.miles_spin = money(self.entry.miles)
        self.rental_spin = money(self.entry.rental)
        self.air_cash_spin = money(self.entry.air_cash)
        self.air_spin = money(self.entry.air)
        self.hotel_spin = money(self.entry.hotel)
        self.meals_spin = money(self.entry.meals)
        self.ent_bus_spin = money(self.entry.ent_bus_mtgs)
        self.parking_spin = money(self.entry.parking)
        self.telephone_spin = money(self.entry.telephone)
        self.misc_spin = money(self.entry.misc)

        self.expl_edit = QLineEdit(self.entry.explanation)

        # Add rows
        form.addRow("Date:", self.date_edit)
        form.addRow("Destination:", self.dest_edit)
        form.addRow("# of miles:", self.miles_spin)
        form.addRow("Rental:", self.rental_spin)
        form.addRow("Air-Cash:", self.air_cash_spin)
        form.addRow("Air:", self.air_spin)
        form.addRow("Hotel:", self.hotel_spin)
        form.addRow("Meals:", self.meals_spin)
        form.addRow("Ent. Bus. Mtgs.:", self.ent_bus_spin)
        form.addRow("Parking:", self.parking_spin)
        form.addRow("Telephone:", self.telephone_spin)
        form.addRow("Misc.:", self.misc_spin)
        form.addRow("Explanation:", self.expl_edit)

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    # -----------------------------------------------------------

    def to_entry(self) -> ExpenseLine:
    # Return an ExpenseLine populated from the dialog fields.
        line = ExpenseLine()
        line.expense_date = self.date_edit.date().toPython()
        line.destination = self.dest_edit.text().strip()
        line.miles = self.miles_spin.value()
        line.rental = self.rental_spin.value()
        line.air_cash = self.air_cash_spin.value()
        line.air = self.air_spin.value()
        line.hotel = self.hotel_spin.value()
        line.meals = self.meals_spin.value()
        line.ent_bus_mtgs = self.ent_bus_spin.value()
        line.parking = self.parking_spin.value()
        line.telephone = self.telephone_spin.value()
        line.misc = self.misc_spin.value()
        line.explanation = self.expl_edit.text().strip()
        return line
