from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DB_PATH = 'status.db'

# Initialize database if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    if request.method == 'POST':
        order_id = request.form['order_id']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT status FROM orders WHERE order_id=?", (order_id,))
        result = cur.fetchone()
        conn.close()
        if result:
            status = result['status']
        else:
            status = "Order ID not found."
    return render_template('index.html', status=status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        order_id = request.form['order_id']
        status = request.form['status']
        conn.execute("INSERT OR REPLACE INTO orders (order_id, status) VALUES (?, ?)", (order_id, status))
        conn.commit()

    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
