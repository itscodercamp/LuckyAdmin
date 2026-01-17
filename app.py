from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
import os
from models import db, Admin, User
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'lucky-lubricants-prod-secret-9988')
    
    # Deployment Database Handling
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///lucky_lubricant.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)
    
    # CORS Configuration - Fully Permissive
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    login_manager = LoginManager()
    login_manager.login_view = 'admin_routes.admin_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.wallet import wallet_bp
    from routes.rewards import rewards_bp
    from routes.products import products_bp
    from routes.content import content_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(rewards_bp, url_prefix='/api/rewards')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.context_processor
    def inject_notifications():
        from models import Notification
        count = Notification.query.filter_by(is_admin_alert=True, is_read=False).count()
        return dict(unread_admin_notifications_count=count)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('landing.html')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
