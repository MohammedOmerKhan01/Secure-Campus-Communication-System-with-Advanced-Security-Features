"""
Activity logger — writes events to the Log table.
"""

from extensions import db
from models import Log
from flask import request


def log_event(action: str, username: str, detail: str = ''):
    """Insert a log entry. Safe to call inside any request context."""
    try:
        ip = request.remote_addr or ''
    except RuntimeError:
        ip = ''

    entry = Log(action=action, username=username, detail=detail, ip=ip)
    db.session.add(entry)
    db.session.commit()
