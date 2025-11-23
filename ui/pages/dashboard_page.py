from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame,
                               QGridLayout, QSizePolicy)
from PySide6.QtGui import QPixmap, QIcon, QFont, QCursor
from PySide6.QtCore import Qt, QTimer, QSize
import os
from core.models.inventory_model import InventoryItem
from core.models.mileage_model import MileageEntry
from core.models.service_activity_model import ServiceActivity
from core.logic import get_current_user
from ui.components.widgets import InventoryCountdownWidget, MileageCountdownWidget

# Path to locate images and icons for the dashboard
ASSETS = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

"""
This page defines the main Dashboard screen that users see after logging into the application. It 
constructs a visually rich interface that displays key information such as inventory statistics, 
mileage logs, countdown widgets, toner status, shortcut buttons for common tasks, and a list of recent 
service activity. The dashboard retrieves live data from the database, reacts to model-change signals 
to update widgets, and provides navigation helpers to jump to other sections of the app. Overall, it 
serves as the central hub for quick insights and fast access to the app’s primary features.

ui.pages.dashboard_page.py index:
class DashboardPage(): Main application home screen.
- def __init__(): Build dashboard UI and load data.
    - def create_stat_card(): Make inventory/mileage stat card.
    - def create_shortcut(): Create dashboard shortcut button.
- def _navigate_to(): Navigate to another app page.
- def _create_service_item(): Build a clickable recent-service card.
    - def truncate(): Shorten long text.
    - def enterEvent(): Apply hover-in highlight.
    - def leaveEvent(): Revert hover highlight.
- def refresh_toner_widget(): Rebuild and refresh toner widget.
- def refresh_recent_activity(): Reload recent service activity list.
"""

# This class defines everything the Dashboard screen displays where user is taken upon
# successful login.
class DashboardPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)

        # "controller" is the object that manages page navigation.
        self.controller = controller

        # Get the username of whoever is logged in, or revert to a default.
        user = get_current_user() or "default_user"

        # Main vertical layout: everything on the dashboard page is added inside this layout.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Background image (potential future addition, sets a full-screen background image).
        bg_path = os.path.join(ASSETS, "images", "dashboard_bg.png")
        if os.path.exists(bg_path):
            self.setAutoFillBackground(True)
            self.setStyleSheet(f"""
                QWidget {{
                    background-image: url("{bg_path.replace(os.sep, '/')}");
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    background-color: #111111;
                }}
            """)

        # Header section (Logo + Title), appears at very top of dashboard.
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # If logo file exists, show it.
        logo_path = os.path.join(ASSETS, "icons", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            header_layout.addWidget(logo_label, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # Text “Dashboard”
        title_label = QLabel("Dashboard")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setStyleSheet("color: #e0e0e0;")
        header_layout.addWidget(title_label, 0, Qt.AlignLeft)

        # Push everything else to the left
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # =============================CURRENTLY=REMOVED====================================
        # STATISTICS CARDS
        # Displays 3 small “cards” with important numbers:
        # - Total inventory items
        # - Number of low-stock items
        # - Total mileage logs

        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        stats_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 12px;")

        # Pull data from the database:
        inventory_items = InventoryItem.get_all_for_user(user)
        inventory_count = len(inventory_items)

        # Count items that have 5 or fewer units.
        low_stock = len([i for i in inventory_items if i.quantity <= 5])
        mileage_count = len(MileageEntry.get_all_for_user(user))

        # Helper to create each card box
        def create_stat_card(title, value, icon_path):
            card = QFrame()
            card.setStyleSheet("background-color: #2a2a2a; border-radius: 12px;")
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            card_layout.setSpacing(6)

            # Optional icon for visual flare
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                icon_label.setAlignment(Qt.AlignCenter)
                card_layout.addWidget(icon_label)

            # Main label on card
            title_lbl = QLabel(title)
            title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
            title_lbl.setStyleSheet("color: #ffffff;")
            card_layout.addWidget(title_lbl)

            # Value (the number)
            value_lbl = QLabel(str(value))
            value_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
            value_lbl.setStyleSheet("color: #00ff88;")
            card_layout.addWidget(value_lbl)
            return card

        # Add the 3 statistic cards to the grid layout
        stats_layout.addWidget(create_stat_card("Inventory Items", inventory_count, os.path.join(ASSETS, "icons", "inventory.png")), 0, 0)
        stats_layout.addWidget(create_stat_card("Low Stock", low_stock, os.path.join(ASSETS, "icons", "warning.png")), 0, 1)
        stats_layout.addWidget(create_stat_card("Mileage Logs", mileage_count, os.path.join(ASSETS, "icons", "mileage.png")), 0, 2)

        # UNCOMMENT BELOW TO ADD WIDGETS BACK ONTO DASHBOARD
        # main_layout.addWidget(stats_frame)
        # UNCOMMENT ABOVE TO ADD WIDGETS BACK ONTO DASHBOARD

        # =============================CURRENTLY=REMOVED====================================

        # Countdown widgets showing (1) days since last inventory verification and (2) days since
        # the last mileage log was submitted (or, more accurately, since the first of the month).
        countdown_frame = QFrame()
        countdown_frame.setStyleSheet("background-color: #1f1f1f; border-radius: 12px;")
        countdown_layout = QGridLayout(countdown_frame)
        countdown_layout.setSpacing(10)
        countdown_layout.setContentsMargins(10, 10, 10, 10)

        inventory_widget = InventoryCountdownWidget(countdown_frame)
        mileage_widget = MileageCountdownWidget(countdown_frame)
        countdown_layout.addWidget(inventory_widget, 0, 0)
        countdown_layout.addWidget(mileage_widget, 0, 1)

        main_layout.addWidget(countdown_frame)

        # ---- Toner levels widget ----
        from ui.components.widgets import TonerLevelsWidget
        self.toner_widget = TonerLevelsWidget(self)
        main_layout.addWidget(self.toner_widget)
        # -----------------------------
        # ---- Connect model signals ----
        from ui.signals.model_signals import model_signals
        model_signals.inventory_changed.connect(self.refresh_toner_widget)
        model_signals.service_activity_changed.connect(self.refresh_recent_activity)

        # Shortcut buttons that jump the user to: Add Inventory | Log Trip | Order Parts | Log Service
        shortcut_frame = QFrame()
        shortcut_frame.setStyleSheet("background-color: #1f1f1f; border-radius: 12px;")
        shortcut_layout = QGridLayout(shortcut_frame)
        shortcut_layout.setSpacing(8)
        shortcut_layout.setContentsMargins(10, 10, 10, 10)

        def create_shortcut(text, icon_path, callback, background_color=None):
            btn = QPushButton()
            btn.setText(text)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedSize(250, 50)

            # Default styling (if no custom color passed)
            base_color = background_color or "#2a2a2a"
            hover_color = "#333333"

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {base_color};
                    color: #ffffff;
                    border-radius: 12px;
                    font: bold 16px 'Segoe UI';
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                    color: #00ff99;
                }}
            """)

            btn.clicked.connect(callback)
            return btn

        # Green gradient colors (left > right)
        g1 = "#00cc55"  # bright green
        g2 = "#009944"
        g3 = "#006633"
        g4 = "#003322"  # dark green

        shortcut_layout.addWidget(
            create_shortcut("Add Inventory", os.path.join(ASSETS, "icons", "inventory.png"),
                            lambda: self._navigate_to("inventory"), background_color=g1), 0, 0)

        shortcut_layout.addWidget(
            create_shortcut("Log Trip", os.path.join(ASSETS, "icons", "mileage.png"),
                            lambda: self._navigate_to("mileage"), background_color=g2), 0, 1)

        shortcut_layout.addWidget(
            create_shortcut("Order Parts", os.path.join(ASSETS, "icons", "parts.png"),
                            lambda: self._navigate_to("parts"), background_color=g3), 0, 2)

        shortcut_layout.addWidget(
            create_shortcut("Log Service", os.path.join(ASSETS, "icons", "service.png"),
                            lambda: self._navigate_to("service_activity"), background_color=g4), 0, 3)

        main_layout.addWidget(shortcut_frame)

        # Recent activity: shows the 5 most recent 5 service entries (clickable).
        recent_frame = QFrame()
        recent_frame.setStyleSheet("background-color: #1f1f1f; border-radius: 12px;")
        recent_layout = QVBoxLayout(recent_frame)
        self.recent_layout = recent_layout
        recent_layout.setContentsMargins(10, 10, 10, 10)
        recent_layout.setSpacing(8)

        title_lbl = QLabel("Recent Service Activity")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_lbl.setStyleSheet("color: #ffffff;")
        recent_layout.addWidget(title_lbl)

        # Pull the 5 most recent records for the logged-in user
        service_items = ServiceActivity.get_all_for_user(user)[:5]

        if not service_items:
            # Show a message if there are no logs.
            lbl = QLabel("No recent service activity.")
            font = QFont("Segoe UI", 12)
            font.setItalic(True)
            lbl.setFont(font)
            lbl.setStyleSheet("color: #bbbbbb;")
            recent_layout.addWidget(lbl)

        else:
            # Create a “card” for each recent service record
            for sa in service_items:
                item = self._create_service_item(sa)
                recent_layout.addWidget(item)

        # Make service log list expand as the window grows
        main_layout.addWidget(recent_frame, 1)

    # Nav helper: allows dashboard buttons (shortcuts) to jump to other pages.
    def _navigate_to(self, page_name):
        if hasattr(self.controller, "show_page"):
            self.controller.show_page(page_name)

            # Delay slightly to allow target page to load,
            # then open the “Add New” form automatically if it has one.
            QTimer.singleShot(
                150,
                lambda: getattr(self.controller, "current_page", None)
                and getattr(self.controller.current_page, "open_add_form", lambda: None)()
            )

    # Recent Service Item UI Builder: Creates one of the “recent service activity” cards (clickable).
    def _create_service_item(self, sa):
        frame = QFrame()
        frame.setStyleSheet("background-color: #2f2f2f; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)

        def truncate(text, length=60):
            return (text[:length] + "...") if text and len(text) > length else (text or "")

        info_text = (
            f"<b>Area:</b> {sa.area or 'N/A'} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Customer:</b> {sa.customer or 'N/A'} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Serial:</b> {sa.serial_number or 'N/A'}<br>"
            f"<b>Malfunction:</b> {truncate(sa.malfunction)}<br>"
            f"<b>Action:</b> {truncate(sa.remedial_action)}<br>"
            f"<b>Comments:</b> {truncate(sa.comments)}"
        )

        lbl = QLabel(info_text)
        lbl.setTextFormat(Qt.RichText)  # enable bold tags
        lbl.setStyleSheet("color: #cccccc; font-size: 13px;")
        lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl.setWordWrap(True)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(lbl)

        # Hover effects
        def enterEvent(_): frame.setStyleSheet("background-color: #3a3a3a; border-radius: 10px;")
        def leaveEvent(_): frame.setStyleSheet("background-color: #2f2f2f; border-radius: 10px;")
        frame.enterEvent = enterEvent
        frame.leaveEvent = leaveEvent

        # Clicking takes user to service activity page
        frame.mousePressEvent = lambda e: self.controller.show_page("service_activity")
        return frame

    # Toner widget refresh handler: called whenever inventory data changes anywhere in the app.
    def refresh_toner_widget(self):
        if not hasattr(self, "toner_widget"):
            return
        layout = self.layout()

        # Remove old toner widget
        old_index = layout.indexOf(self.toner_widget)
        if self.toner_widget is not None:
            layout.removeWidget(self.toner_widget)
            self.toner_widget.setParent(None)
            self.toner_widget.deleteLater()

        # Re-create toner widget
        from ui.components.widgets import TonerLevelsWidget
        self.toner_widget = TonerLevelsWidget(self)

        # Insert it back at the same position > ensures it stays ABOVE recent activity
        insert_index = 2
        layout.insertWidget(insert_index, self.toner_widget)

    # Service activity refresh widget handler
    def refresh_recent_activity(self):
        user = get_current_user() or "default_user"

        # Clear the recent layout
        recent_layout = self.recent_layout  # Save this in __init__!
        for i in reversed(range(recent_layout.count())):
            widget = recent_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
            recent_layout.removeItem(recent_layout.itemAt(i))

        # Reload service items
        service_items = ServiceActivity.get_all_for_user(user)[:5]

        if not service_items:
            lbl = QLabel("No recent service activity.")
            lbl.setStyleSheet("color: #bbbbbb; font-style: italic;")
            recent_layout.addWidget(lbl)
        else:
            for sa in service_items:
                recent_layout.addWidget(self._create_service_item(sa))
