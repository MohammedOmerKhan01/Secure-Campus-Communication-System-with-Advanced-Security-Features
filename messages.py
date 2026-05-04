"""
Messages blueprint
  POST  /send-message    — send a message
  GET   /get-messages    — fetch messages (own or all for admin)
  GET   /get-users       — list users for recipient dropdown
  GET   /admin/logs      — activity logs (admin only)
  GET   /admin/users     — all users (admin only)
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Message, Log
from logger import log_event
from functools import wraps

messages_bp = Blueprint('messages', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required.'}), 403
        return f(*args, **kwargs)
    return decorated


# ── send message ──────────────────────────────────────────────────────────────
@messages_bp.route('/send-message', methods=['POST'])
@login_required
def send_message():
    data     = request.get_json(silent=True) or request.form
    receiver_username = (data.get('receiver') or '').strip()
    content           = (data.get('message')  or '').strip()

    if not receiver_username or not content:
        return jsonify({'error': 'Receiver and message are required.'}), 400

    if len(content) > 2000:
        return jsonify({'error': 'Message too long (max 2000 chars).'}), 400

    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        return jsonify({'error': 'Recipient not found.'}), 404

    if receiver.id == current_user.id:
        return jsonify({'error': 'Cannot message yourself.'}), 400

    msg = Message(sender_id=current_user.id, receiver_id=receiver.id, content=content)
    db.session.add(msg)
    db.session.commit()

    log_event('MESSAGE_SENT', current_user.username,
              f'To {receiver.username} (Campus {receiver.campus})')

    return jsonify({'message': 'Sent.', 'id': msg.id}), 201


# ── get messages ──────────────────────────────────────────────────────────────
@messages_bp.route('/get-messages', methods=['GET'])
@login_required
def get_messages():
    with_user = request.args.get('with', '').strip()

    if current_user.role == 'admin':
        query = Message.query.order_by(Message.timestamp.desc())
    else:
        query = Message.query.filter(
            (Message.sender_id == current_user.id) |
            (Message.receiver_id == current_user.id)
        ).order_by(Message.timestamp.desc())

    if with_user:
        other = User.query.filter_by(username=with_user).first()
        if not other:
            return jsonify({'error': 'User not found.'}), 404
        query = query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == other.id)) |
            ((Message.sender_id == other.id) & (Message.receiver_id == current_user.id))
        )

    msgs = query.limit(100).all()
    return jsonify({'messages': [m.to_dict() for m in msgs]}), 200


# ── get users ─────────────────────────────────────────────────────────────────
@messages_bp.route('/get-users', methods=['GET'])
@login_required
def get_users():
    users = User.query.filter(User.id != current_user.id, User.role != 'admin').all()
    return jsonify({'users': [{'username': u.username, 'campus': u.campus} for u in users]}), 200


# ── admin: logs ───────────────────────────────────────────────────────────────
@messages_bp.route('/admin/logs', methods=['GET'])
@login_required
@admin_required
def admin_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(200).all()
    return jsonify({'logs': [l.to_dict() for l in logs]}), 200


# ── admin: broadcast ─────────────────────────────────────────────────────────
@messages_bp.route('/admin/broadcast', methods=['POST'])
@login_required
@admin_required
def admin_broadcast():
    """Send one message to every user in the selected target (A, B, or both)."""
    data    = request.get_json(silent=True) or request.form
    content = (data.get('message') or '').strip()
    target  = (data.get('target')  or 'all').strip().upper()   # 'A' | 'B' | 'ALL'

    if not content:
        return jsonify({'error': 'Message content is required.'}), 400
    if len(content) > 2000:
        return jsonify({'error': 'Message too long (max 2000 chars).'}), 400
    if target not in ('A', 'B', 'ALL'):
        return jsonify({'error': 'Target must be A, B, or ALL.'}), 400

    # Build recipient list
    query = User.query.filter(User.role != 'admin', User.id != current_user.id)
    if target != 'ALL':
        query = query.filter(User.campus == target)
    recipients = query.all()

    if not recipients:
        return jsonify({'error': 'No users found for the selected campus.'}), 404

    for user in recipients:
        db.session.add(Message(
            sender_id=current_user.id,
            receiver_id=user.id,
            content=content
        ))
    db.session.commit()

    label = f'Campus {target}' if target != 'ALL' else 'All Campuses (A + B)'
    log_event('BROADCAST', current_user.username,
              f'{label} — {len(recipients)} recipients')

    return jsonify({
        'message': f'Broadcast sent to {len(recipients)} user(s).',
        'count':   len(recipients)
    }), 201


# ── admin: users ──────────────────────────────────────────────────────────────
@messages_bp.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def admin_users():
    users = User.query.filter(User.role != 'admin').all()
    return jsonify({'users': [
        {'id': u.id, 'username': u.username, 'campus': u.campus}
        for u in users
    ]}), 200
