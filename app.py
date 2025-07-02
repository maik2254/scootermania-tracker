
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database and create table if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Route for home page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# Route for admin panel
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'order_id' in request.form and 'status' in request.form:
            order_id = request.form['order_id']
            status = request.form['status']
            cursor.execute('REPLACE INTO orders (order_id, status) VALUES (?, ?)', (order_id, status))
            conn.commit()

    orders = cursor.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

# Route for logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# Tracker lookup
@app.route('/tracker', methods=['POST'])
def tracker():
    order_id = request.form['order_id']
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()
    if order:
        return render_template('status.html', order=order)
    else:
        return render_template('status.html', error='Tracking number not found')

if __name__ == '__main__':
    app.run(debug=True)
