"""
Venue Booking System - Main Application
Flask backend for managing venue bookings
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from supabase import create_client, Client
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing required environment variables!")
    print("Please ensure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env file")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==================== Helper Functions ====================


# ==================== Web Routes ====================

@app.route('/')
def index():
    """Landing page with public calendar"""
    return render_template('index.html')


@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# ==================== Run Application ====================

if __name__ == '__main__':

    # Configuration
    port = int(os.getenv('APP_PORT'))
    host = os.getenv('APP_HOST')
    debug_mode = os.getenv('APP_ENV') == 'development'
    
    # Run the app with auto-reload enabled in debug mode
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode,  # Auto-reload when files change
        threaded=True  # Enable threading for better performance
    )
