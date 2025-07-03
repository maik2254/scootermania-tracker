from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

STATUS_COORDS = {
    'en miami': "25°46'00.4\"N 80°08'47.5\"W",
    'en aduana de cuba': "23°08'12.0\"N 82°20'51.2\"W",
    'en transito': "23.5, -82.0"
}

STATUS_COORDS_DECIMAL = {
    'en miami': (25.766778, -80.146528),         # 25°46'00.4"N 80°08'47.5"W
    'en aduana de cuba': (23.136667, -82.347556),
    'en transito': (23.5, -82.0)
}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    coords = None
    lat, lon = (None, None)
    if request.method == 'POST':
        order_id = request.form['order_id']
        conn = get_db_connection()
        order = conn.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
        conn.close()
        if order:
            status = order['status']
            coords = STATUS_COORDS.get(status)
            lat, lon = STATUS_COORDS_DECIMAL.get(status, (None, None))
        else:
            status = 'Tracking code not found.'
            coords = None
            lat, lon = (None, None)
    return render_template('index.html', status=status, coords=coords, lat=lat, lon=lon)

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

    editing_order = None

    conn = get_db_connection()

    # Check if editing (GET param)
    edit_id = request.args.get('edit')
    if edit_id:
        order = conn.execute('SELECT * FROM orders WHERE order_id = ?', (edit_id,)).fetchone()
        if order:
            editing_order = {'order_id': order['order_id'], 'status': order['status']}
    # Handle form submission
    if request.method == 'POST':
        if request.form.get('editing') == '1':
            # Edit existing order
            original_order_id = request.form['original_order_id']
            new_order_id = request.form['order_id']
            new_status = request.form['status']
            conn.execute('UPDATE orders SET order_id = ?, status = ? WHERE order_id = ?', (new_order_id, new_status, original_order_id))
            conn.commit()
            return redirect(url_for('admin'))
        else:
            # Create new order
            order_id = request.form['order_id']
            status = request.form['status']
            conn.execute('INSERT OR IGNORE INTO orders (order_id, status) VALUES (?, ?)', (order_id, status))
            conn.commit()
            return redirect(url_for('admin'))

    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    orders_with_coords = [
        {
            'order_id': o['order_id'],
            'status': o['status'],
            'coords': STATUS_COORDS.get(o['status'])
        }
        for o in orders
    ]
    return render_template('admin.html', orders=orders_with_coords, editing_order=editing_order)

@app.route('/delete/<order_id>', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)