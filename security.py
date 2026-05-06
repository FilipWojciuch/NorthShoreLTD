import hashlib
import logging
import sqlite3

# This sets up the actual text file where logs are saved
logging.basicConfig(
    filename='audit_log.txt',
    level=logging.INFO,
    format='%(asctime)s - User: %(user)s - Action: %(action)s'
)


def hash_password(password):
    """Encrypts the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def log_event(user, action):
    """Records an event to the audit_log.txt file."""
    logging.info('', extra={'user': user, 'action': action})


def verify_login(username, password):
    """Checks credentials and returns the user's role if successful."""
    conn = sqlite3.connect('northshore.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        result = None
    finally:
        conn.close()

    if result:
        db_hash, role = result
        if db_hash == hash_password(password):
            log_event(username, "LOGIN_SUCCESS")
            return role

    log_event(username if username else "UNKNOWN", "LOGIN_FAIL")
    return None