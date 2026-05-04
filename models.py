"""
Database models: User, Message, Log
"""
from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    campus   = db.Column(db.String(1), nullable=False)   # 'A' or 'B'
    role     = db.Column(db.String(20), default='user')  # 'user' | 'admin'

    sent_messages     = db.relationship('Message', foreign_keys='Message.sender_id',
                                        backref='sender_user', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id',
                                        backref='receiver_user', lazy=True)


class Message(db.Model):
    __tablename__ = 'messages'
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'sender':          self.sender_user.username,
            'sender_campus':   self.sender_user.campus,
            'receiver':        self.receiver_user.username,
            'receiver_campus': self.receiver_user.campus,
            'content':         self.content,
            'timestamp':       self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class StegMessage(db.Model):
    """Steganographic image message sent between users over the secure channel."""
    __tablename__ = 'steg_messages'
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename    = db.Column(db.String(200), nullable=False)   # stored file on disk
    caption     = db.Column(db.String(255), default='')       # optional visible note
    is_read     = db.Column(db.Boolean, default=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    sender_user   = db.relationship('User', foreign_keys=[sender_id],   backref='sent_steg')
    receiver_user = db.relationship('User', foreign_keys=[receiver_id], backref='received_steg')

    def to_dict(self):
        return {
            'id':              self.id,
            'sender':          self.sender_user.username,
            'sender_campus':   self.sender_user.campus,
            'receiver':        self.receiver_user.username,
            'receiver_campus': self.receiver_user.campus,
            'filename':        self.filename,
            'caption':         self.caption,
            'is_read':         self.is_read,
            'download_url':    f'/download/{self.filename}',
            'timestamp':       self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class Log(db.Model):
    __tablename__ = 'logs'
    id        = db.Column(db.Integer, primary_key=True)
    action    = db.Column(db.String(100), nullable=False)
    username  = db.Column(db.String(80), nullable=False)
    detail    = db.Column(db.String(255), default='')
    ip        = db.Column(db.String(45), default='')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':        self.id,
            'action':    self.action,
            'username':  self.username,
            'detail':    self.detail,
            'ip':        self.ip,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
