"""
Web interface routes
"""

from flask import render_template, request, jsonify
from app.routes import web_bp

@web_bp.route('/')
def index():
    """Landing page"""
    return render_template('landing.html')

@web_bp.route('/dashboard')
def dashboard():
    """Dashboard homepage"""
    return render_template('index.html')

@web_bp.route('/opportunities')
def opportunities():
    """Opportunities page"""
    return render_template('opportunities.html')

@web_bp.route('/trades')
def trades():
    """Trades history page"""
    return render_template('trades.html')

@web_bp.route('/wallet')
def wallet():
    """Wallet page"""
    return render_template('wallet.html')

@web_bp.route('/docs')
def docs():
    """API documentation"""
    return render_template('docs.html')
