import sqlite3

def database_run():
    """Requirement (a): Develop a centralised database system using SQLite."""
    conn = sqlite3.connect('northshore.db')
    cursor = conn.cursor()

    # Shipments with financial and delivery details
    cursor.execute('''CREATE TABLE IF NOT EXISTS shipments (
        shipment_id TEXT PRIMARY KEY,
        order_number TEXT,
        sender_details TEXT,
        receiver_details TEXT,
        status TEXT,
        vehicle_id TEXT,
        driver_name TEXT,
        delivery_date TEXT,
        route_details TEXT,
        cost REAL,
        surcharges REAL DEFAULT 0.0,
        payment_status TEXT DEFAULT 'Pending'
    )''')

    # Fleet Management
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id TEXT PRIMARY KEY,
        capacity REAL,
        maintenance_schedule TEXT,
        availability TEXT
    )''')

    # Inventory tracking
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse_id TEXT,
        item_name TEXT,
        quantity INTEGER,
        reorder_level INTEGER
    )''')

    # Users and RBAC
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )''')

    conn.commit()
    conn.close()

def execute_query(query, params=()):
    with sqlite3.connect('northshore.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()

if __name__ == "__main__":
    database_run()
    print("Database Schema Initialised.")