from dataclasses import dataclass
from datetime import date
from typing import Optional

"""
This page defines a simple ExpenseReportHeader dataclass used to store the top-level metadata 
for an expense report. It contains fields for employee information, contact details, organizational 
data, report purpose, and the relevant date range. The class acts as a structured container for 
passing or saving header information throughout the application.
"""

@dataclass
class ExpenseReportHeader:
    name: str = ""
    employee_number: str = ""
    telephone_number: str = ""
    mail_team: str = ""
    group: str = ""
    division: str = ""
    destination_purpose: str = ""
    report_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bc: str = ""
    account_number: str = ""
