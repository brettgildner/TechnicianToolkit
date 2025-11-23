from __future__ import annotations
from datetime import date
from typing import Optional
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,QDateEdit, QDialogButtonBox)
from core.models.expense_report_header_model import ExpenseReportHeader

"""
This page contains information to map the labels of the header fields within the Expense Report
page which need to be filled out prior to exporting the expense report to the blank Excel document,
so that these fields are properly filled in within the destination Excel document.
"""

class ExpenseHeaderDialog(QDialog):
    def __init__(self, parent, header: ExpenseReportHeader):
        super().__init__(parent)
        self.setWindowTitle("Expense Report Info")
        self.header = header

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        # --- Text fields ---
        self.name_edit = QLineEdit(header.name)
        self.emp_edit = QLineEdit(header.employee_number)
        self.tel_edit = QLineEdit(header.telephone_number)
        self.mail_team_edit = QLineEdit(header.mail_team)
        self.group_edit = QLineEdit(header.group)
        self.division_edit = QLineEdit(header.division)
        self.dest_purpose_edit = QLineEdit(header.destination_purpose)
        self.bc_edit = QLineEdit(header.bc)
        self.account_edit = QLineEdit(header.account_number)

        # Dates
        def to_qdate(d: Optional[date]) -> QDate:
            if d is None:
                return QDate.currentDate()
            return QDate(d.year, d.month, d.day)

        self.report_date_edit = QDateEdit()
        self.report_date_edit.setCalendarPopup(True)
        self.report_date_edit.setDate(to_qdate(header.report_date))

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(to_qdate(header.start_date))

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(to_qdate(header.end_date))

        # Add form rows
        form.addRow("Name:", self.name_edit)
        form.addRow("Employee Number:", self.emp_edit)
        form.addRow("Telephone Number:", self.tel_edit)
        form.addRow("Mail/Team:", self.mail_team_edit)
        form.addRow("Group:", self.group_edit)
        form.addRow("Division:", self.division_edit)
        form.addRow("Destination / Purpose:", self.dest_purpose_edit)
        form.addRow("Report Date:", self.report_date_edit)
        form.addRow("Start Date:", self.start_date_edit)
        form.addRow("End Date:", self.end_date_edit)
        form.addRow("B/C:", self.bc_edit)
        form.addRow("Account Number:", self.account_edit)

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def apply_to_header(self):
        # Copy widget values back into the header dataclass.
        self.header.name = self.name_edit.text().strip()
        self.header.employee_number = self.emp_edit.text().strip()
        self.header.telephone_number = self.tel_edit.text().strip()
        self.header.mail_team = self.mail_team_edit.text().strip()
        self.header.group = self.group_edit.text().strip()
        self.header.division = self.division_edit.text().strip()
        self.header.destination_purpose = self.dest_purpose_edit.text().strip()
        self.header.bc = self.bc_edit.text().strip()
        self.header.account_number = self.account_edit.text().strip()

        self.header.report_date = self.report_date_edit.date().toPython()
        self.header.start_date = self.start_date_edit.date().toPython()
        self.header.end_date = self.end_date_edit.date().toPython()
