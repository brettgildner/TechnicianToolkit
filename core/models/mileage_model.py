import os
from PySide6.QtCore import QObject, Signal

"""
This module provides the data-layer implementation for the application's mileage-tracking system. 
It defines the MileageEntry model, initializes the underlying SQLite table, and implements all CRUD 
operations needed to create, update, retrieve, and delete mileage logs for individual users. By 
emitting a centralized Qt signal whenever mileage data changes, it ensures the rest of the 
application—especially the UI—can stay synchronized with the database. Overall, this page acts as 
the dedicated backend for storing and managing user-specific mileage records.

core.models.mileage_model.py index:
def get_connection(): Opens a connection to the application's SQLite database
class ModelSignals(): Centralized Qt signals emitted whenever a model changes
class MileageEntry: Represents a single mileage log entry stored in the mileage table
 - def __init__(): Initializes MileageEntry class
 - def init_table(): Creates the mileage table with fields for user, mileage values, and locations
 - def create(): Inserts a new mileage log for the given user
 - def update(): Updates a mileage row using both id and user to prevent cross-account edits
 - def delete(): Deletes a mileage entry tied to a specific user
 - def get_all_for_user(): Fetches all mileage entries for a user, sorted by newest date first
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

# Mileage model
class MileageEntry:
    def __init__(
            self,
            id,
            user,
            date,
            start_miles,
            end_miles,
            start_location,
            end_location,
            purpose,
    ):
        # Represents a single mileage log entry stored in the mileage table.
        self.id = id
        self.user = user
        self.date = date
        self.start_miles = start_miles
        self.end_miles = end_miles
        self.start_location = start_location
        self.end_location = end_location
        self.purpose = purpose

    # ------------------------------------------------------------
    @staticmethod
    def init_table():
        # Creates the mileage table with fields for user, mileage values, and locations.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS mileage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                date TEXT,
                start_miles REAL,
                end_miles REAL,
                start_location TEXT,
                end_location TEXT,
                purpose TEXT
            )
        """)

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    @staticmethod
    def create(date, start_miles, end_miles, start_location, end_location, purpose, user):
        # Inserts a new mileage log for the given user.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO mileage (user, date, start_miles, end_miles, start_location, end_location, purpose)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user, date, start_miles, end_miles, start_location, end_location, purpose))

        conn.commit()
        conn.close()
        model_signals.mileage_changed.emit()

    # ------------------------------------------------------------
    @staticmethod
    def update(id, user, date, start_miles, end_miles, start_location, end_location, purpose):
        # Updates a mileage row using both id and user to prevent cross-account edits.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE mileage
            SET date=?, start_miles=?, end_miles=?, start_location=?, end_location=?, purpose=?
            WHERE id=? AND user=?
        """, (date, start_miles, end_miles, start_location, end_location, purpose, id, user))
        # ^ WHERE clause enforces multi-tenant safety at the DB level.

        conn.commit()
        conn.close()
        model_signals.mileage_changed.emit()

    # ------------------------------------------------------------
    @staticmethod
    def delete(id, user):
        # Deletes a mileage entry tied to a specific user.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM mileage WHERE id=? AND user=?", (id, user))

        conn.commit()
        conn.close()
        model_signals.mileage_changed.emit()

    # ------------------------------------------------------------
    @staticmethod
    def get_all_for_user(user):
        # Fetches all mileage entries for a user, sorted by newest date first.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, user, date, start_miles, end_miles, start_location, end_location, purpose
            FROM mileage
            WHERE user=?
            ORDER BY date DESC
        """, (user,))

        rows = cur.fetchall()
        conn.close()

        # Convert each row into a MileageEntry instance
        return [
            MileageEntry(
                id=row[0],
                user=row[1],
                date=row[2],
                start_miles=row[3],
                end_miles=row[4],
                start_location=row[5],
                end_location=row[6],
                purpose=row[7],
            )
            for row in rows
        ]