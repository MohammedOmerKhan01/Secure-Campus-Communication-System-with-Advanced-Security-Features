"""
Authentication blueprint with strong password enforcement
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from logger import log_event
import bcrypt, re

auth_bp = Blueprint('auth', __name__)


# ── Password strength validator ───────────────────────────────────────────────
def validate_password(password):
    """
    Returns (is_valid, error_message).
    Rules: 8+ chars, uppercase, lowercase, digit, special char.
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number.'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', password):
        return False, 'Password must contain at least one special character.'
    return True, ''


def valid_username(u):
    return bool(re.match(r'^\w{3,30}$', u))


def check_creds(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return user
    return None


# ── Landing ───────────────────────────────────────────────────────────────────
@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        dest = 'views.admin_dashboard' if current_user.role == 'admin' else 'views.dashboard'
        return redirect(url_for(dest))
    return render_template('index.html')


# ── Campus login ──────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')

        user = check_creds(username, password)
        if not user or user.role == 'admin':
            log_event('LOGIN_FAILED', username or 'unknown', 'Campus portal')
            flash('Invalid credentials.', 'danger')
            return render_template('login.html')

        login_user(user)
        log_event('LOGIN_SUCCESS', user.username, f'Campus {user.campus}')
        return redirect(url_for('views.dashboard'))

    return render_template('login.html')


# ── Admin login ───────────────────────────────────────────────────────────────
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        dest = 'views.admin_dashboard' if current_user.role == 'admin' else 'views.dashboard'
        return redirect(url_for(dest))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = check_creds(username, password)
        if not user or user.role != 'admin':
            log_event('ADMIN_LOGIN_FAILED', username or 'unknown', 'Admin portal')
            flash('Access denied. Admin credentials required.', 'danger')
            return render_template('admin_login.html')

        login_user(user)
        log_event('ADMIN_LOGIN_SUCCESS', user.username, 'Admin portal')
        return redirect(url_for('views.admin_dashboard'))

    return render_template('admin_login.html')


# ── Register ──────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        campus   = request.form.get('campus', '').strip().upper()

        if not username or not password or campus not in ('A', 'B'):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if not valid_username(username):
            flash('Username: 3-30 alphanumeric characters only.', 'danger')
            return render_template('register.html')

        ok, err = validate_password(password)
        if not ok:
            flash(err, 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        db.session.add(User(username=username, password=hashed, campus=campus))
        db.session.commit()

        log_event('REGISTER', username, f'Campus {campus}')
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    log_event('LOGOUT', current_user.username)
    was_admin = current_user.role == 'admin'
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.admin_login' if was_admin else 'auth.login'))
