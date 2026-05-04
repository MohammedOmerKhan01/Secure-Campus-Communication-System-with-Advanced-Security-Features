"""Views blueprint — HTML page routes."""

from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from models import User, Message, Log
from functools import wraps

views_bp = Blueprint('views', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@views_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('views.admin_dashboard'))
    users    = User.query.filter(User.id != current_user.id, User.role != 'admin').all()
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) |
        (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.desc()).limit(50).all()
    return render_template('dashboard.html', users=users, messages=messages)


@views_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    all_users    = User.query.filter(User.role != 'admin').all()
    all_messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
    recent_logs  = Log.query.order_by(Log.timestamp.desc()).limit(50).all()
    campus_a     = [u for u in all_users if u.campus == 'A']
    campus_b     = [u for u in all_users if u.campus == 'B']
    steg_logs    = Log.query.filter(Log.action.like('STEG%')).order_by(Log.timestamp.desc()).limit(20).all()
    return render_template('admin_dashboard.html',
                           all_users=all_users,
                           all_messages=all_messages,
                           recent_logs=recent_logs,
                           campus_a=campus_a,
                           campus_b=campus_b,
                           steg_logs=steg_logs)


@views_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403
