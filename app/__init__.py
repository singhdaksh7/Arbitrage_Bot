"""
Flask application factory
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
import os

db = SQLAlchemy()

def create_app(config_name='development'):
    """Create and configure Flask app"""
    
    # Get the project root directory (parent of app folder)
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create Flask app with correct template and static folders
    app = Flask(
        __name__,
        template_folder=os.path.join(app_root, 'templates'),
        static_folder=os.path.join(app_root, 'static')
    )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Enable CORS
    CORS(app)
    
    # Create database directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Register blueprints
    from app.routes.api import api_bp
    from app.routes.web import web_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    return app
