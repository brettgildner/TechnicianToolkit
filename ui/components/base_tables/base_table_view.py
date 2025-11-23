from __future__ import annotations
from PySide6.QtWidgets import QTableView

"""
A reusable, dark-themed QTableView used across multiple pages. Many pages in the application display 
tab data, so instead of rewriting the style/behavior on each page, this class defines shared table 
settings: alternating dark rows, green selection highlight, row-based selection, sorting enabled with 
QSortFilterProxyModel, hidden vertical row numbers, smooth hover tracking for action-button delegates 
(Edit/Delete/Order). This page is used for Expense Reports and Mileage Tracker (the rest of the pages
have functions which require specific action pages.
"""

class BaseTableView(QTableView):
    # Any page that needs a clean, consistent table simply uses:
    # table = BaseTableView()
    def __init__(self, parent=None):
        # Initialize the table view and apply universal styling + behavior.
        super().__init__(parent)

        self.setAlternatingRowColors(True)
        #  Enable alternating light/dark rows for readability

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        #  SelectRows: clicking anywhere in a row selects the whole row.
        #  SingleSelection: only one row can be selected at a time.

        self.setSortingEnabled(True)
        # When a QSortFilterProxyModel is used, clicking column headers sorts the data.

        # -------------------------self.setStyleSheet-------------------------------
        self.setStyleSheet("""
            QTableView {
                background-color: #1a1a1a;
                color: #e0e0e0;
                gridline-color: #333;
                alternate-background-color: #222;
                selection-background-color: #00cc88;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

        #  Header configuration
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        # Don't automatically stretch the last column

        header.setHighlightSections(False)
        # Prevent the header from showing as "selected" when a column sorts-- keeps the UI
        # from flashing blue or highlighting unexpectedly.

        self.verticalHeader().hide()
        # Hide the vertical header (the 1,2,3 row numbers).

        self.setMouseTracking(True)
        # Enable mouse tracking WITHOUT holding mouse buttons. Required for highlighting
        # mini action buttons on hover and changing button color when the cursor moves over.