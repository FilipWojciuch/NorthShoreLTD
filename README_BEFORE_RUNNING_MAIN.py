#Please run this first so that the username and hashed password get created.
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_users():
    conn = sqlite3.connect('northshore.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )''')

    cursor.execute("DELETE FROM users")

    users_to_create = [
        ('admin', 'admin123', 'Admin'),
        ('warehouse1', 'stock123', 'Warehouse staff'),
        ('driver1', 'drive123', 'Drivers'),
        ('shipment1', 'ship123', 'Shipment staff')
    ]

    for username, password, role in users_to_create:
        pwd_hash = hash_password(password)
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, pwd_hash, role))
            print(f"Created: {username} | Role: {role}")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_users()
    print("\nSystem ready. Use these credentials to test different access levels.")