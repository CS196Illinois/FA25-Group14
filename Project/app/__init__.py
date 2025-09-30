from flask import Flask
from flask_login import LoginManager
from app.models import db, User
import os
import secrets

def create_app():
    app = Flask(__name__)
    
    # Configuration with better security defaults
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if os.environ.get('FLASK_ENV') == 'development':
            secret_key = 'dev-secret-key-change-in-production'
        else:
            # Generate a random key for production if not set (not recommended, set it properly!)
            secret_key = secrets.token_hex(32)
            print("WARNING: Using auto-generated secret key. Set SECRET_KEY environment variable!")
    
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///course_compass.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Additional security configurations
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') != 'development'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
