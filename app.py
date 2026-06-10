"""
Venue Booking System - Main Application
Flask backend for managing venue bookings
"""

import email
from flask import flash
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

load_dotenv()


app = Flask(__name__)


app.secret_key = os.getenv('APP_SECRET_KEY', 'super-secret-key-change-this')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
    exit(1)
print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_KEY[:20] if SUPABASE_KEY else "None")
print("KEY LENGTH:", len(SUPABASE_KEY))
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

service_supabase: Client = create_client(
    SUPABASE_URL,
    SERVICE_KEY
)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        email=email.lower().strip()
        if not email.endswith("@saintgits.org"):
            return "Only Saintgits email addresses are allowed."
        reserved_accounts = [ "hodcse@saintgits.org", "hodeee@saintgits.org", "pro@saintgits.org", "admin@saintgits.org" ]
        if email in reserved_accounts:
            return "This email address is reserved for specific users."
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            print("FULL RESPONSE:", response.user.email)

            if response.user:
                special_roles = {
    "hodcse@saintgits.org": "hod_cse",
    "hodeee@saintgits.org": "hod_eee",
    "pro@saintgits.org": "pro",
    "admin@saintgits.org": "admin"
}
                role = special_roles.get(email, "student")
                
                supabase.table("users").insert({
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_name": name,
                    "role": role,
                    "is_active": True
                }).execute()

                return redirect(url_for("login"))
            return "⚠️ Signup completed. Please check your email for verification."

        except Exception as e:
            error = str(e)
            print("ERROR DETAILS:", error)

            if "users_email_key" in error.lower() or "already exists" or "already registered" in error.lower():
                flash(
    "An account with this email already exists. Please login.",
    "error"
)
                return redirect(url_for("signup"))

            flash(
        "Something went wrong. Please try again.",
        "error"
         )
        return redirect(url_for("signup"))
        

    return render_template("signup.html")


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
                user_record = supabase.table("users")\
                    .select("*")\
                    .eq("id", response.user.id)\
                    .single()\
                    .execute()
                session["role"] = user_record.data["role"]
                session["user_name"] = user_record.data["user_name"]
                role = session["role"]
                if role.startswith("hod"):
                    return redirect(url_for("dashboard"))
                elif role == "pro":
                    return redirect(url_for("dashboard"))
                elif role == "admin":
                    return redirect(url_for("dashboard"))
                return redirect(url_for("index"))   
            return "Invalid login. Try again."
        except Exception as e:
            error = str(e)
            print("ERROR DETAILS:", error)
            flash(
        "Invalid email or password.",
        "error"
        )
            return redirect(url_for("login"))
            
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    events = (
        supabase.table("dashboard_events_view")
        .select("*")
        .eq("created_by", session["user"])
        .order("start_time")
        .execute()
    )

    return render_template(
        "dashboard.html",
        events=events.data,
        user_name=session.get("user_name")
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/event')
def event_page():
    """Event creation form"""
    return render_template('event.html')

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
    """Fetch all events from the view and format them for FullCalendar.js"""
    try:
        # 💥 CHANGED: We now query the 'events_view' so we have access to 'venue_name'
        response = supabase.table('events_view').select('id, title, start_time, end_time, venue_name, club_name').execute()
        
        formatted_events = []
        for item in response.data:
            # Combine the title and venue for the calendar display
            display_title = f"{item['title']} ({item['venue_name']})"
            
            formatted_events.append({
                'id': item['id'],
                'title': display_title, # This will now show: "Hackathon (Innovation Hall)"
                'start': item['start_time'], 
                'end': item['end_time'],
                'backgroundColor': '#2563eb', 
                'borderColor': '#1d4ed8'
            })
        return jsonify(formatted_events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    """Handle event form submission, file upload, and facility JSON parsing"""
    try:
        print("STEP 1")
        data = dict(request.form)

        if "user" in session:
            data["created_by"] = session["user"]
        
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

        print("STEP 2")
        # 2. Handle the File Upload
        permission_file = request.files.get('permission_file')
        print("STEP 3")


        if permission_file and permission_file.filename:
            original_filename = secure_filename(permission_file.filename)
            unique_filename = f"{int(time.time())}_{original_filename}"
            file_bytes = permission_file.read()
            try:
                service_supabase.storage.from_('approved_letters').upload(
                    file=file_bytes,
                    path=unique_filename,
                    file_options={"content-type": permission_file.content_type}
                )
                print("UPLOAD SUCCESS")

            except Exception as e:
                print("STORAGE ERROR:")
                print(e)
                raise

            public_url = service_supabase.storage.from_('approved_letters').get_public_url(unique_filename)

            data['permission_file_url'] = public_url
        print(public_url)
        # Determine approval authority
        print("STEP 4")
        venue_id = data.get("venue_id")

        venue_response = (
    supabase.table("venues")
    .select("name")
    .eq("id", venue_id)
    .single()
    .execute()
)

        venue_name = venue_response.data["name"]

        if venue_name == "RB Seminar Hall":
            data["assigned_to"] = "hod_cse"

        elif venue_name == "EEE Seminar Hall":
            data["assigned_to"] = "hod_eee"
        
        elif venue_name == "ME Seminar Hall":
            data["assigned_to"] = "hod_me"

        elif venue_name == "VB Seminar Hall":
            data["assigned_to"] = "hod_ce"

        elif venue_name in [
    "Mini Auditorium",
    "High-Tech Lab",
    "AK Seminar Hall",
    "AB Seminar Hall",
]:
            data["assigned_to"] = "pro"

        else:
            data["assigned_to"] = "pro"

        data["status"] = "Pending Approval"

        print("DATA BEING SENT:")
        print(data)

        print("STEP 4")

        # 3. Insert the main data into the Events table
        event_response = supabase.table('Events').insert(data).execute()
        print("EVENT INSERT SUCCESS")
        
        # Grab the newly generated Event ID
        new_event_id = event_response.data[0]['id']

        # 4. Insert the requested facilities into the junction table
        if facilities_to_insert:
            # Attach the new event ID to every facility in the list
            for f in facilities_to_insert:
                f['event_id'] = new_event_id
                
            # Perform a bulk insert into event_facilities
            print("TRYING FACILITY INSERT")
            supabase.table('event_facilities').insert(facilities_to_insert).execute()
            print("FACILITY INSERT SUCCESS")

        return jsonify({'message': 'Event created successfully!', 'data': event_response.data}), 201
        
    except Exception as e:
        print("ERROR DETAILS:", str(e)) 
        return jsonify({'error': str(e)}), 500

# ==================== Venue Route (Shows the HTML Page) ====================
@app.route("/venue", methods=['GET'])
def venue():
    # Fetch all master lists from Supabase
    locations_response = supabase.table("location").select("*").execute()
    types_response = supabase.table("venue_type").select("*").execute()
    facilities_response = supabase.table("facilities").select("*").execute()

    # Pass the data to the HTML using Jinja
    return render_template(
        "venue.html", 
        locations=locations_response.data,
        venue_types=types_response.data,
        facilities=facilities_response.data
    )

# ==================== Venue API ====================
@app.route("/venues", methods=["POST"])
def create_venue_api():
    try:
        data = request.get_json()
        print("\n--- 1. INCOMING FROM BROWSER ---")
        print(data)
        
        venue_name = data.get("venue_name")
        venue_type_id = data.get("venue_type") # This is now a UUID!
        location_id = data.get("location")     # This is now a UUID!
        description = data.get("description")
        floor = data.get("floor")
        room_number = data.get("room_number")
        capacity = data.get("capacity")
        facilities = data.get("facilities", []) # Array of objects with facility_id & quantity

        if not venue_name or not venue_type_id or not location_id:
            return jsonify({"success": False, "error": {"message": "Missing required fields"}}), 400

        # --- STEP 1: Insert Venue ---
        insert_data = {
            "name": venue_name,
            "venue_type_id": venue_type_id, # Updated column name
            "location_id": location_id,     # Updated column name
            "floor": floor,
            "room_number": room_number,
            "capacity": capacity,
            "description": description,
            "is_active": True,
            "booking_allowed": True
        }
        
        print("\n--- 2. SENDING VENUE TO SUPABASE ---")
        venue_response = supabase.table("venues").insert(insert_data).execute()
        
        # Grab the UUID of the venue we just created
        new_venue_id = venue_response.data[0]['id'] 

        # --- STEP 2: Insert into Bridge Table ---
        if facilities:
            print("\n--- 3. SENDING FACILITIES TO BRIDGE TABLE ---")
            bridge_data = []
            for item in facilities:
                bridge_data.append({
                    "venue_id": new_venue_id,
                    "facility_id": item['facility_id'],
                    "quantity": int(item['quantity'])
                })
            # Bulk insert all tags at once
            supabase.table("venue_facilities").insert(bridge_data).execute()

        print("\n--- 4. SUCCESS ---")
        return jsonify({"success": True, "message": "Venue created successfully"}), 201

    except Exception as e:
        print("\n--- ERROR CRASH  ---")
        print(e)
        return jsonify({"success": False, "error": {"message": str(e)}}), 500

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session.get("user")
    
    if request.method == "POST":
        updated_name = request.form.get("user_name")
        updated_phone = request.form.get("phone_number")
        updated_dept_id = request.form.get("department_id") # Changed to department_id
        
        try:
            supabase.table("users").update({
                "user_name": updated_name,
                "phone_number": updated_phone,
                "department_id": updated_dept_id # Saving to the new FK column
            }).eq("id", user_id).execute()
            
            session["user_name"] = updated_name
            flash("Profile updated successfully!", "success")
        except Exception as e:
            print("Error updating profile:", e)
            flash("Failed to update profile.", "error")
        return redirect(url_for("profile"))

    # GET Request
    try:
        user_record = supabase.table("users").select("*").eq("id", user_id).single().execute()
        dept_response = supabase.table("department").select("*").order("name").execute()
        
        return render_template("profile.html", user=user_record.data, departments=dept_response.data)
    except Exception as e:
        print("Error fetching profile:", e)
        return "Error loading profile."
    
@app.route("/cancel-event/<event_id>", methods=["POST"])
@login_required
def cancel_event(event_id):
    reason=request.form.get("reason")
    supabase.table("Events")\
        .update({"status": "Cancelled", "cancellation_reason": reason})\
        .eq("id", event_id)\
        .execute()
    return redirect(url_for("dashboard"))    

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