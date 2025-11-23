import os
from PySide6.QtCore import QObject, Signal
from core.utils import safe_str, safe_int, parse_date
from datetime import date

"""
This module implements the data model and SQLite persistence layer for the application's 
inventory system. It defines the `InventoryItem` class for representing individual inventory 
records, provides schema-migration helpers that safely add missing columns, and exposes CRUD 
operations for creating, retrieving, updating, and deleting inventory items. The model ensures 
all field values are normalized before being written to the database, tracks user-scoped inventory, 
and emits Qt signals so the UI updates automatically whenever inventory data changes.

core.models.inventory_model.py index: 
def get_connection(): Opens a connection to the application's SQLite database
def migrate_inventory_schema(): Add missing columns to inventory_items without destroying data.
class ModelSignals(): Centralized Qt signals emitted whenever a model changes.
class InventoryItem: Defines the InventoryItem
 - def __init__(): Initializes the InventoryItem class
 - def days_since_verification(): Returns the number of days since the stored verification date
 - def create(): Creates a new inventory row after normalizing all fields.
 - def get_all_for_user(): Returns all inventory items for a user
 - def update(): Updates an item by id
 - def delete_by_part_number(): Deletes one inventory item tied to a specific user and part number
 - def add_quantity(): Increases inventory for a given part and user
 - def init_table(): Creates the inventory_items table if missing and adds any required columns
"""

# Full path to the main SQLite database file.
DB_PATH = os.path.join("data", "database.db")

def get_connection():
    # Opens a connection to the application's SQLite database; all models use this helper.
    import sqlite3
    return sqlite3.connect(DB_PATH)

def migrate_inventory_schema():
    # Add missing columns to inventory_items without destroying data.
    conn = get_connection()
    cur = conn.cursor()

    # PRAGMA table_info returns a list of columns for the specified table.
    cur.execute("PRAGMA table_info(inventory_items)")
    cols = {row[1] for row in cur.fetchall()}  # row[1] is the column name
    # ^ Using a set comprehension makes lookups O(1) for "in" checks.

    # Add 'notes' if missing
    if "notes" not in cols:
        cur.execute("ALTER TABLE inventory_items ADD COLUMN notes TEXT")
        # ^ ALTER TABLE in SQLite can add new columns at the end of the table
        #   without touching existing rows; new column values default to NULL.
        conn.commit()
        print("[DB] Added 'notes' column to inventory_items")
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

# Inventory Item Model
class InventoryItem:
    def __init__(
        self, id=None, part_number=None, quantity=0, part_location=None, model=None,
        part_description=None, quarterly_inventory_verification_date=None,
        category_id=None, notes=None, user=None
    ):
        # Represents a single inventory record with normalized values for string and numeric fields.
        self.id = id
        self.part_number = safe_str(part_number)
        self.quantity = safe_int(quantity)
        self.part_location = safe_str(part_location)
        self.model = safe_str(model)
        self.part_description = safe_str(part_description)
        self.quarterly_inventory_verification_date = safe_str(quarterly_inventory_verification_date)
        self.category_id = category_id
        self.notes = safe_str(notes)
        self.user = safe_str(user)

    @property
    def days_since_verification(self):
        # Returns the number of days since the stored verification date, or None if invalid.
        conn = get_connection()
        cur = conn.cursor()
        d = parse_date(self.quarterly_inventory_verification_date)
        if not d:
            return None
        return (date.today() - d.date()).days

    @staticmethod
    def create(**kw):
        # Creates a new inventory row after normalizing all fields.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO inventory_items (
                part_number,
                quantity,
                part_location,
                model,
                part_description,
                quarterly_inventory_verification_date,
                category_id,
                notes,
                user
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            safe_str(kw.get("part_number")),
            safe_int(kw.get("quantity")),
            safe_str(kw.get("part_location")),
            safe_str(kw.get("model")),
            safe_str(kw.get("part_description")),
            safe_str(kw.get("quarterly_inventory_verification_date")),
            safe_str(kw.get("category_id")),
            safe_str(kw.get("notes")),
            safe_str(kw.get("user", "default_user")),
        ))

        conn.commit()
        conn.close()
        model_signals.inventory_changed.emit()

    @staticmethod
    def get_all_for_user(user="default_user"):
        # Returns all inventory items for a user, automatically migrating schema if needed.
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, part_number, quantity, part_location, model, part_description,
                       quarterly_inventory_verification_date, category_id, notes, user
                FROM inventory_items
                WHERE user=?
                ORDER BY id
            """, (user,))
            rows = cur.fetchall()
            return [InventoryItem(*row) for row in rows]

        except Exception as e:
            # If the error mentions missing 'notes' column, attempt migration
            if "no such column: notes" in str(e).lower():
                print("[DB] Detected missing 'notes' column — applying migration...")
                conn.close()

                try:
                    migrate_inventory_schema()
                    # ^ Calls the migration defined above to add the 'notes' column safely.
                except Exception as e2:
                    print(f"[DB] Migration failed: {e2}")

                # Retry the query after migrating
                return InventoryItem.get_all_for_user(user)
            else:
                raise

        finally:
            conn.close()

    @staticmethod
    def update(item_id, **kw):
        # Updates an item by id, ensuring fields are sanitized before being written.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE inventory_items
            SET part_number=?, quantity=?, part_location=?, model=?, part_description=?,
                quarterly_inventory_verification_date=?, category_id=?, notes=?, user=?
            WHERE id=?
        """, (
            safe_str(kw.get("part_number")),
            safe_int(kw.get("quantity")),
            safe_str(kw.get("part_location")),
            safe_str(kw.get("model")),
            safe_str(kw.get("part_description")),
            safe_str(kw.get("quarterly_inventory_verification_date")),
            kw.get("category_id"),
            safe_str(kw.get("notes")),
            safe_str(kw.get("user")),
            item_id,
        ))
        conn.commit()
        conn.close()
        model_signals.inventory_changed.emit()

    @staticmethod
    def delete_by_part_number(part_number, user):
        # Deletes one inventory item tied to a specific user and part number.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM inventory_items WHERE part_number=? AND user=?",
            (part_number, user),
        )
        conn.commit()
        conn.close()
        model_signals.inventory_changed.emit()

    @staticmethod
    def add_quantity(part_number, quantity, user="default_user"):
        # Increases inventory for a given part and user.
        if not part_number or quantity <= 0:
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE inventory_items
            SET quantity = quantity + ?
            WHERE part_number=? AND user=?
        """, (quantity, part_number, user))

        conn.commit()
        conn.close()
        model_signals.inventory_changed.emit()

    @staticmethod
    def init_table():
        # Creates the inventory_items table if missing and adds any required columns.
        import sqlite3

        conn = get_connection()
        cur = conn.cursor()

        # Base table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_number TEXT,
                quantity INTEGER,
                part_location TEXT,
                model TEXT,
                part_description TEXT,
                quarterly_inventory_verification_date TEXT,
                category_id TEXT,
                user TEXT NOT NULL
            )
        """)
        # ^ Uses TEXT for category_id (more flexible than strict INTEGER FK).

        # Migration logic
        cur.execute("PRAGMA table_info(inventory_items)")
        columns = [row[1] for row in cur.fetchall()]

        expected_columns = [
            ("category_id", "TEXT"),
            ("notes", "TEXT")
        ]
        # ^ List of schema requirements; future columns can be added here as tuples.

        for col_name, col_type in expected_columns:
            if col_name not in columns:
                print(f"[DB] Adding missing column '{col_name}' to inventory_items...")
                try:
                    cur.execute(f"ALTER TABLE inventory_items ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    # ^ Silently logs if the column already exists or other ALTER issues arise.
                    print(f"[DB] Warning: could not add '{col_name}' column:", e)

        conn.commit()
        conn.close()