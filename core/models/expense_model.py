import os
from PySide6.QtCore import QObject, Signal
from datetime import date, datetime

"""
This module centralizes all database-related logic and model definitions for the application’s 
expense and mileage reporting features. It provides the SQLite connection helper, initializes 
the required tables, and defines the data structures and CRUD operations for expense reports, 
individual expense entries, and mileage headers. It also exposes Qt signals that notify the rest 
of the application whenever model data changes, ensuring the UI can react in real time. Overall, 
this page acts as the core data layer that manages persistent storage and structured access to 
user-specific financial recordkeeping.

core.models.expense_model.py index:
def get_connection(): Opens a connection to the application's SQLite database
class ModelSignals():Centralized Qt signals emitted whenever a model changes
class ExpenseReportInfo: Stores a user's report-level expense metadata; only one row exists per user
 - def __init__(): Initializes the ExpenseReportInfo class
 - def init_table(): Creates the table for storing expense report header information
 - def _to_str(): Converts a date object to an ISO string or returns None
 - def _to_date(): Attempts to interpret a string or object as a date; returns None on failure
 - def get_for_user(): Fetches the user's expense report header row or returns None
 - def upsert_for_user(): Inserts or updates the user’s report-wide expense info
class ExpenseEntry: Single expense line item model.
 - def __init__(): Initializes the ExpenseEntry class
 - def init_table(): Creates the expense_entries table if missing
 - def _to_str(): Converts a date object to an ISO string or returns None
 - def _to_date(): Attempts to interpret a string or object as a date; returns None on failure
 - def create(): Insert new expense row.
 - def get_all_for_user(): Fetch user’s expense entries.
 - def update(): Updates allowed fields of an expense entry identified by user and id
 - def delete(): Deletes a specific expense entry for a user
 - def delete_all_for_user(): Deletes all expense entries belonging to a user
class MileageHeader: Stores header information for mileage reports, one row per user
 - def init_table(): Creates the mileage_header table if missing
 - def get(): Fetches the stored header info for a user or returns an empty dict
 - def save(): Inserts or updates a user's mileage header using an UPSERT
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

# Expense reports
class ExpenseReportInfo:
# Stores a user's report-level expense metadata; only one row exists per user.
    def __init__(
            self,
            id: int,
            user: str,
            name: str = "",
            employee_number: str = "",
            telephone_number: str = "",
            mail_team: str = "",
            group_name: str = "",
            division: str = "",
            destination_purpose: str = "",
            report_date: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            bc: str = "",
            account_number: str = "",
    ):
        self.id = id
        self.user = user
        self.name = name
        self.employee_number = employee_number
        self.telephone_number = telephone_number
        self.mail_team = mail_team
        self.group_name = group_name
        self.division = division
        self.destination_purpose = destination_purpose

        # convert date strings to date objects
        self.report_date = self._to_date(report_date)
        self.start_date = self._to_date(start_date)
        self.end_date = self._to_date(end_date)
        self.bc = bc
        self.account_number = account_number

    #------------init db table------------------------
    @staticmethod
    def init_table():
    # Creates the table for storing expense report header information.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expense_report_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT UNIQUE,
                name TEXT,
                employee_number TEXT,
                telephone_number TEXT,
                mail_team TEXT,
                group_name TEXT,
                division TEXT,
                destination_purpose TEXT,
                report_date TEXT,
                start_date TEXT,
                end_date TEXT,
                bc TEXT,
                account_number TEXT
            )
        """)
        conn.commit()
        conn.close()

    # --------- helpers for date conversion ----------
    @staticmethod
    def _to_str(d: date | None) -> str | None:
    # Converts a date object to an ISO string or returns None.
        return d.isoformat() if d else None

    @staticmethod
    def _to_date(s: str | None) -> date | None:
    # Attempts to interpret a string or object as a date; returns None on failure.
        if not s:
            return None
        # Already a date object
        if isinstance(s, date):
            return s
        # Handle strings
        s = str(s).strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        try:
            return date.fromisoformat(s)
        except:
            return None

    # --------- CRUD-style helpers ----------

    @classmethod
    def get_for_user(cls, user: str) -> "ExpenseReportInfo | None":
    # Fetches the user's expense report header row or returns None.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user, name, employee_number, telephone_number, mail_team, "
            "group_name, division, destination_purpose, report_date, start_date, end_date, bc, account_number "
            "FROM expense_report_info WHERE user = ? LIMIT 1",
            (user,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return cls(*row)

    @classmethod
    def upsert_for_user(
    # Inserts or updates the user’s report-wide expense info and returns the resulting object.
        cls,
        user: str,
        name: str = "",
        employee_number: str = "",
        telephone_number: str = "",
        mail_team: str = "",
        group_name: str = "",
        division: str = "",
        destination_purpose: str = "",
        report_date: date | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        bc: str = "",
        account_number: str = "",
    ) -> "ExpenseReportInfo":
        conn = get_connection()
        cur = conn.cursor()

        # convert dates to ISO strings
        rd = cls._to_str(report_date)
        sd = cls._to_str(start_date)
        ed = cls._to_str(end_date)

        existing = cls.get_for_user(user)
        if existing is None:
            cur.execute(
                """
                INSERT INTO expense_report_info (
                    user, name, employee_number, telephone_number, mail_team,
                    group_name, division, destination_purpose,
                    report_date, start_date, end_date,
                    bc, account_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user,name,employee_number,telephone_number,mail_team,group_name,division,
                 destination_purpose,rd,sd,ed,bc,account_number,),
            )
            conn.commit()
            model_signals.expense_changed.emit()
            new_id = cur.lastrowid
            conn.close()
            return cls(new_id,user,name,employee_number,telephone_number,mail_team,group_name,division,
                destination_purpose,rd,sd,ed,bc,account_number,)
        else:
            cur.execute(
                """
                UPDATE expense_report_info
                SET name = ?, employee_number = ?, telephone_number = ?,
                    mail_team = ?, group_name = ?, division = ?,
                    destination_purpose = ?, report_date = ?,
                    start_date = ?, end_date = ?, bc = ?, account_number = ?
                WHERE user = ?
                """,
                (name,employee_number,telephone_number,mail_team,group_name,division,
                    destination_purpose,rd,sd,ed,bc,account_number,user,),
            )
            conn.commit()
            model_signals.expense_changed.emit()
            conn.close()
            # return updated object
            return cls.get_for_user(user)


class ExpenseEntry:
# Represents a single expense line item for a user.
    def __init__(
        self,
        id: int,
        user: str,
        expense_date: str | None,
        destination: str,
        miles: float,
        rental: float,
        air_cash: float,
        air: float,
        hotel: float,
        meals: float,
        ent_bus_mtgs: float,
        parking: float,
        telephone: float,
        misc: float,
        explanation: str,
    ):
        self.id = id
        self.user = user
        self.expense_date = expense_date   # stored as ISO string or None
        self.destination = destination
        self.miles = miles
        self.rental = rental
        self.air_cash = air_cash
        self.air = air
        self.hotel = hotel
        self.meals = meals
        self.ent_bus_mtgs = ent_bus_mtgs
        self.parking = parking
        self.telephone = telephone
        self.misc = misc
        self.explanation = explanation

    # ------------------init db info---------------------
    @staticmethod
    def init_table():
    # Creates the expense_entries table if missing.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expense_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                expense_date TEXT,
                destination TEXT,
                miles REAL,
                rental REAL,
                air_cash REAL,
                air REAL,
                hotel REAL,
                meals REAL,
                ent_bus_mtgs REAL,
                parking REAL,
                telephone REAL,
                misc REAL,
                explanation TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def _to_str(d: date | None) -> str | None:
    # Converts a date object to an ISO string or returns None
        return d.isoformat() if d else None

    @staticmethod
    def _to_date(s: str | None) -> date | None:
    # Attempts to interpret a string or object as a date; returns None on failure
        if not s:
            return None
        return datetime.strptime(s, "%Y-%m-%d").date()

    # ---------- CRUD helpers ----------

    @classmethod
    def create(
        cls,
        user: str,
        expense_date: date | None,
        destination: str,
        miles: float = 0.0,
        rental: float = 0.0,
        air_cash: float = 0.0,
        air: float = 0.0,
        hotel: float = 0.0,
        meals: float = 0.0,
        ent_bus_mtgs: float = 0.0,
        parking: float = 0.0,
        telephone: float = 0.0,
        misc: float = 0.0,
        explanation: str = "",
    ) -> "ExpenseEntry":
        conn = get_connection()
        cur = conn.cursor()

        ed = cls._to_str(expense_date)

        cur.execute(
            """
            INSERT INTO expense_entries (
                user, expense_date, destination, miles, rental,
                air_cash, air, hotel, meals, ent_bus_mtgs,
                parking, telephone, misc, explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user,ed,destination,miles,rental,air_cash,air,hotel,meals,ent_bus_mtgs,parking,
                telephone,misc,explanation,),
        )
        conn.commit()
        model_signals.expense_changed.emit()
        new_id = cur.lastrowid
        conn.close()

        return cls(
            new_id,user,ed,destination,miles,rental,air_cash,air,hotel,meals,ent_bus_mtgs,parking,
            telephone,misc,explanation,)

    @classmethod
    def get_all_for_user(cls, user: str) -> list["ExpenseEntry"]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user, expense_date, destination, miles, rental, air_cash, air, "
            "hotel, meals, ent_bus_mtgs, parking, telephone, misc, explanation "
            "FROM expense_entries WHERE user = ? ORDER BY expense_date ASC, id ASC",
            (user,),
        )
        rows = cur.fetchall()
        conn.close()
        return [cls(*row) for row in rows]

    @classmethod
    def update(
    # Updates allowed fields of an expense entry identified by user and id.
        cls,
        entry_id: int,
        user: str,
        **fields,
    ):
        if not fields:
            return
        allowed = {
            "expense_date",
            "destination",
            "miles",
            "rental",
            "air_cash",
            "air",
            "hotel",
            "meals",
            "ent_bus_mtgs",
            "parking",
            "telephone",
            "misc",
            "explanation",
        }
        set_parts = []
        values = []
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "expense_date" and isinstance(value, date):
                value = cls._to_str(value)
            set_parts.append(f"{key} = ?")
            values.append(value)
        if not set_parts:
            return

        values.append(user)
        values.append(entry_id)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            f"UPDATE expense_entries SET {', '.join(set_parts)} WHERE user = ? AND id = ?",
            values,
        )
        conn.commit()
        model_signals.expense_changed.emit()
        conn.close()

    @classmethod
    def delete(cls, entry_id: int, user: str):
    # Deletes a specific expense entry for a user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM expense_entries WHERE user = ? AND id = ?", (user, entry_id))
        conn.commit()
        model_signals.expense_changed.emit()
        conn.close()

    @classmethod
    def delete_all_for_user(cls, user: str):
    # Deletes all expense entries belonging to a user.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM expense_entries WHERE user = ?", (user,))
        conn.commit()
        model_signals.expense_changed.emit()
        conn.close()


class MileageHeader:
# Stores header information for mileage reports, one row per user.
    @staticmethod
    def init_table():
    # Creates the mileage_header table if missing.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mileage_header (
                user TEXT PRIMARY KEY,
                employee_name TEXT,
                employee_number TEXT,
                telephone_number TEXT,
                mail_team TEXT,
                vehicle_make TEXT,
                model TEXT,
                license_plate TEXT,
                begin_date TEXT,
                end_date TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def get(user: str):
    # Fetches the stored header info for a user or returns an empty dict.
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT employee_name, employee_number, telephone_number,
                   mail_team, vehicle_make, model, license_plate,
                   begin_date, end_date
            FROM mileage_header
            WHERE user = ?
        """, (user,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return {}

        return {
            "employee_name": row[0] or "",
            "employee_number": row[1] or "",
            "telephone_number": row[2] or "",
            "mail_team": row[3] or "",
            "vehicle_make": row[4] or "",
            "model": row[5] or "",
            "license_plate": row[6] or "",
            "begin_date": row[7] or "",
            "end_date": row[8] or "",
        }

    @staticmethod
    def save(user: str, values: dict):
    # Inserts or updates a user's mileage header using an UPSERT.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO mileage_header (
                user, employee_name, employee_number, telephone_number,
                mail_team, vehicle_make, model, license_plate,
                begin_date, end_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user) DO UPDATE SET
                employee_name=excluded.employee_name,
                employee_number=excluded.employee_number,
                telephone_number=excluded.telephone_number,
                mail_team=excluded.mail_team,
                vehicle_make=excluded.vehicle_make,
                model=excluded.model,
                license_plate=excluded.license_plate,
                begin_date=excluded.begin_date,
                end_date=excluded.end_date;
        """, (
            user,
            values.get("employee_name", ""),
            values.get("employee_number", ""),
            values.get("telephone_number", ""),
            values.get("mail_team", ""),
            values.get("vehicle_make", ""),
            values.get("model", ""),
            values.get("license_plate", ""),
            values.get("begin_date", ""),
            values.get("end_date", ""),
        ))

        conn.commit()
        conn.close()