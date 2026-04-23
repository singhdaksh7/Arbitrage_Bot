"""
Flask application factory
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Initialize scheduler for background tasks (safely)
    try:
        from app.scheduler import scheduler
        scheduler.init_app(app)
        if os.environ.get('RENDER') is None:  # Only auto-start on local development
            scheduler.start()
            logger.info("✅ Scheduler initialized and started")
        else:
            logger.info("ℹ️ Scheduler initialized (disabled on Render)")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler initialization warning: {str(e)}")
    
    # Initialize alerts
    try:
        from app.alerts import alert_manager
        logger.info("✅ Alert manager initialized")
    except Exception as e:
        logger.warning(f"⚠️ Alert manager warning: {str(e)}")
    
    return app
