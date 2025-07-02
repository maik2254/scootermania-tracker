
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    if request.method == 'POST':
        order_id = request.form['order_id']
        conn = get_db_connection()
        order = conn.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
        conn.close()
        if order:
            status = order['status']
    return render_template('index.html', status=status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        order_id = request.form['order_id']
        status = request.form['status']
        conn = get_db_connection()
        conn.execute("INSERT OR REPLACE INTO orders (order_id, status) VALUES (?, ?)", (order_id, status))
        conn.commit()
        conn.close()

    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
