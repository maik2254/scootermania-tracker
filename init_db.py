
import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create the orders table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    status TEXT NOT NULL
)
''')

# Insert sample data (optional)
cursor.execute("INSERT OR IGNORE INTO orders (order_id, status) VALUES (?, ?)", ("ABC123", "In Miami"))

# Commit and close connection
conn.commit()
conn.close()
print("Database initialized with 'orders' table.")
