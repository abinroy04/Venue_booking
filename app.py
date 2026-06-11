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
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if SERVICE_KEY:
    service_supabase: Client = create_client(SUPABASE_URL, SERVICE_KEY)


# ==================== Security Decorators ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def pro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
            
        # GOD MODE: Allow PRO and Admin
        if session.get("role") not in ["pro", "admin"]:
            flash("Access denied. PRO role required.", "error")
            return redirect(url_for("index"))
            
        return f(*args, **kwargs)
    return decorated_function
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Access denied. Admin role required.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function


# ==================== Auth Routes ====================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        
        if not email.endswith("@saintgits.org"):
            flash("Only Saintgits email addresses are allowed.", "error")
            return redirect(url_for("signup"))
            
        reserved_accounts = [
            "hodcse@saintgits.org", 
            "hodeee@saintgits.org", 
            "pro@saintgits.org", 
            "admin@saintgits.org"
        ]
        
        if email in reserved_accounts:
            flash("This email address is reserved for specific users.", "error")
            return redirect(url_for("signup"))
            
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                supabase.table("users").insert({
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_name": name,
                    "role": "student",
                    "is_active": True
                }).execute()
                
                return redirect(url_for("login"))

        except Exception as e:
            error = str(e)
            if "already exists" in error.lower() or "already registered" in error.lower():
                flash("An account with this email already exists. Please login.", "error")
            else:
                flash("Something went wrong. Please try again.", "error")
            return redirect(url_for("signup"))
            
    return render_template("signup.html")

@app.context_processor
def inject_base_template():
    # Default to user_base if not logged in or not defined
    role = session.get("role", "student")
    
    if role == "admin":
        base = "admin_base.html"
    elif role == "pro":
        base = "pro_base.html"
    elif role.startswith("hod"):
        base = "hod_base.html"
    else:
        base = "user_base.html"
        
    return dict(base_template=base)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                session["user"] = response.user.id
                session["email"] = response.user.email
                
                user_record = (
                    supabase.table("users")
                    .select("*")
                    .eq("id", response.user.id)
                    .single()
                    .execute()
                )
                
                session["role"] = user_record.data["role"]
                session["user_name"] = user_record.data["user_name"]
                
                role = session["role"]
                
                # --- MERGED ROUTING LOGIC ---
                if role.startswith("hod"):
                    return redirect(url_for("hod_dashboard"))
                elif role == "pro":
                    return redirect(url_for("pro_dashboard"))
                elif role == "admin":
                    return redirect(url_for("admin_dashboard")) 
                else:
                    return redirect(url_for("dashboard"))
                    
        except Exception as e:
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== Core Dashboards ====================
@app.route("/")
def index():
    return render_template("index.html")

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


# ==================== HOD Routes ====================
@app.route("/hod/dashboard")
@login_required
def hod_dashboard():
    pending_events = (
        supabase.table("Events")
        .select("*")
        .eq("assigned_to", session["user"])
        .eq("status", "Pending")
        .execute()
    )
    
    approved_events = (
        supabase.table("Events")
        .select("*")
        .eq("assigned_to", session["user"])
        .eq("status", "Approved")
        .execute()
    )
    
    rejected_events = (
        supabase.table("Events")
        .select("*")
        .eq("assigned_to", session["user"])
        .eq("status", "Rejected")
        .execute()
    )

    return render_template(
        "hod_dashboard.html",
        pending_events=pending_events.data,
        approved_events=approved_events.data,
        rejected_events=rejected_events.data,
        user_email=session["email"]
    )
    
@app.route("/approve-event/<event_id>", methods=["POST"])
@login_required
def approve_event(event_id):
    (
        supabase.table("Events")
        .update({
            "status": "Approved",
            "approved_by": session["user"]
        })
        .eq("id", event_id)
        .execute()
    )
    return redirect(url_for("hod_dashboard"))

@app.route("/reject-event/<event_id>", methods=["POST"])
@login_required
def reject_event(event_id):
    remark = request.form.get("remark")
    
    (
        supabase.table("Events")
        .update({
            "status": "Rejected",
            "approved_by": session["user"],
            "rejection_reason": remark
        })
        .eq("id", event_id)
        .execute()
    )
    return redirect(url_for("hod_dashboard"))


# ==================== PRO Routes ====================
@app.route("/pro-dashboard")
@pro_required
def pro_dashboard():
    events = (
        supabase.table("dashboard_events_view")
        .select("*")
        .neq("status", "Cancelled")
        .order("start_time")
        .execute()
    )
    return render_template(
        "pro_dashboard.html", 
        events=events.data, 
        user_name=session.get("user_name")
    )

@app.route('/api/pro-calendar-events', methods=['GET'])
@pro_required
def get_pro_calendar_events():
    try:
        response = (
            supabase.table('dashboard_events_view')
            .select('id, title, start_time, end_time, venue_name, club_name, status, pro_status, assigned_to')
            .neq('status', 'Cancelled')
            .execute()
        )
        
        color_map = {
            'Approved': {'bg': '#059669', 'border': '#047857'}, 
            'Rejected': {'bg': '#dc2626', 'border': '#b91c1c'}
        }
        default_color = {'bg': '#d97706', 'border': '#b45309'}
        
        formatted = []
        for item in response.data:
            pro_st = item.get('pro_status', 'Pending')
            colors = color_map.get(pro_st, default_color)
            
            formatted.append({
                'id': item['id'],
                'title': f"{item['title']} ({item['venue_name']})",
                'start': item['start_time'],
                'end': item['end_time'],
                'backgroundColor': colors['bg'],
                'borderColor': colors['border'],
                'extendedProps': {
                    'venue_name': item.get('venue_name'),
                    'club_name': item.get('club_name'),
                    'status': item.get('status'),
                    'pro_status': pro_st,
                    'assigned_to': item.get('assigned_to'),
                }
            })
            
        return jsonify(formatted), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pro-event/<event_id>', methods=['GET'])
@pro_required
def get_pro_event_detail(event_id):
    try:
        event = (
            supabase.table('dashboard_events_view')
            .select('*')
            .eq('id', event_id)
            .single()
            .execute()
        )
        
        facilities = (
            supabase.table('event_facilities')
            .select('requested_quantity, facilities(id, f_name)')
            .eq('event_id', event_id)
            .execute()
        )
        
        fac_list = []
        for f in facilities.data:
            if f.get('facilities'):
                fac_list.append({
                    'name': f['facilities']['f_name'], 
                    'requested_quantity': f['requested_quantity']
                })
                
        result = event.data
        result['requested_facilities'] = fac_list
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pro-event/<event_id>/respond', methods=['POST'])
@pro_required
def pro_respond_event(event_id):
    try:
        data = request.get_json()
        new_pro_status = data.get('pro_status')
        pro_remarks = data.get('pro_remarks', '')

        if new_pro_status not in ['Approved', 'Rejected']:
            return jsonify({'error': 'Invalid pro_status value'}), 400

        event = (
            supabase.table('dashboard_events_view')
            .select('assigned_to, status')
            .eq('id', event_id)
            .single()
            .execute()
        )
        
        update_payload = {
            'pro_status': new_pro_status, 
            'pro_remarks': pro_remarks
        }

        if event.data.get('assigned_to') == 'pro':
            update_payload['status'] = new_pro_status

        (
            supabase.table('Events')
            .update(update_payload)
            .eq('id', event_id)
            .execute()
        )
        
        return jsonify({'message': 'Response submitted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ==================== Admin Routes ====================
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    # This is the new home page with the Calendar and Grid
    return render_template("admin_dashboard.html", user_name=session.get("user_name"))

@app.route("/admin/users")
@admin_required
def admin_users():
    # We moved the User table here!
    users_response = supabase.table("users").select("*").order("created_at", desc=True).execute()
    return render_template(
        "admin_users.html", 
        users=users_response.data,
        user_name=session.get("user_name")
    )

    try:
        # 1. Create the user in Supabase Authentication Vault using God Mode key
        auth_response = service_supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        new_user_id = auth_response.user.id

        # 2. Add their profile to our public users table
        supabase.table("users").insert({
            "id": new_user_id,
            "email": email,
            "user_name": user_name,
            "role": role,
            "is_active": True
        }).execute()

        # 3. Auto-link HOD to their Department!
        if role.startswith("hod_"):
            department_mapping = {
                "hod_cse": "Computer Science (CSE)",
                "hod_eee": "Electrical & Electronics (EEE)",
                "hod_ce":  "Civil Engineering (CE)",
                "hod_me":  "Mechanical Engineering (ME)",
                "hod_ece": "Electronics & Communication (ECE)",
                "hod_ra":  "Robotics & Automation (RA)"
            }
            target_dept_name = department_mapping.get(role)
            if target_dept_name:
                supabase.table("department").update({
                    "hod_name": role,
                    "hod_id": new_user_id
                }).eq("name", target_dept_name).execute()

        flash(f"User {user_name} created successfully!", "success")
        
    except Exception as e:
        print("Error creating user:", e)
        flash(f"Failed to create user. They might already exist.", "error")
        
    return redirect(url_for("admin_dashboard"))


# ==================== Creation Routes ====================
@app.route('/event')
@login_required
def event_page():
    return render_template('event.html')

@app.route('/api/events', methods=['POST'])
@login_required
def create_event():
    try:
        data = dict(request.form)
        data["created_by"] = session["user"]

        # Parse Facilities
        facilities_to_insert = []
        if 'facilities_json' in data:
            facilities_list = json.loads(data['facilities_json'])
            for item in facilities_list:
                facilities_to_insert.append({
                    "facility_id": item['id'], 
                    "requested_quantity": item['quantity']
                })
            data.pop('facilities_json', None)

        # Handle File Upload
        permission_file = request.files.get('permission_file')
        if permission_file and permission_file.filename:
            original_filename = secure_filename(permission_file.filename)
            unique_filename = f"{int(time.time())}_{original_filename}"
            file_bytes = permission_file.read()
            
            (
                service_supabase.storage.from_('approved_letters')
                .upload(
                    file=file_bytes, 
                    path=unique_filename, 
                    file_options={"content-type": permission_file.content_type}
                )
            )
            
            data['permission_file_url'] = (
                service_supabase.storage.from_('approved_letters')
                .get_public_url(unique_filename)
            )

        # Dynamic HOD Assignment
        venue_id = data.get("venue_id")
        venue_response = (
            supabase.table("venues")
            .select("hod_id")
            .eq("id", venue_id)
            .single()
            .execute()
        )
        
        if venue_response.data and venue_response.data.get("hod_id"):
            data["assigned_to"] = venue_response.data["hod_id"]
        else:
            data["assigned_to"] = "pro"

        data["status"] = "Pending"
        data["pro_status"] = "Pending"

        # Insert Event
        event_response = (
            supabase.table("Events")
            .insert(data)
            .execute()
        )
        
        new_event_id = event_response.data[0]["id"]

        # Insert Facilities
        if facilities_to_insert:
            for facility in facilities_to_insert:
                facility["event_id"] = new_event_id
                
            (
                supabase.table("event_facilities")
                .insert(facilities_to_insert)
                .execute()
            )

        return jsonify({
            "message": "Event created successfully!", 
            "data": event_response.data
        }), 201

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# ==================== Venue Routes ====================
@app.route("/venue", methods=['GET'])
def venue():
    locations_response = supabase.table("location").select("*").execute()
    types_response = supabase.table("venue_type").select("*").execute()
    facilities_response = supabase.table("facilities").select("*").execute()
    
    return render_template(
        "venue.html", 
        locations=locations_response.data, 
        venue_types=types_response.data, 
        facilities=facilities_response.data
    )

@app.route("/venues", methods=["POST"])
def create_venue_api():
    try:
        data = request.get_json()
        
        insert_data = {
            "name": data.get("venue_name"),
            "venue_type_id": data.get("venue_type"),
            "location_id": data.get("location"),
            "floor": data.get("floor"),
            "room_number": data.get("room_number"),
            "capacity": data.get("capacity"),
            "description": data.get("description"),
            "is_active": True,
            "booking_allowed": True
        }
        
        venue_response = (
            supabase.table("venues")
            .insert(insert_data)
            .execute()
        )
        
        new_venue_id = venue_response.data[0]['id'] 

        facilities = data.get("facilities", [])
        if facilities:
            bridge_data = []
            for item in facilities:
                bridge_data.append({
                    "venue_id": new_venue_id, 
                    "facility_id": item['facility_id'], 
                    "quantity": int(item['quantity'])
                })
                
            (
                supabase.table("venue_facilities")
                .insert(bridge_data)
                .execute()
            )

        return jsonify({
            "success": True, 
            "message": "Venue created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": {"message": str(e)}
        }), 500


# ==================== APIs & Utilities ====================
@app.route('/api/calendar-events', methods=['GET'])
def get_calendar_events():
    try:
        response = (
            supabase.table('events_view')
            .select('id, title, start_time, end_time, venue_name')
            .execute()
        )
        
        formatted = []
        for i in response.data:
            formatted.append({
                'id': i['id'], 
                'title': f"{i['title']} ({i['venue_name']})", 
                'start': i['start_time'], 
                'end': i['end_time'], 
                'backgroundColor': '#2563eb', 
                'borderColor': '#1d4ed8'
            })
            
        return jsonify(formatted), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    response = supabase.table('clubs').select('id, name').execute()
    return jsonify(response.data), 200

@app.route('/api/venues', methods=['GET'])
def get_venues():
    response = supabase.table('venues').select('id, name').execute()
    return jsonify(response.data), 200

@app.route('/api/event-types', methods=['GET'])
def get_event_types():
    response = supabase.table('event_types').select('id, event_type_name').execute()
    
    data = []
    for i in response.data:
        data.append({
            'id': i['id'], 
            'name': i['event_type_name']
        })
        
    return jsonify(data), 200

@app.route('/api/facilities/<venue_id>', methods=['GET'])
def get_facilities_for_venue(venue_id):
    try:
        response = (
            supabase.table('venue_facilities')
            .select('facility_id, quantity, facilities(id, f_name)')
            .eq('venue_id', venue_id)
            .execute()
        )
        
        data = []
        for i in response.data:
            if i.get('facilities'):
                data.append({
                    'id': i['facilities']['id'], 
                    'name': i['facilities']['f_name'], 
                    'max_quantity': i['quantity']
                })
                
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/cancel-event/<event_id>", methods=["POST"])
@login_required
def cancel_event(event_id):
    (
        supabase.table("Events")
        .update({
            "status": "Cancelled", 
            "cancellation_reason": request.form.get("reason")
        })
        .eq("id", event_id)
        .execute()
    )
    return redirect(url_for("dashboard"))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        try:
            (
                supabase.table("users")
                .update({
                    "user_name": request.form.get("user_name"), 
                    "phone_number": request.form.get("phone_number"), 
                    "department_id": request.form.get("department_id")
                })
                .eq("id", session.get("user"))
                .execute()
            )
            session["user_name"] = request.form.get("user_name")
            flash("Profile updated successfully!", "success")
            
        except Exception as e:
            flash("Failed to update profile.", "error")
            
        return redirect(url_for("profile"))

    user_record = (
        supabase.table("users")
        .select("*")
        .eq("id", session.get("user"))
        .single()
        .execute()
    )
    
    dept_response = (
        supabase.table("department")
        .select("*")
        .order("name")
        .execute()
    )
    
    return render_template(
        "profile.html", 
        user=user_record.data, 
        departments=dept_response.data
    )

@app.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        try:
            supabase.auth.reset_password_for_email(request.form["email"].strip().lower())
            flash("Password reset email sent.", "success")
        except Exception as e:
            flash("Unable to send reset email. Please try again.", "error")
            
        return redirect(url_for("forget_password"))
        
    return render_template("forget_password.html")

@app.route("/calendar-redirect")
def calendar_redirect():
    # If not logged in, send them to the homepage calendar
    if "user" not in session:
        return redirect("/#calendar-section")
        
    role = session.get("role", "student")
    
    # Staff go to their respective dashboards
    if role.startswith("hod"):
        return redirect(url_for("hod_dashboard"))
    elif role == "pro":
        return redirect(url_for("pro_dashboard"))
    elif role == "admin":
        return redirect(url_for("admin_dashboard"))
    else:
        # Students/Normal users go to the homepage calendar
        return redirect("/#calendar-section")
if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", 5000)),
        debug=(os.getenv("APP_ENV") == "development"),
        use_reloader=(os.getenv("APP_ENV") == "development"),
        threaded=True
    )