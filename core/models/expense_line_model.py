from dataclasses import dataclass
from datetime import date
from typing import Optional

"""
This module defines the ExpenseLine dataclass, which represents a single line-item entry in an 
expense report, including travel, lodging, meal, and miscellaneous cost fields.
"""

@dataclass
class ExpenseLine:
    expense_date: Optional[date] = None
    destination: str = ""
    miles: float = 0.0
    rental: float = 0.0
    air_cash: float = 0.0
    air: float = 0.0
    hotel: float = 0.0
    meals: float = 0.0
    ent_bus_mtgs: float = 0.0
    parking: float = 0.0
    telephone: float = 0.0
    misc: float = 0.0
    explanation: str = ""
