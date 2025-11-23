from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer
from datetime import date
import calendar
from core.logic import get_current_user
from core.models.inventory_model import InventoryItem

"""
This module defines three dashboard-style widgets that provide live visual status indicators for 
key operational tasks. The InventoryCountdownWidget displays a color-coded countdown to the next 
quarterly inventory verification date, the MileageCountdownWidget tracks days remaining until the 
end of the month for submitting mileage and expense reports, and the TonerLevelsWidget scans the 
user’s inventory to generate a dynamic bar chart of printer toner levels. Together, these widgets 
supply at-a-glance reminders and status visuals that help users stay aware of deadlines and supply 
levels within the application.

ui.components.widgets.py index: 

class InventoryCountdownWidget: Displays countdown to next verification date
 - def __init__(): Initialize widget + setup visual layout/timer
 - def update_countdown(): Compute days remaining to next quarterly inv. date
class MileageCountdownWidget: Widget to display countdown to the last day of current month
 - def __init__(): Build countdown UI and start timer.
 - def update_countdown(): Compute days remaining to end of current month
class TonerLevelsWidget: detects printer models from inventory, colors, quantities
 - def __init__(): Build countdown UI and start timer.
 - def toner_color(): Color helper
"""

class InventoryCountdownWidget(QFrame):
# Displays a countdown widget to the next quarterly inventory verification date (Q1: 31Mar, Q2: 30Jun,
# Q3: 30Sep, Q4: 31Dec). Shows "Next Quarterly Inventory", "<N> days", "Target Date: Month, DD, YYYY".
# "<N> days" colors: Green (45+ days remaining), Yellow (15-45 days), Red (less than 14 days).
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #2f2f2f;
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Next Quarterly Inventory")
        self.title.setStyleSheet("font-weight: bold; font-size: 18px;")

        self.days_label = QLabel()
        self.days_label.setStyleSheet("font-weight: bold; font-size: 36px;")

        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 14px;")

        for w in (self.title, self.days_label, self.date_label):
            layout.addWidget(w, alignment=Qt.AlignCenter)

        self.update_countdown()
        timer = QTimer(self)
        timer.timeout.connect(self.update_countdown)
        timer.start(86400000)

    # Countdown logic
    def update_countdown(self):
    # Compute days remaining to next quarterly inv. date, and update labels accordingly.
        today = date.today()
        year = today.year
        quarters = [
            date(year, 3, 31),
            date(year, 6, 30),
            date(year, 9, 30),
            date(year, 12, 31),
        ]
        # Find the quarter date that is >= today.
        next_q = next(
            (q for q in quarters if q >= today),
            date(year + 1, 3, 31)
        )
        days_left = (next_q - today).days
        color = "#00FF7F"
        # If 14 or fewer days remain > urgent (red)
        if days_left <= 14:
            color = "#FF5555"
        # Else if 45 or fewer days remain > caution (yellow)
        elif days_left <= 45:
            color = "#FFD700"

        # Set text like "<N> days"
        self.days_label.setText(f"{days_left} days")

        # Apply style with dynamic color
        self.days_label.setStyleSheet(
            f"font-weight: bold; font-size: 36px; color: {color};"
        )
        # Show the actual date in readable form (e.g. "Target Date: June 30, 2025")
        self.date_label.setText(
            f"Target Date: {next_q.strftime('%B %d, %Y')}"
        )
# Widget to display countdown to the last day of current month (for mileage/expense reports). Color
# rules: 'green' (>10 days), 'yellow' (6-10 days), 'red' (0-5 days).
class MileageCountdownWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #2f2f2f;
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Next Mileage Expense / Employee Expense Report")
        self.title.setStyleSheet("font-weight: bold; font-size: 18px;")
        self.title.setAlignment(Qt.AlignCenter)

        self.days_label = QLabel()
        self.days_label.setAlignment(Qt.AlignCenter)
        self.days_label.setStyleSheet(
            "font-weight: bold; font-size: 36px; color: #00FF7F;"
        )

        self.target_label = QLabel()
        self.target_label.setAlignment(Qt.AlignCenter)
        self.target_label.setStyleSheet("font-size: 14px; color: #dddddd;")

        layout.addWidget(self.title)
        layout.addWidget(self.days_label)
        layout.addWidget(self.target_label)

        self.update_countdown()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(86400000)

    def update_countdown(self):
    # Compute days remaining to end of current month + update display accordingly.
        today = date.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        target_date = date(today.year, today.month, last_day)
        days_left = (target_date - today).days
        self.days_label.setText(f"{days_left} days")
        self.target_label.setText(
            f"Target Date: {target_date.strftime('%B %d, %Y')}"
        )

        if days_left <= 5:
            color = "#FF5555"  # red (very urgent)
        elif days_left <= 10:
            color = "#FFD700"  # yellow (approaching)
        else:
            color = "#00FF7F"  # green (safe)

        self.days_label.setStyleSheet(
            f"font-weight: bold; font-size: 36px; color: {color};"
        )

class TonerLevelsWidget(QWidget):
# Dynamic toner level widget; detects printer models from inventory, colors (black, cyan,
# magenta, yellow), quantities per printer+toner type. Only displays those toner items.
    VALID_COLORS = ("BLACK", "CYAN", "MAGENTA", "YELLOW")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(350)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("Toner Levels (Max 100)")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("color: #ffffff; font: bold 14px 'Segoe UI';")
        layout.addWidget(title)

        # Load inventory for the current user
        user = get_current_user() or "default_user"
        items = InventoryItem.get_all_for_user(user=user)

        # Extract (model, tonerColor) pairs dynamically
        toner_pairs = []
        qty_map = {}

        for it in items:
            model = (it.model or "").strip().upper()
            desc = (it.part_description or "").strip().upper()

            if not model or not desc:
                continue

            if not any(color in desc for color in self.VALID_COLORS):
                continue

            if "TONER" not in desc:
                continue

            key = (model, desc)
            color_name = next(c for c in self.VALID_COLORS if c in desc)
            label = f"{model} {color_name}"

            toner_pairs.append((key, label))
            qty_map[key] = qty_map.get(key, 0) + max(0, it.quantity or 0)

        # Remove duplicates (maintain order)
        seen = set()
        unique_slots = []
        for key, label in toner_pairs:
            if key not in seen:
                seen.add(key)
                unique_slots.append((key, label))
        toner_slots = unique_slots

        if not toner_slots:
            empty_label = QLabel("No toner items found in inventory.")
            empty_label.setStyleSheet("color: #ffffff; font-size: 12px;")
            layout.addWidget(empty_label)
            return

        # Prepare data arrays for bar chart
        MAX_LEVEL = 100
        categories = [label for (_, label) in toner_slots]
        values = []

        for key, _ in toner_slots:
            qty = qty_map.get(key, 0)
            qty = max(0, min(MAX_LEVEL, qty))
            values.append(qty)

        # Build bar chart using PyQtGraph
        import pyqtgraph as pg

        plot = pg.PlotWidget()
        plot.setBackground(None)
        plot.setMenuEnabled(False)
        plot.showGrid(x=False, y=True)
        plot.getPlotItem().getViewBox().setBackgroundColor((255, 255, 255, 30))

        # Hide unused axes
        plot.getPlotItem().getAxis('right').setStyle(showValues=False)
        plot.getPlotItem().getAxis('top').setStyle(showValues=False)

        # X-axis positions
        x_positions = list(range(len(categories)))
        BAR_WIDTH = 0.6

        def toner_color(desc):
            if "BLACK" in desc:
                return (30, 30, 30)
            if "CYAN" in desc:
                return (0, 180, 255)
            if "MAGENTA" in desc:
                return (255, 0, 150)
            if "YELLOW" in desc:
                return (255, 220, 0)
            return (180, 180, 180)

        # Draw bars dynamically
        for idx, ((model, desc), label) in enumerate(toner_slots):
            color = toner_color(desc)
            bar = pg.BarGraphItem(
                x=[idx],
                height=[values[idx]],
                width=BAR_WIDTH,
                brush=color,
                pen=None
            )
            plot.addItem(bar)

        # Configure X-axis labels
        axis = plot.getPlotItem().getAxis('bottom')
        axis.setTicks([[(i, categories[i]) for i in range(len(categories))]])
        axis.setStyle(tickFont=pg.QtGui.QFont("Segoe UI", 8))
        axis.setPen(pg.mkPen(255, 255, 255))
        axis.setTextPen(pg.mkPen(255, 255, 255))

        # Y-axis style
        axis_y = plot.getPlotItem().getAxis('left')
        axis_y.setStyle(tickFont=pg.QtGui.QFont("Segoe UI", 8))
        axis_y.setPen(pg.mkPen(255, 255, 255))
        axis_y.setTextPen(pg.mkPen(255, 255, 255))
        layout.addWidget(plot)


