import os
from PySide6.QtCore import QObject, Signal

"""
This module defines the simple SQLite-backed Category model used to group or classify inventory 
items and other records within the application. It provides basic CRUD-style functionality for 
retrieving all category rows and creating new ones, converting raw database tuples into Python 
objects for cleaner UI consumption. The module also includes shared model signals used throughout 
the app, and relies on a centralized database connection helper to interact with the categories 
table.

core.models.category_model.py index:

def get_connection(): Opens a connection to the application's SQLite database
class ModelSignals(): Centralized Qt signals emitted whenever a model changes
class Category: Represents a simple category row with id and name fields
 - def __init__(): 
 - def get_all(): Represents a simple category row with id and name fields
 - def create(): Creates a new category record using the supplied name
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

# Category model
class Category:
    def __init__(self, id=None, name=""):
        # Represents a simple category row with id and name fields.
        self.id = id
        self.name = name

    @staticmethod
    def get_all():
        # Represents a simple category row with id and name fields.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        rows = cur.fetchall()               # Returns a list of (id, name) tuples.
        conn.close()

        # Convert each (id, name) tuple into a Category object
        return [Category(id=row[0], name=row[1]) for row in rows]

    @staticmethod
    def create(name):
        # Creates a new category record using the supplied name.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        # ^ name is passed directly; if it can be None or unsafe, caller should sanitize first.
        conn.commit()
        conn.close()