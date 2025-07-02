
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'scootermania_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if session.get('admin'):
        return render_template('admin.html')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
