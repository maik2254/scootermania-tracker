from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['admin_logged_in'] = True
            return redirect('/admin')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':
        order_id = request.form.get('order_id')
        status = request.form.get('status')

        if 'update' in request.form:
            conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
        elif 'create' in request.form:
            conn.execute('INSERT OR IGNORE INTO orders (order_id, status) VALUES (?, ?)', (order_id, status))
        conn.commit()

    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
