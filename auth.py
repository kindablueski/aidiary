from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Username and password are required.", "info")
            return redirect(url_for('auth.register'))
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
            user_id = cur.lastrowid
            conn.close()
            session['user_id'] = user_id
            session['username'] = username
            flash("Registration successful! Please complete the wellness quiz.", "info")
            return redirect(url_for('quiz.quiz_start'))
        except Exception:
            flash("Username already exists or an error occurred. Please choose a different one.", "info")
            return redirect(url_for('auth.register'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            if user['quiz_taken'] == 0:
                return redirect(url_for('quiz.quiz_start'))
            else:
                return redirect(url_for('diary.diary'))
        else:
            flash("Invalid username or password.", "info")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/auth.logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
