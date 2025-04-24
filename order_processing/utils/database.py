"""
Database utility module for the order processing application.
"""
import os
import sqlite3
import shutil
from datetime import datetime
import bcrypt

def get_db_connection():
    """Get a connection to the SQLite database."""
    db_path = os.path.join("data", "order_processing.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    # Roles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        role_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles (role_id)
    )
    ''')
    
    # Customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_number TEXT,
        email TEXT UNIQUE,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        description TEXT,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date TIMESTAMP,
        status TEXT NOT NULL,
        total_cost REAL NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')
    
    # Order Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    # Payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        payment_date TIMESTAMP,
        amount REAL NOT NULL,
        payment_type TEXT NOT NULL,
        status TEXT NOT NULL,
        reference_number TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (order_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def seed_default_data():
    """Seed the database with default data if tables are empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if roles table is empty
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        # Add default roles
        roles = [
            (1, "Admin", "Full access to all features"),
            (2, "Cashier", "Can process orders and payments")
        ]
        cursor.executemany("INSERT INTO roles (role_id, name, description) VALUES (?, ?, ?)", roles)
    
    # Check if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Add default admin user (username: admin, password: admin123)
        password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (?, ?, ?, ?, ?)",
            ("admin", password_hash, "Administrator", "admin@example.com", 1)
        )
        
        # Add default cashier user (username: cashier, password: cashier123)
        password_hash = bcrypt.hashpw("cashier123".encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (?, ?, ?, ?, ?)",
            ("cashier", password_hash, "Cashier User", "cashier@example.com", 2)
        )
    
    # Sample customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        customers = [
            ("John Doe", "555-1234", "john.doe@example.com", "123 Main St, Anytown"),
            ("Jane Smith", "555-5678", "jane.smith@example.com", "456 Oak Ave, Somewhere"),
            ("Bob Johnson", "555-9012", "bob.johnson@example.com", "789 Pine Rd, Elsewhere")
        ]
        cursor.executemany(
            "INSERT INTO customers (name, contact_number, email, address) VALUES (?, ?, ?, ?)",
            customers
        )
    
    # Sample products
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ("Laptop", "TECH001", "High-performance laptop", 999.99, 10),
            ("Smartphone", "TECH002", "Latest smartphone model", 699.99, 15),
            ("Tablet", "TECH003", "10-inch tablet", 349.99, 20),
            ("Headphones", "ACC001", "Wireless noise-canceling headphones", 149.99, 30),
            ("Mouse", "ACC002", "Wireless ergonomic mouse", 29.99, 50)
        ]
        cursor.executemany(
            "INSERT INTO products (name, sku, description, price, stock_quantity) VALUES (?, ?, ?, ?, ?)",
            products
        )
    
    conn.commit()
    conn.close()

def backup_database(backup_path):
    """Create a backup of the database.
    
    Args:
        backup_path: Path to save the backup file
        
    Returns:
        True if backup was successful, False otherwise
    """
    try:
        db_path = os.path.join("data", "order_processing.db")
        shutil.copy2(db_path, backup_path)
        return True
    except Exception:
        return False

def restore_database(backup_path):
    """Restore the database from a backup.
    
    Args:
        backup_path: Path to the backup file
        
    Returns:
        True if restore was successful, False otherwise
    """
    try:
        db_path = os.path.join("data", "order_processing.db")
        shutil.copy2(backup_path, db_path)
        return True
    except Exception:
        return False