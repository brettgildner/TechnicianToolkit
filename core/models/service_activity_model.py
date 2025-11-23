import os
from PySide6.QtCore import QObject, Signal
from core.utils import safe_str, safe_int

"""
This module provides the data model, schema management, and change-notification 
system for service activity records within the application. It defines helpers 
for migrating database schemas, exposes Qt signals that notify the UI when model 
data changes, and implements the ServiceActivity class that handles creating, 
retrieving, updating, and deleting service call entries, including automatic 
inventory adjustments when parts are used. All operations interact directly with 
the SQLite database, acting as the persistence layer for service activity and 
related inventory updates.

core.models.service_activity_model.py index:
 - def get_connection(): Opens a connection to the application's SQLite database
class ModelSignals(): Centralized Qt signals emitted whenever a model changes
class ServiceActivity: Defines a single service call.
 - def __init__(): Initialize activity fields.
 - def init_table(): Create table if missing.
 - def _from_row(): Convert DB row to object.
 - def get_all(): Get all activities.
 - def get_all_for_user(): Gat all of 'user's' activities.
 - def get_by_id(): Get activity by ID.
 - def create(): Insert new activity and adjust inventory.
 - def update(): Update record and adjust inventory.
 - def delete(): Delete record and signal change.
"""

# Full path to the main SQLite database file inside the project's data folder.
DB_PATH = os.path.join("data", "database.db")

def get_connection():
    # Opens a connection to the application's SQLite database; all models use this helper.
    import sqlite3
    return sqlite3.connect(DB_PATH)

# Centralized Qt signals emitted whenever a model changes.
class ModelSignals(QObject):
    service_activity_changed = Signal()
    inventory_changed = Signal()
    mileage_changed = Signal()
    parts_changed = Signal()
    equipment_changed = Signal()
    expense_changed = Signal()

model_signals = ModelSignals()

# Service Activity
class ServiceActivity:
    def __init__(
        self, id=None, area=None, customer=None, serial_number=None, meter=None,
        malfunction=None, arrival_date=None, arrival_time=None, remedial_action=None,
        quantity=None, part_replaced=None, departure_date=None, departure_time=None,
        call_duration=None, technician=None, comments=None, user=None,
    ):
        self.id = id
        self.area = safe_str(area)
        self.customer = safe_str(customer)
        self.serial_number = safe_str(serial_number)
        self.meter = safe_str(meter)
        self.malfunction = safe_str(malfunction)
        self.arrival_date = safe_str(arrival_date)
        self.arrival_time = safe_str(arrival_time)
        self.remedial_action = safe_str(remedial_action)
        self.quantity = safe_int(quantity)
        self.part_replaced = safe_str(part_replaced)
        self.departure_date = safe_str(departure_date)
        self.departure_time = safe_str(departure_time)
        self.call_duration = safe_str(call_duration)
        self.technician = safe_str(technician)
        self.comments = safe_str(comments)
        self.user = safe_str(user or "default_user")

    @staticmethod
    def init_table():
        # Creates the service_activity table if missing.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT,
                customer TEXT,
                serial_number TEXT,
                meter TEXT,
                malfunction TEXT,
                arrival_date TEXT,
                arrival_time TEXT,
                remedial_action TEXT,
                quantity INTEGER,
                part_replaced TEXT,
                departure_date TEXT,
                departure_time TEXT,
                call_duration TEXT,
                technician TEXT,
                comments TEXT,
                user TEXT
            )
        """)

        conn.commit()
        conn.close()

    # Converts a SQL row tuple into a ServiceActivity object.
    @staticmethod
    def _from_row(row):
        if not row:
            return None

        return ServiceActivity(
            id=row[0],
            area=row[1],
            customer=row[2],
            serial_number=row[3],
            meter=row[4],
            malfunction=row[5],
            arrival_date=row[6],
            arrival_time=row[7],
            remedial_action=row[8],
            quantity=row[9],
            part_replaced=row[10],
            departure_date=row[11],
            departure_time=row[12],
            call_duration=row[13],
            technician=row[14],
            comments=row[15],
            user=row[16],
        )

    # Fetches all service activity records, sorted by most recent arrival datetime.
    @staticmethod
    def get_all():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM service_activity
            ORDER BY
                datetime(arrival_date || 'T' || arrival_time) DESC
        """)
        rows = cur.fetchall()
        conn.close()

        return [ServiceActivity._from_row(r) for r in rows]

    # Fetches all service activity rows for a given user.
    @staticmethod
    def get_all_for_user(user):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM service_activity
            WHERE user=?
            ORDER BY
                datetime(arrival_date || 'T' || arrival_time) DESC
        """, (user,))
        rows = cur.fetchall()
        conn.close()

        return [ServiceActivity._from_row(r) for r in rows]

    # Returns a single service activity by id, or None if not found.
    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM service_activity WHERE id=?", (id,))
        row = cur.fetchone()
        conn.close()

        return ServiceActivity._from_row(row)

    # Creates a new service call entry and updates inventory if parts were used.
    @staticmethod
    def create(**data):
        # Insert a new service call and decrement inventory if needed.
        conn = get_connection()
        cur = conn.cursor()

        area           = safe_str(data.get("area"))
        customer       = safe_str(data.get("customer"))
        serial_number  = safe_str(data.get("serial_number"))
        meter          = safe_str(data.get("meter"))
        malfunction    = safe_str(data.get("malfunction"))
        arrival_date   = safe_str(data.get("arrival_date"))
        arrival_time   = safe_str(data.get("arrival_time"))
        remedial_action = safe_str(data.get("remedial_action"))
        quantity       = safe_int(data.get("quantity"))
        part_replaced  = safe_str(data.get("part_replaced"))
        departure_date = safe_str(data.get("departure_date"))
        departure_time = safe_str(data.get("departure_time"))
        call_duration  = safe_str(data.get("call_duration"))
        technician     = safe_str(data.get("technician"))
        comments       = safe_str(data.get("comments"))
        user           = safe_str(data.get("user") or "default_user")

        # INSERT ROW
        cur.execute("""
            INSERT INTO service_activity (
                area, customer, serial_number, meter, malfunction,
                arrival_date, arrival_time, remedial_action, quantity,
                part_replaced, departure_date, departure_time, call_duration,
                technician, comments, user
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            area, customer, serial_number, meter, malfunction,
            arrival_date, arrival_time, remedial_action, quantity,
            part_replaced, departure_date, departure_time, call_duration,
            technician, comments, user,
        ))

        # HANDLE INVENTORY
        try:
            if part_replaced:
                use_qty = quantity if quantity and quantity > 0 else 1

                cur.execute(
                    "SELECT quantity FROM inventory_items WHERE part_number=? AND user=?",
                    (part_replaced, user),
                )
                row = cur.fetchone()

                if row:
                    current_qty = row[0] or 0
                    new_qty = max(0, current_qty - use_qty)

                    cur.execute(
                        "UPDATE inventory_items SET quantity=? WHERE part_number=? AND user=?",
                        (new_qty, part_replaced, user),
                    )
        except Exception as e:
            print("[ServiceActivity.create] Inventory error:", e)

        conn.commit()
        conn.close()
        model_signals.service_activity_changed.emit()

    #  Updates the service call and adjusts inventory based on part/quantity changes.
    def update(self):
        #print("REAL MODEL UPDATE CALLED", self.id)

        conn = get_connection()
        cur = conn.cursor()

        # Load old row for inventory adjustment
        cur.execute("SELECT part_replaced, quantity, user FROM service_activity WHERE id=?", (self.id,))
        old_row = cur.fetchone()

        if not old_row:
            print("[SA.update] ERROR: Tried to update non-existent ID", self.id)
            conn.close()
            return

        old_part = safe_str(old_row[0])
        old_qty = safe_int(old_row[1])
        old_user = safe_str(old_row[2] or "default_user")

        new_part = safe_str(getattr(self, "part_replaced", ""))
        new_qty = safe_int(getattr(self, "quantity", 0))
        user = safe_str(getattr(self, "user", old_user))

        # 1. Update service_activity row itself
        cur.execute("""
            UPDATE service_activity SET
                area=?, customer=?, serial_number=?, meter=?, malfunction=?,
                arrival_date=?, arrival_time=?, remedial_action=?, quantity=?,
                part_replaced=?, departure_date=?, departure_time=?, call_duration=?,
                technician=?, comments=?, user=?
            WHERE id=?
        """, (
            safe_str(self.area),
            safe_str(self.customer),
            safe_str(self.serial_number),
            safe_str(self.meter),
            safe_str(self.malfunction),
            safe_str(self.arrival_date),
            safe_str(self.arrival_time),
            safe_str(self.remedial_action),
            new_qty,
            new_part,
            safe_str(self.departure_date),
            safe_str(self.departure_time),
            safe_str(self.call_duration),
            safe_str(self.technician),
            safe_str(self.comments),
            user,
            self.id,
        ))

        # 2. Inventory adjustments (inventory_items table)
        try:
            # PART CHANGED
            if old_part and old_part != new_part:
                # Return old qty
                cur.execute("""
                    UPDATE inventory_items
                    SET quantity = quantity + ?
                    WHERE part_number=? AND user=?
                """, (old_qty, old_part, user))

                # Subtract new qty
                if new_part:
                    cur.execute("""
                        UPDATE inventory_items
                        SET quantity = MAX(quantity - ?, 0)
                        WHERE part_number=? AND user=?
                    """, (new_qty, new_part, user))

            # SAME PART, quantity changed
            elif old_part == new_part and new_part:
                diff = new_qty - old_qty
                if diff > 0:
                    cur.execute("""
                        UPDATE inventory_items
                        SET quantity = MAX(quantity - ?, 0)
                        WHERE part_number=? AND user=?
                    """, (diff, new_part, user))
                elif diff < 0:
                    cur.execute("""
                        UPDATE inventory_items
                        SET quantity = quantity + ?
                        WHERE part_number=? AND user=?
                    """, (-diff, new_part, user))

            # PART REMOVED
            elif old_part and not new_part:
                cur.execute("""
                    UPDATE inventory_items
                    SET quantity = quantity + ?
                    WHERE part_number=? AND user=?
                """, (old_qty, old_part, user))

            # PART ADDED
            elif not old_part and new_part:
                cur.execute("""
                    UPDATE inventory_items
                    SET quantity = MAX(quantity - ?, 0)
                    WHERE part_number=? AND user=?
                """, (new_qty, new_part, user))

        except Exception as e:
            print("[SA.update] ERROR adjusting inventory:", e)

        conn.commit()
        conn.close()
        model_signals.service_activity_changed.emit()

    #  Deletes a service activity entry by its primary key.
    def delete(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM service_activity WHERE id=?", (self.id,))
        conn.commit()
        conn.close()
        model_signals.service_activity_changed.emit()