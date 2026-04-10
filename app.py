"""
Venue Booking System - Main Application
Flask backend for managing venue bookings
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from functools import wraps
import requests
import json 
import time
from werkzeug.utils import secure_filename

try:
    r = requests.get("https://google.com")
    print("Internet OK:", r.status_code)
except Exception as e:
    print("Internet FAIL:", e)

# ==================== Load Environment ====================
load_dotenv()

# ==================== Initialize Flask ====================
app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'super-secret-key-change-this')

# ==================== Supabase Setup ====================
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
    exit(1)

print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY:", SUPABASE_KEY[:10] if SUPABASE_KEY else None)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== Auth Decorator ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Signup Route ====================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                supabase.table("users").insert({
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": name
                }).execute()
                return "✅ Signup successful! Please login."

            return "⚠️ Signup done, check email"

        except Exception as e:
            print("ERROR DETAILS:", e)
            return f"❌ Error: {str(e)}" 

    return render_template("signup.html")

# ==================== Login Route ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                session["user"] = response.user.id
                session["email"] = response.user.email
                return redirect(url_for("index"))

            return "❌ Invalid login"

        except Exception as e:
            print("ERROR:", e)
            return "Login error occurred"

    return render_template("login.html")

# ==================== Dashboard (Protected) ====================
@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome {session['email']} 🎉"

# ==================== Logout ====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==================== Home ====================
@app.route("/")
def index():
    return render_template("index.html")

# ==================== Test Signup ====================
@app.route("/test-signup")
def test_signup():
    try:
        response = supabase.auth.sign_up({
            "email": "testuser12345@gmail.com",
            "password": "12345678"
        })
        if response.user:
            return "✅ Supabase working!"
        return "❌ Failed"
    except Exception as e:
        print("ERROR:", e)
        return "Error"

# ==================== Event Page Route ====================
@app.route('/event')
def event_page():
    """Event creation form"""
    return render_template('event.html')


# ==================== API Routes (Dropdowns & Data) ====================
@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    try:
        response = supabase.table('clubs').select('id, name').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/venues', methods=['GET'])
def get_venues():
    try:
        response = supabase.table('venues').select('id, name').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/event-types', methods=['GET'])
def get_event_types():
    try:
        response = supabase.table('event_types').select('id, event_type_name').execute()
        data = [{'id': item['id'], 'name': item['event_type_name']} for item in response.data]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/facilities/<venue_id>', methods=['GET'])
def get_facilities_for_venue(venue_id):
    """Fetch amenities AND their max quantity available at a specific venue"""
    try:
        response = supabase.table('venue_facilities') \
            .select('facility_id, quantity, facilities(id, f_name)') \
            .eq('venue_id', venue_id) \
            .execute()
        
        data = []
        for item in response.data:
            if item.get('facilities'):
                data.append({
                    'id': item['facilities']['id'],
                    'name': item['facilities']['f_name'],
                    'max_quantity': item['quantity']
                })
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar-events', methods=['GET'])
def get_calendar_events():
    """Fetch all events and format them for FullCalendar.js"""
    try:
        response = supabase.table('Events').select('id, title, start_time, end_time').execute()
        
        formatted_events = []
        for item in response.data:
            formatted_events.append({
                'id': item['id'],
                'title': item['title'],
                'start': item['start_time'], 
                'end': item['end_time'],
                'backgroundColor': '#2563eb', 
                'borderColor': '#1d4ed8'
            })
        return jsonify(formatted_events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MAIN EVENT SUBMISSION ====================
@app.route('/api/events', methods=['POST'])
def create_event():
    """Handle event form submission, file upload, and facility JSON parsing"""
    try:
        data = dict(request.form)
        
        # 1. Grab the JSON string of facilities and convert it to a Python list
        facilities_to_insert = []
        if 'facilities_json' in data:
            facilities_list = json.loads(data['facilities_json'])
            
            # Format it exactly how our Supabase event_facilities table expects it
            for item in facilities_list:
                facilities_to_insert.append({
                    "facility_id": item['id'],
                    "requested_quantity": item['quantity']
                })
            
            # Remove the raw JSON string from the main data dictionary 
            data.pop('facilities_json', None)

        # 2. Handle the File Upload
        permission_file = request.files.get('permission_file')
        if permission_file and permission_file.filename:
            original_filename = secure_filename(permission_file.filename)
            unique_filename = f"{int(time.time())}_{original_filename}"
            file_bytes = permission_file.read()

            supabase.storage.from_('approved_letters').upload(
                file=file_bytes,
                path=unique_filename,
                file_options={"content-type": permission_file.content_type}
            )
            public_url = supabase.storage.from_('approved_letters').get_public_url(unique_filename)
            data['permission_file_url'] = public_url

        # 3. Insert the main data into the Events table
        event_response = supabase.table('Events').insert(data).execute()
        
        # Grab the newly generated Event ID
        new_event_id = event_response.data[0]['id']

        # 4. Insert the requested facilities into the junction table
        if facilities_to_insert:
            # Attach the new event ID to every facility in the list
            for f in facilities_to_insert:
                f['event_id'] = new_event_id
                
            # Perform a bulk insert into event_facilities
            supabase.table('event_facilities').insert(facilities_to_insert).execute()

        return jsonify({'message': 'Event created successfully!', 'data': event_response.data}), 201
        
    except Exception as e:
        print("ERROR DETAILS:", str(e)) 
        return jsonify({'error': str(e)}), 500

# ==================== Run App ====================
if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 5000))
    host = os.getenv("APP_HOST", "127.0.0.1")
    debug_mode = os.getenv("APP_ENV") == "development"

    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode,
        threaded=True
    )