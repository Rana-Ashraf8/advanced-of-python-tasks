from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    init_db()

@app.route('/')
def index():
    if "user_id" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not email or not password:
            flash('Please fill in all fields.')
            return redirect(url_for('signup'))

        if password != confirm:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        hashed = generate_password_hash(password)
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed)
            )
            db.commit()
            flash('Account created successfully. You can now login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (identifier, identifier)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))

        flash('Invalid username/email or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    return render_template('dashboard.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
            """)
    app.run(debug=True)
