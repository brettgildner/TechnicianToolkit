from argon2 import PasswordHasher, exceptions as argon2_exceptions
#   Argon2id is the modern standard for password hashing — secure and slow.
#   PasswordHasher = high-level API for hashing/verifying passwords.
#   exceptions = all the error types that need to be captured safely.
from datetime import datetime
from core.models.inventory_model import get_connection
from core.models.mileage_model import get_connection, MileageEntry
from core.models.parts_model import get_connection
from core.models.service_activity_model import get_connection

"""
This page handles most of the logic that isn't used for the UI, such as: Authentication, user
registration and login, user session state (get_current_user), some of the logic for the 
mileage page, and the unified db initialization for all of the imported models listed below.

core.logic.py index:
- def hash_password(): - hashes plaintext passwords
- def verify_password_argon2(): - verifies that the password matches the stored hash
- def init_user_table(): - ensures the user table exists in the database
- def register_user(): - creates new users (3 step process; listed below)
- def login_user(): - login using Argon2 (4 step process; listed below)
- def _set_current_user(): - internal helper to set the global session user
- def get_current_user(): - returns logged-in username
- def clear_all_mileage_entries(): - clears the mileage tracker for end-of-month export
- def compute_duration(): - calculates service activity duration
    - def parse(): - helper to convert various date/time inputs into consistent datetime objects
- def init_all_tables(): - initializes DB's for all models imported (listed below)
"""

# ----------------------------------------------------------------------------------------------------
# ARGON2 PASSWORD HASHER CONFIGURATION
# Argon2id is recommended by OWASP and NIST.
#
# Parameters:
#   time_cost = number of iterations
#   memory_cost = memory used by hashing (64 MB here)
#   parallelism = number of threads
#
# These settings strike a balance:
#   • strong resistance to GPU cracking
#   • reasonable login speed
#
ph = PasswordHasher(
    time_cost=3,          # Number of hashing iterations
    memory_cost=64 * 1024,  # 64 MB of memory (slows down attackers)
    parallelism=2,        # Use 2 threads for hashing
)

def hash_password(password: str) -> str:
    # This hashes a plaintext password using Argon2id. It returns 'str'-- which is the encoded Argon2
    # hash, containing the algorithm, parameters, the salt, and the hashed password. The result will
    # look like: $argon2id$v=19$m=65536,t=3,p=2$<salt>$<hash>
    return ph.hash(password)

def verify_password_argon2(stored_hash: str, password: str) -> bool:
    # This verifies that the provided password matches the stored Argon2 hash. Returns 'True' if the
    # password is correct and 'False' if the password is incorrect or the hash is invalid.
    # Important: This ONLY verifies Argon2 hashes, there's no legacy SHA fallback for security reasons.
    try:
        return ph.verify(stored_hash, password)
    except (
        argon2_exceptions.VerifyMismatchError,    # wrong password
        argon2_exceptions.VerificationError,      # corrupted hash
        argon2_exceptions.InvalidHash             # invalid format
    ):
        return False
# ----------------------------------------------------------------------------------------------------

# User session management:
# This stores the active username for the current running instance.
# No JWTs, no cookies — just an in-memory session.
current_user: str | None = None

# User table initialization:
def init_user_table():
    # This ensures the "users" table exists in the database. This is called at app startup inside
    # init_all_tables(). Creates columns 'id' (Integer primary key), 'username' (Text [unique]),
    # 'email' (Text), and 'password_hash' (Text [Argon2id string]).

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# User registration:
def register_user(username: str, email: str, password: str) -> bool:
    # This creates a new user account by (1) checking if the username already exists, (2) hashing the
    # password with Argon2id, and (3) inserting the new user into the db. Returns 'True' if the user
    # was created and 'False' if the username already exists.
    conn = get_connection()
    cur = conn.cursor()

    # Check if username exists
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return False  # Username taken

    # Hash password using modern Argon2id
    password_hash = hash_password(password)

    # Insert new user
    cur.execute("""
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    """, (username, email, password_hash))

    conn.commit()
    conn.close()
    return True

# User login:
def login_user(username: str, password: str) -> bool:
    # Performs login using Argon2. Steps: (1) look up user, (2) verify Argon2 hash, (3) if Argon2 parameters
    # changed, silently rehash and update, (4) store the user in the session.
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    user_id, stored_hash = row

    if not stored_hash:
        conn.close()
        return False

    # Step 1: try to verify password
    try:
        if verify_password_argon2(stored_hash, password):

            # Step 2: upgrade outdated hashes
            try:
                if ph.check_needs_rehash(stored_hash):
                    new_hash = ph.hash(password)
                    cur.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (new_hash, user_id)
                    )
                    conn.commit()
            except Exception:
                # If rehashing fails, do NOT block login.
                pass

            conn.close()
            _set_current_user(username)
            return True

    except Exception:
        # Argon2 raised unexpected issue > deny login
        conn.close()
        return False

    conn.close()
    return False  # incorrect password

# Internal session setter:
def _set_current_user(username: str):
    # Internal helper to set the global session user.
    global _current_user
    _current_user = username

def get_current_user() -> str:
    # Returns the logged-in username. If nobody is logged in, defer to 'default_user' (used by DB
    # records that always require a 'user').
    return current_user or "default_user"

def clear_all_mileage_entries(user):
    # NOTE: The mileage tracker was designed to be filled out and exported at the end of the month, this function
    # is designed to be used AFTER the user has exported the mileage tracker to the Excel document when filing
    # their monthly expense report. The function deletes all mileage entries for the current user.
    entries = MileageEntry.get_all_for_user(user)
    for e in entries:
        MileageEntry.delete(e.id, user)

# Service activity logic:
def compute_duration(arr_date: str, arr_time: str, dep_date: str, dep_time: str) -> str:
    # This function calculates the duration of a service activity entry by subtracting the arrival time
    # from the departure, accepting several known patterns (AM/PM, 24hr, with|w/o seconds) and returning
    # the format as "_hrs, _mins".

    def parse(d, t):
        # If v is already a datetime object (from Excel), accept it
        if isinstance(t, datetime):
            return t
        # Combine date + time
        ts = f"{d} {t}".strip()

        # Try multiple known patterns
        patterns = [
            "%Y-%m-%d %I:%M %p",   # 12-hour with AM/PM
            "%Y-%m-%d %H:%M",      # 24-hour HH:MM
            "%Y-%m-%d %H:%M:%S",   # 24-hour HH:MM:SS
        ]

        for p in patterns:
            try:
                return datetime.strptime(ts, p)
            except:
                pass
        # If all formats fail
        return None

    start = parse(arr_date, arr_time)
    end   = parse(dep_date, dep_time)

    # If parsing failed, return 0
    if not start or not end:
        return "0hr, 0min"

    diff = end - start
    mins = int(diff.total_seconds() // 60)
    h, m = divmod(mins, 60)

    hr_label = "hr" if h == 1 else "hrs"
    min_label = "min" if m == 1 else "mins"

    return f"{h}{hr_label}, {m}{min_label}"

# DB initialization for all tables (listed within):
def init_all_tables():
    print("[DB] Initializing all tables...")

    from core.models.inventory_model import InventoryItem
    from core.models.mileage_model import MileageEntry
    from core.models.parts_model import PartsOrder
    from core.models.service_activity_model import ServiceActivity
    from core.models.equipment_model import EquipmentInfo
    from core.models.expense_model import ExpenseEntry, ExpenseReportInfo, MileageHeader

    InventoryItem.init_table()
    MileageEntry.init_table()
    PartsOrder.init_table()
    ServiceActivity.init_table()
    EquipmentInfo.init_table()
    ExpenseReportInfo.init_table()
    ExpenseEntry.init_table()
    MileageHeader.init_table()

    init_user_table()