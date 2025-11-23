from PySide6.QtCore import QObject, Signal

"""
This file defines a ModelSignals class that centralizes application-wide Qt signals for when 
different data models change, such as inventory, service activity, equipment, or expenses. 
An instance named model_signals is created for global use, allowing any part of the application 
to emit or listen for these updates. This provides a simple, unified way to trigger UI refreshes 
or other reactions whenever underlying data is modified.
"""

class ModelSignals(QObject):
# Global app-wide change signals.
    inventory_changed = Signal()
    service_activity_changed = Signal()
    equipment_changed = Signal()
    expense_changed = Signal()

    def __init__(self):
        super().__init__()

model_signals = ModelSignals()
