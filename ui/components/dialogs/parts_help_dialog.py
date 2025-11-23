from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog

"""
This module defines the PartsHelpDialog-- a help window that helps users with properly using the 
Parts Order page. It explains the 'Export to CSV' function, filtering and column visibility, and 
sorting tools. 
"""

class PartsHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help – Parts Order Page")
        self.resize(650, 520)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("Using the Parts Orders Page")
        title.setStyleSheet("font: bold 20px 'Segoe UI'; color: #00ff99;")
        layout.addWidget(title)

        # Adding / Editing Orders
        section1 = QLabel(
            "<h3 style='color:#00ff99;'>Adding and Editing Parts Orders</h3>"
            "<p>You can manage your parts orders directly from this page.</p>"
            "<ul>"
            "<li>Click <b>+ Add Parts Order</b> to create a new entry.</li>"
            "<li>Double-click any row to edit that order.</li>"
            "<li>The Edit and Delete buttons are available in the Actions column.</li>"
            "<li>All fields you enter are saved to your local database and persist across sessions.</li>"
            "</ul>"
        )
        section1.setWordWrap(True)
        section1.setStyleSheet("color: #ddd;")
        layout.addWidget(section1)

        # Filters
        section2 = QLabel(
            "<h3 style='color:#00ff99;'>Filtering Parts Orders</h3>"
            "<p>The Filters button opens a panel that lets you narrow down your parts list.</p>"
            "<ul>"
            "<li>You can type text to filter each column individually.</li>"
            "<li>Filtering is case-insensitive and matches any part of the text.</li>"
            "<li>Multiple filters may be active at the same time.</li>"
            "<li>Clear Filters removes all filters and shows all orders.</li>"
            "</ul>"
        )
        section2.setWordWrap(True)
        section2.setStyleSheet("color: #ddd;")
        layout.addWidget(section2)

        # Sorting
        section3 = QLabel(
            "<h3 style='color:#00ff99;'>Sorting the Table</h3>"
            "<p>You can sort by any column header.</p>"
            "<ul>"
            "<li>Left-click a header to sort ascending.</li>"
            "<li>Click again to sort descending.</li>"
            "<li>Sorting works together with your filters.</li>"
            "</ul>"
        )
        section3.setWordWrap(True)
        section3.setStyleSheet("color: #ddd;")
        layout.addWidget(section3)

        # Export to CSV
        section4 = QLabel(
            "<h3 style='color:#00ff99;'>Exporting Parts Orders to CSV</h3>"
            "<p>The <b>Export CSV</b> button generates a CSV file containing the "
            "<b>currently visible</b> (filtered) table rows.</p>"
            "<ul>"
            "<li>The exported file includes Part Number, Model, Description, and Quantity.</li>"
            "<li>You can open the CSV in Excel or upload it to your parts order form.</li>"
            "<li>Hidden rows (because of filters) are <b>not included</b> in the export.</li>"
            "<li>This feature is useful when filling out purchase order forms manually.</li>"
            "</ul>"
        )
        section4.setWordWrap(True)
        section4.setStyleSheet("color: #ddd;")
        layout.addWidget(section4)

        # Close Button
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(120)
        btn_close.clicked.connect(self.accept)
        btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        btn_close.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: #fff;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_close)
        layout.addLayout(bottom)