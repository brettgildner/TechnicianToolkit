import os
from PySide6.QtCore import QObject, Signal
from core.utils import safe_str, safe_int

"""
This module defines and manages the data layer for user-specific parts orders within the application. 
It provides the SQLite connection helper, ensures the parts_orders table stays up to date through a 
simple schema-migration routine, and implements all CRUD operations for creating, retrieving, updating, 
and deleting parts orders. Text and quantity fields are normalized through shared utility functions, 
helping maintain clean, predictable data. The module also emits Qt signals whenever parts-related 
records change so the rest of the application can update accordingly. Altogether, it serves as the 
backend component responsible for persisting and maintaining the integrity of parts-ordering data.

core.models.parts_model.py index:
def get_connection(): Opens a connection to the application's SQLite database
def migrate_parts_schema(): Ensure the parts_orders table has the required columns
class ModelSignals(): Centralized Qt signals emitted whenever a model changes
class PartsOrder: Represents one parts order, normalizing text and quantity fields
 - def __init__(): Initializes PartsOrder class
 - def create(): Inserts a new parts order for a user
 - def get_all_for_user(): Fetches all parts orders belonging to a specific user
 - def update(): Updates an existing order using the provided values
 - def delete(): Deletes a parts order by ID
 - def delete_by_part_number(): Deletes a parts order only if it matches both part number and user
 - def init_table(): Creates the parts_orders table if it does not already exist
"""

# Full path to the main SQLite database file inside the project's data folder.
DB_PATH = os.path.join("data", "database.db")

def get_connection():
    # Opens a connection to the application's SQLite database; all models use this helper.
    import sqlite3
    return sqlite3.connect(DB_PATH)

def migrate_parts_schema():
    # Ensure the parts_orders table has the required columns.
    conn = get_connection()
    cur = conn.cursor()

    # Get current column names from parts_orders.
    cur.execute("PRAGMA table_info(parts_orders)")
    columns = [row[1] for row in cur.fetchall()]
    # ^ Extracting [1] yields only column names; ordering matches table definition.

    # Add 'category' column if it doesn't exist.
    if "category" not in columns:
        print("[DB] Detected missing 'category' column in parts_orders — migrating...")
        try:
            cur.execute("ALTER TABLE parts_orders ADD COLUMN category TEXT")
            # ^ Same as inventory migration: column is appended; existing rows get NULL.
            print("[DB] Added 'category' column to parts_orders")
        except Exception as e:
            # ^ Broad except is used here to prevent breaking app startup if migration fails.
            print("[DB] Migration failed:", e)
    conn.commit()
    conn.close()

# Centralized Qt signals emitted whenever a model changes.
class ModelSignals(QObject):
    service_activity_changed = Signal()
    inventory_changed = Signal()
    mileage_changed = Signal()
    parts_changed = Signal()
    equipment_changed = Signal()
    expense_changed = Signal()

model_signals = ModelSignals()

# Parts Orders
class PartsOrder:
    def __init__(self, id, quantity, part_number, model, description, user):
        # Represents one parts order, normalizing text and quantity fields.
        self.id = id
        self.quantity = safe_int(quantity)
        self.part_number = safe_str(part_number)
        self.model = safe_str(model)
        self.description = safe_str(description)
        self.user = safe_str(user)

    @staticmethod
    def create(quantity, part_number, model, description, user):
        # Inserts a new parts order for a user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO parts_orders (quantity, part_number, model, description, user)
            VALUES (?, ?, ?, ?, ?)
        """, (
            safe_int(quantity),
            part_number,
            model,
            description,
            user,
        ))
        # ^ quantity is normalized, but other fields are passed as given; caller should avoid None
        #   or sanitize using safe_str if needed.
        conn.commit()
        conn.close()
        model_signals.parts_changed.emit()

    @staticmethod
    def get_all_for_user(user):
        # Fetches all parts orders belonging to a specific user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, quantity, part_number, model, description, user
            FROM parts_orders
            WHERE user=?
        """, (user,))
        rows = cur.fetchall()
        conn.close()
        return [PartsOrder(*row) for row in rows]

    @staticmethod
    def update(id, quantity, part_number, model, description):
        # Updates an existing order using the provided values.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE parts_orders
            SET quantity=?, part_number=?, model=?, description=?
            WHERE id=?
        """, (
            safe_int(quantity),
            part_number,
            model,
            description,
            id,
        ))
        conn.commit()
        conn.close()
        model_signals.parts_changed.emit()

    @staticmethod
    def delete(id):
        # Deletes a parts order by ID.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM parts_orders WHERE id=?", (id,))
        conn.commit()
        conn.close()
        model_signals.parts_changed.emit()

    @staticmethod
    def delete_by_part_number(part_number, user):
        # Deletes a parts order only if it matches both part number and user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM parts_orders WHERE part_number=? AND user=?",
            (part_number, user)
        )
        conn.commit()
        conn.close()
        model_signals.parts_changed.emit()

    @staticmethod
    def init_table():
        # Creates the parts_orders table if it does not already exist.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS parts_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quantity INTEGER,
                part_number TEXT,
                model TEXT,
                description TEXT,
                user TEXT NOT NULL
            )
        """)
        # ^ The NOT NULL on user enforces that every row is associated with a user.
        conn.commit()
        conn.close()