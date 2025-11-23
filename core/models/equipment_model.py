import os
from PySide6.QtCore import QObject, Signal
from core.utils import safe_str

"""
This module defines the SQLite-backed data model for storing equipment, location, and contact 
information associated with each user. It provides the EquipmentInfo class, which normalizes 
all incoming field values and offers CRUD operations for inserting, retrieving, updating, and 
deleting equipment records. The module also initializes the underlying equipment_info table if 
missing, emits Qt signals so the UI can update when equipment data changes, and ensures each 
record is scoped to the correct user for multi-tenant safety within the application.

core.models.equipment_model.py index:

def get_connection(): Opens a connection to the application's SQLite database
class ModelSignals(): Centralized Qt signals emitted whenever a model changes
class EquipmentInfo: Model for storing equipment and location details
 - def __init__(): Initializes EquipmentInfo class
 - def create(): Stores equipment, contact, and location details for a user
 - def get_all_for_user(): Fetches all equipment info rows for a user
    - class RowObj: Allows attribute-style access
        - def __init__(): Initializes RowObj class
 - def update(): Updates an equipment info row identified by id
 - def delete(): Deletes an equipment info entry matching both the id and the user
 - def init_table(): Creates the equipment_info table if missing
"""

# Full path to the main SQLite database file.
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

class EquipmentInfo:
    # Model for storing equipment and location details.
    def __init__(
        self,
        id=None,
        area=None,
        customer=None,
        building=None,
        room=None,
        serial_number=None,
        model=None,
        poc=None,
        poc_phone=None,
        it_support=None,
        it_phone=None,
        notes=None,
        user=None,
    ):
        # All string-like fields go through safe_str to avoid None/invalid values.
        self.id = id
        self.area = safe_str(area)
        self.customer = safe_str(customer)
        self.building = safe_str(building)
        self.room = safe_str(room)
        self.serial_number = safe_str(serial_number)
        self.model = safe_str(model)
        self.poc = safe_str(poc)                # Point of contact (person responsible).
        self.poc_phone = safe_str(poc_phone)
        self.it_support = safe_str(it_support)  # IT contact or vendor name.
        self.it_phone = safe_str(it_phone)
        self.notes = safe_str(notes)
        self.user = safe_str(user or "default_user")

    @staticmethod
    def create(**kwargs):
    # Stores equipment, contact, and location details for a user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO equipment_info (
                area, customer, building, room, serial_number, model,
                poc, poc_phone, it_support, it_phone, notes, user
            ) VALUES (
                :area, :customer, :building, :room, :serial_number, :model,
                :poc, :poc_phone, :it_support, :it_phone, :notes, :user
            )
        """, kwargs)
        # ^ Named parameter style (:area etc.) is used here instead of ? placeholders.
        #   Caller must pass a dict with keys matching these names exactly.
        conn.commit()
        conn.close()
        model_signals.equipment_changed.emit()

    @staticmethod
    def get_all_for_user(user):
    # Fetches all equipment info rows for a user and returns them as dot-accessible objects.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, area, customer, building, room, serial_number, model,
                   poc, poc_phone, it_support, it_phone, notes,
                   user
            FROM equipment_info
            WHERE user = ?
            ORDER BY id
        """, (user,))
        rows = cur.fetchall()
        conn.close()

        class RowObj:
            def __init__(self, **entries):
                self.__dict__.update(entries)
                # ^ Allows attribute-style access: row_obj.area, row_obj.customer, etc.

        columns = [
            "id", "area", "customer", "building", "room", "serial_number", "model",
            "poc", "poc_phone", "it_support", "it_phone", "notes", "user"
        ]

        return [RowObj(**dict(zip(columns, r))) for r in rows]
        # ^ Convert each row tuple into a mapping, then into a simple object, which is convenient
        #   for templates or UI code (dot-notation instead of index-based access).

    @staticmethod
    def update(item_id, **kw):
    # Updates an equipment info row identified by id.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE equipment_info
            SET area=?, customer=?, building=?, room=?, serial_number=?, model=?,
                poc=?, poc_phone=?, it_support=?, it_phone=?, notes=?, user=?
            WHERE id=?
        """, (
            safe_str(kw.get("area")),
            safe_str(kw.get("customer")),
            safe_str(kw.get("building")),
            safe_str(kw.get("room")),
            safe_str(kw.get("serial_number")),
            safe_str(kw.get("model")),
            safe_str(kw.get("poc")),
            safe_str(kw.get("poc_phone")),
            safe_str(kw.get("it_support")),
            safe_str(kw.get("it_phone")),
            safe_str(kw.get("notes")),
            safe_str(kw.get("user")),
            item_id,
        ))
        conn.commit()
        conn.close()
        model_signals.equipment_changed.emit()

    @staticmethod
    def delete(item_id, user):
    # Deletes an equipment info entry matching both the id and the user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM equipment_info WHERE id=? AND user=?", (item_id, user))
        conn.commit()
        conn.close()
        model_signals.equipment_changed.emit()

    @staticmethod
    def init_table():
    # Creates the equipment_info table if missing.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS equipment_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT,
                customer TEXT,
                building TEXT,
                room TEXT,
                serial_number TEXT,
                model TEXT,
                poc TEXT,
                poc_phone TEXT,
                it_support TEXT,
                it_phone TEXT,
                notes TEXT,
                user TEXT NOT NULL
            )
        """)
        # ^ The schema here matches the fields used by EquipmentInfo.create/update/get_all_for_user.
        conn.commit()
        conn.close()