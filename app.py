
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tracker', methods=['POST'])
def tracker():
    tracking_number = request.form['tracking_number']
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE tracking_number = ?', (tracking_number,)).fetchone()
    conn.close()
    if order:
        return render_template('result.html', order=order)
    else:
        return render_template('index.html', error='Tracking number not found')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['admin'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/update_status', methods=['POST'])
def update_status():
    if not session.get('admin'):
        return redirect('/login')
    tracking_number = request.form['tracking_number']
    new_status = request.form['status']
    conn = get_db_connection()
    conn.execute("UPDATE orders SET status = ? WHERE tracking_number = ?", (new_status, tracking_number))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
