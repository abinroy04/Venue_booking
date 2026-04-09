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

            print("FULL RESPONSE:", response)

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
            return f"❌ Error: {str(e)}"   # 🔥 SHOW ERROR IN BROWSER

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