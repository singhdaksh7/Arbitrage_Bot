#!/usr/bin/env python3
"""
Arbitrage Bot - Main Entry Point
Cryptocurrency arbitrage detection and paper trading simulator
"""

import os
import sys
from app import create_app, db

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Starting Arbitrage Bot...")
    print(f"📊 Dashboard: http://127.0.0.1:{port}")
    print(f"🔌 API: http://127.0.0.1:{port}/api")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
