#!/usr/bin/env python
"""
Production server for Geopark Tuban Management System
Optimized for better performance
"""
from app import create_app
import os

# Create production app instance
app = create_app()

# Production configuration
if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        from models import db
        db.create_all()

    # Production server settings
    print("Starting production server...")
    print("Access URL: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")

    # Run with production settings
    app.run(
        host='0.0.0.0',           # Allow external connections
        port=5000,                 # Default port
        debug=False,              # Disable debug mode
        threaded=True,            # Enable threading
        use_reloader=False,       # Disable reloader
        use_debugger=False        # Disable debugger
    )