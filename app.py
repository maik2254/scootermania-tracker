
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3


def get_coordinates_from_status(status: str):
    """Return latitude and longitude tuple based on status text."""
    if not status:
        return None

    text = status.lower()

    # Mapping of key phrases to coordinates
    mapping = {
        "en miami": (25.761681, -80.191788),
        "en aduana de cuba": (23.1387, -82.3539),
        "en transito": (23.5, -82.0),
        # Legacy English phrases kept for compatibility
        "miami": (25.761681, -80.191788),
        "havana": (23.1136, -82.3666),
        "ocean": (24.5, -81.0),
    }

    for phrase, coords in mapping.items():
        if phrase in text:
            return coords

    return None

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    coords = None
    if request.method == 'POST':
        order_id = request.form['order_id']
        conn = get_db_connection()
        order = conn.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
        conn.close()
        if order:
            status = order['status']
            coords = get_coordinates_from_status(status)
        else:
            status = 'Tracking code not found.'
    return render_template('index.html', status=status, location=coords)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'adminpass':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Invalid Credentials'
    return render_template('login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        if 'update' in request.form:
            order_id = request.form['order_id']
            new_status = request.form['status']
            conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', (new_status, order_id))
            conn.commit()
        elif 'create' in request.form:
            order_id = request.form['new_order_id']
            status = request.form['new_status']
            conn.execute('INSERT INTO orders (order_id, status) VALUES (?, ?)', (order_id, status))
            conn.commit()

    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
