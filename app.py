"""
Secure Campus Communication System with Steganography
App factory and entry point
"""

from flask import Flask
from extensions import db, login_manager
from auth import auth_bp
from messages import messages_bp
from views import views_bp
from steg import steg_bp
import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']                     = os.environ.get('SECRET_KEY', 'change-me-in-production')
    # Use absolute path for DB so it works from any working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path  = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(base_dir, "campus.db")}')
    app.config['SQLALCHEMY_DATABASE_URI']        = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH']             = 16 * 1024 * 1024  # 16 MB max upload

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view             = 'auth.login'
    login_manager.login_message          = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    app.register_blueprint(auth_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(steg_bp)

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    from models import User
    import bcrypt
    if not User.query.filter_by(username='admin').first():
        pw = bcrypt.hashpw('Admin@1234'.encode(), bcrypt.gensalt()).decode()
        db.session.add(User(username='admin', password=pw, campus='A', role='admin'))
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    # Local dev: use adhoc SSL. In production (Render/Heroku) SSL is handled by the platform.
    import os
    debug = os.environ.get('FLASK_ENV') != 'production'
    ssl   = 'adhoc' if debug else None
    app.run(debug=debug, ssl_context=ssl, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
