"""
Venue Booking System - Main Application
Flask backend connected to Neon PostgreSQL, Cloudinary, and SMTP Email Notifier
"""

import os
import json
import time
import uuid
from datetime import datetime, date
from functools import wraps
import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from flask.json.provider import DefaultJSONProvider
from dotenv import load_dotenv

import db
import mailer
import cloud_storage

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'venuebooking@123')


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json_provider_class = CustomJSONProvider
app.json = CustomJSONProvider(app)


# ==================== Security & Helper Decorators ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        user_exists = db.fetch_one("SELECT id FROM users WHERE id = %s AND is_active = true", (session["user"],))
        if not user_exists:
            session.clear()
            flash("Session expired or invalid user. Please log in again.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def pro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        user_exists = db.fetch_one("SELECT id FROM users WHERE id = %s AND is_active = true", (session["user"],))
        if not user_exists:
            session.clear()
            flash("Session expired. Please log in again.", "info")
            return redirect(url_for("login"))
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
        user_exists = db.fetch_one("SELECT id FROM users WHERE id = %s AND is_active = true", (session["user"],))
        if not user_exists:
            session.clear()
            flash("Session expired. Please log in again.", "info")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Access denied. Admin role required.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function


@app.template_filter('format_datetime')
def format_datetime(value, format='%b %d, %Y %I:%M %p'):
    if not value:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    try:
        dt = datetime.fromisoformat(str(value).replace('Z', ''))
        return dt.strftime(format)
    except Exception:
        return str(value)[:16]


@app.template_filter('format_date')
def format_date(value, format='%b %d, %Y'):
    if not value:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    try:
        dt = datetime.fromisoformat(str(value).replace('Z', ''))
        return dt.strftime(format)
    except Exception:
        return str(value)[:10]


@app.context_processor
def inject_base_template():
    role = session.get("role", "student")
    if role == "admin":
        base = "admin_base.html"
    elif role == "pro":
        base = "pro_base.html"
    elif role == "hod":
        base = "hod_base.html"
    else:
        base = "user_base.html"
    return dict(base_template=base)


# ==================== Auth Routes ====================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].lower().strip()
        password = request.form["password"]

        if not email.endswith("@saintgits.org"):
            flash("Only Saintgits email addresses (@saintgits.org) are allowed.", "error")
            return redirect(url_for("signup"))

        reserved_accounts = [
            "hodcse@saintgits.org", 
            "hodeee@saintgits.org", 
            "hodmech@saintgits.org",
            "hodcivil@saintgits.org",
            "hodit@saintgits.org",
            "pro@saintgits.org", 
            "admin@saintgits.org"
        ]

        if email in reserved_accounts:
            flash("This email address is reserved for system administrators and HODs.", "error")
            return redirect(url_for("signup"))

        existing_user = db.fetch_one("SELECT id FROM users WHERE email = %s", (email,))
        if existing_user:
            flash("An account with this email already exists. Please login.", "error")
            return redirect(url_for("signup"))

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db.execute_query(
            """
            INSERT INTO users (email, password_hash, user_name, role)
            VALUES (%s, %s, %s, 'student')
            """,
            (email, password_hash, name)
        )

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]

        user = db.fetch_one("SELECT * FROM users WHERE email = %s AND is_active = true", (email,))

        if user and user.get("password_hash"):
            if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                session["user"] = str(user["id"])
                session["email"] = user["email"]
                session["role"] = user["role"]
                session["user_name"] = user["user_name"]

                role = user["role"]
                if role == "hod":
                    return redirect(url_for("hod_dashboard"))
                elif role == "pro":
                    return redirect(url_for("pro_dashboard"))
                elif role == "admin":
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("dashboard"))

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
    events = db.fetch_all(
        "SELECT * FROM dashboard_events_view WHERE created_by = %s ORDER BY start_time DESC",
        (session["user"],)
    )
    return render_template("dashboard.html", events=events, user_name=session.get("user_name"))


# ==================== HOD Routes ====================

@app.route("/hod/dashboard")
@login_required
def hod_dashboard():
    user_id = session["user"]
    
    pending_events = db.fetch_all(
        "SELECT * FROM dashboard_events_view WHERE (assigned_to = %s OR assigned_to = %s) AND status = 'Pending' ORDER BY start_time ASC",
        (user_id, session.get("email"))
    )
    approved_events = db.fetch_all(
        "SELECT * FROM dashboard_events_view WHERE (assigned_to = %s OR assigned_to = %s) AND status = 'Approved' ORDER BY start_time DESC",
        (user_id, session.get("email"))
    )
    rejected_events = db.fetch_all(
        "SELECT * FROM dashboard_events_view WHERE (assigned_to = %s OR assigned_to = %s) AND status = 'Rejected' ORDER BY start_time DESC",
        (user_id, session.get("email"))
    )

    return render_template(
        "hod_dashboard.html",
        pending_events=pending_events,
        approved_events=approved_events,
        rejected_events=rejected_events,
        user_email=session.get("email")
    )


@app.route("/approve-event/<event_id>", methods=["POST"])
@login_required
def approve_event(event_id):
    db.execute_query(
        """
        UPDATE "Events" 
        SET status = 'Approved', approved_by = %s 
        WHERE id = %s
        """,
        (session["user"], event_id)
    )

    # Trigger Email Notification to Event Coordinator
    event = db.fetch_one(
        """
        SELECT e.title, v.name as venue_name, u.email as creator_email 
        FROM "Events" e 
        JOIN venues v ON e.venue_id = v.id 
        JOIN users u ON e.created_by = u.id 
        WHERE e.id = %s
        """,
        (event_id,)
    )
    if event:
        mailer.notify_status_update(event["creator_email"], event["title"], event["venue_name"], "Approved")

    flash("Event request approved.", "success")
    return redirect(url_for("hod_dashboard"))


@app.route("/reject-event/<event_id>", methods=["POST"])
@login_required
def reject_event(event_id):
    remark = request.form.get("remark", "")
    
    db.execute_query(
        """
        UPDATE "Events" 
        SET status = 'Rejected', approved_by = %s, rejection_reason = %s 
        WHERE id = %s
        """,
        (session["user"], remark, event_id)
    )

    # Trigger Email Notification to Event Coordinator
    event = db.fetch_one(
        """
        SELECT e.title, v.name as venue_name, u.email as creator_email 
        FROM "Events" e 
        JOIN venues v ON e.venue_id = v.id 
        JOIN users u ON e.created_by = u.id 
        WHERE e.id = %s
        """,
        (event_id,)
    )
    if event:
        mailer.notify_status_update(event["creator_email"], event["title"], event["venue_name"], "Rejected", remark)

    flash("Event request rejected.", "info")
    return redirect(url_for("hod_dashboard"))


# ==================== PRO Routes ====================

@app.route("/pro-dashboard")
@pro_required
def pro_dashboard():
    events = db.fetch_all("SELECT * FROM dashboard_events_view WHERE status != 'Cancelled' ORDER BY start_time ASC")
    return render_template("pro_dashboard.html", events=events, user_name=session.get("user_name"))


@app.route('/api/pro-calendar-events', methods=['GET'])
@pro_required
def get_pro_calendar_events():
    try:
        events = db.fetch_all("SELECT * FROM dashboard_events_view WHERE status != 'Cancelled'")
        formatted = []
        for item in events:
            pro_st = item.get('pro_status', 'Pending')
            colors = {'bg': '#059669', 'border': '#047857'} if pro_st == 'Approved' else {'bg': '#d97706', 'border': '#b45309'}
            
            start_val = item['start_time']
            end_val = item['end_time']
            start_str = start_val.isoformat() if hasattr(start_val, 'isoformat') else str(start_val)
            end_str = end_val.isoformat() if hasattr(end_val, 'isoformat') else str(end_val)

            formatted.append({
                'id': str(item['id']),
                'title': f"{item['title']} ({item.get('venue_name', 'Venue')})",
                'start': start_str,
                'end': end_str,
                'backgroundColor': colors['bg'],
                'borderColor': colors['border'],
                'extendedProps': {
                    'venue_name': item.get('venue_name'),
                    'club_name': item.get('club_name'),
                    'status': item.get('status'),
                    'pro_status': pro_st
                }
            })
        return jsonify(formatted), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pro-event/<event_id>', methods=['GET'])
@pro_required
def get_pro_event_detail(event_id):
    try:
        event = db.fetch_one("SELECT * FROM dashboard_events_view WHERE id = %s", (event_id,))
        facilities = db.fetch_all(
            """
            SELECT ef.requested_quantity, f.f_name as name 
            FROM event_facilities ef 
            JOIN facilities f ON ef.facility_id = f.id 
            WHERE ef.event_id = %s
            """,
            (event_id,)
        )
        if event:
            event['requested_facilities'] = facilities
            return jsonify(event), 200
        return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pro-event/<event_id>/respond', methods=['POST'])
@pro_required
def pro_respond_event(event_id):
    try:
        data = request.get_json()
        new_pro_status = data.get('pro_status')
        pro_remarks = data.get('pro_remarks', '')

        event = db.fetch_one("SELECT * FROM \"Events\" WHERE id = %s", (event_id,))
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        if event.get('assigned_to') == 'pro' or new_pro_status == 'Rejected':
            final_status = new_pro_status
        else:
            final_status = event.get('status', 'Pending')

        db.execute_query(
            """
            UPDATE "Events" 
            SET pro_status = %s, pro_remarks = %s, status = %s 
            WHERE id = %s
            """,
            (new_pro_status, pro_remarks, final_status, event_id)
        )

        if (final_status == 'Approved' or event.get('assigned_to') == 'pro') and new_pro_status == 'Approved':
            existing_booking = db.fetch_one("SELECT id FROM bookings WHERE event_id = %s", (event_id,))
            if not existing_booking:
                db.execute_query(
                    """
                    INSERT INTO bookings (event_id, venue_id, event_name, event_description, club_id, start_time, end_time, approval_letter_path, approved_by, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        event['id'], event['venue_id'], event['title'], event.get('description'),
                        event.get('club_id'), event['start_time'], event['end_time'],
                        event.get('permission_file_url'), session['user'], event['created_by']
                    )
                )

        creator = db.fetch_one("SELECT email FROM users WHERE id = %s", (event['created_by'],))
        venue = db.fetch_one("SELECT name FROM venues WHERE id = %s", (event['venue_id'],))
        if creator:
            mailer.notify_status_update(creator['email'], event['title'], venue['name'] if venue else 'Venue', new_pro_status, pro_remarks)

        return jsonify({'message': f'Event {new_pro_status} successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ==================== Admin Routes ====================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html", user_name=session.get("user_name"))


@app.route("/admin/users")
@admin_required
def admin_users():
    users = db.fetch_all("SELECT * FROM users ORDER BY created_at DESC")
    departments = db.fetch_all("SELECT id, name FROM department ORDER BY name ASC")
    return render_template("admin_users.html", users=users, departments=departments)


@app.route("/api/admin/users/add", methods=["POST"])
@admin_required
def api_add_user():
    data = request.json
    email = data.get("email").lower().strip()
    password = data.get("password")
    user_name = data.get("user_name")
    phone_number = data.get("contact_number")
    role = data.get("role")
    department_id = data.get("department")

    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_res = db.fetch_one(
            """
            INSERT INTO users (email, password_hash, user_name, phone_number, role, department_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (email, password_hash, user_name, phone_number, role, department_id if role in ['student', 'hod'] else None)
        )

        if role == "hod" and department_id:
            db.execute_query(
                "UPDATE department SET hod_name = %s, hod_id = %s WHERE id = %s",
                (user_name, user_res['id'], department_id)
            )

        return jsonify({"success": True, "message": "User created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/users/delete/<user_id>", methods=["DELETE"])
@admin_required
def api_delete_user(user_id):
    try:
        db.execute_query("UPDATE department SET hod_name = NULL, hod_id = NULL WHERE hod_id = %s", (user_id,))
        db.execute_query("DELETE FROM users WHERE id = %s", (user_id,))
        return jsonify({"success": True, "message": "User deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Event Creation & Venue Routing ====================

@app.route('/event')
@login_required
def event_page():
    return render_template('event.html')


@app.route('/api/events', methods=['POST'])
@login_required
def create_event():
    try:
        form_data = dict(request.form)
        title = form_data.get("title")
        description = form_data.get("description", "")
        start_time = form_data.get("start_time")
        end_time = form_data.get("end_time")
        faculty_coordinator = form_data.get("faculty_name") or form_data.get("faculty_coordinator")
        contact_number = form_data.get("phone") or form_data.get("contact_number")

        # Validate Date Range & Past Dates
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
                now_dt = datetime.now()
                
                if start_dt < now_dt:
                    return jsonify({"error": "Start date/time cannot be in the past!"}), 400
                if end_dt <= start_dt:
                    return jsonify({"error": "End date/time must be strictly after the start date/time!"}), 400
            except ValueError:
                pass

        # 1. Custom Event Type Handler
        event_type_id = form_data.get("event_type_id")
        if event_type_id == "other" and form_data.get("custom_event_type"):
            custom_type = form_data.get("custom_event_type").strip()
            type_res = db.fetch_one("SELECT id FROM event_types WHERE LOWER(event_type_name) = LOWER(%s)", (custom_type,))
            if not type_res:
                type_res = db.fetch_one("INSERT INTO event_types (event_type_name) VALUES (%s) RETURNING id", (custom_type,))
            event_type_id = str(type_res['id']) if type_res else None

        # 2. Custom Club Handler
        club_id = form_data.get("club_id")
        if club_id == "other" and form_data.get("custom_club_name"):
            custom_club = form_data.get("custom_club_name").strip()
            club_res = db.fetch_one("SELECT id FROM clubs WHERE LOWER(name) = LOWER(%s)", (custom_club,))
            if not club_res:
                club_res = db.fetch_one("INSERT INTO clubs (name, description) VALUES (%s, 'Custom Organization') RETURNING id", (custom_club,))
            club_id = str(club_res['id']) if club_res else None
        elif not club_id or club_id == "other":
            club_id = None

        # 3. Custom Venue Handler
        venue_id = form_data.get("venue_id")
        if venue_id == "other" and form_data.get("custom_venue_name"):
            custom_venue = form_data.get("custom_venue_name").strip()
            venue_res = db.fetch_one("SELECT id FROM venues WHERE LOWER(name) = LOWER(%s)", (custom_venue,))
            if not venue_res:
                venue_res = db.fetch_one("INSERT INTO venues (name, location, description) VALUES (%s, 'Custom Location', 'User specified venue') RETURNING id", (custom_venue,))
            venue_id = str(venue_res['id']) if venue_res else None

        if not venue_id or venue_id == "other":
            return jsonify({"error": "Please select or specify a valid venue"}), 400

        # Upload permission letter (Cloudinary / Local)
        permission_file = request.files.get('permission_file')
        file_url = cloud_storage.upload_permission_letter(permission_file) if permission_file else None

        # Dynamic Routing Rule Engine
        venue = db.fetch_one("SELECT name, department_id FROM venues WHERE id = %s", (venue_id,))
        assigned_to = "pro"
        approver_email = "pro@saintgits.org"

        if venue:
            venue_name = venue["name"].upper()
            if "RB" in venue_name:
                hod_user = db.fetch_one("SELECT id, email FROM users WHERE email = 'hodcse@saintgits.org'")
                assigned_to = str(hod_user['id']) if hod_user else "pro"
                approver_email = "hodcse@saintgits.org"
            elif "EEE" in venue_name:
                hod_user = db.fetch_one("SELECT id, email FROM users WHERE email = 'hodeee@saintgits.org'")
                assigned_to = str(hod_user['id']) if hod_user else "pro"
                approver_email = "hodeee@saintgits.org"
            elif "MECH" in venue_name:
                hod_user = db.fetch_one("SELECT id, email FROM users WHERE email = 'hodmech@saintgits.org'")
                assigned_to = str(hod_user['id']) if hod_user else "pro"
                approver_email = "hodmech@saintgits.org"
            elif "VB" in venue_name or "CIVIL" in venue_name:
                hod_user = db.fetch_one("SELECT id, email FROM users WHERE email = 'hodcivil@saintgits.org'")
                assigned_to = str(hod_user['id']) if hod_user else "pro"
                approver_email = "hodcivil@saintgits.org"
            elif "LAB" in venue_name or "IT" in venue_name:
                hod_user = db.fetch_one("SELECT id, email FROM users WHERE email = 'hodit@saintgits.org'")
                assigned_to = str(hod_user['id']) if hod_user else "pro"
                approver_email = "hodit@saintgits.org"

        # Insert Event
        event_res = db.fetch_one(
            """
            INSERT INTO "Events" (title, description, venue_id, club_id, event_type_id, start_time, end_time, faculty_coordinator, contact_number, permission_file_url, assigned_to, created_by, status, pro_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending', 'Pending')
            RETURNING id
            """,
            (title, description, venue_id, club_id, event_type_id, start_time, end_time, faculty_coordinator, contact_number, file_url, assigned_to, session["user"])
        )

        event_id = event_res['id']

        # Insert Facilities Payload
        if 'facilities_json' in form_data:
            facilities_list = json.loads(form_data['facilities_json'])
            for item in facilities_list:
                db.execute_query(
                    "INSERT INTO event_facilities (event_id, facility_id, requested_quantity) VALUES (%s, %s, %s)",
                    (event_id, item['id'], item['quantity'])
                )

        # Trigger Email Notifications
        user_name = session.get("user_name", "Event Coordinator")
        mailer.notify_new_booking(approver_email, title, venue['name'] if venue else 'Selected Venue', f"{start_time} to {end_time}", user_name)
        if approver_email != "pro@saintgits.org":
            mailer.notify_new_booking("pro@saintgits.org", title, venue['name'] if venue else 'Selected Venue', f"{start_time} to {end_time}", user_name)

        return jsonify({"message": "Event created successfully!", "event_id": str(event_id)}), 201
    except Exception as e:
        print("Create Event Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/cancel-event/<event_id>", methods=["POST"])
@login_required
def cancel_event(event_id):
    reason = request.form.get("reason", "No reason provided")
    
    event = db.fetch_one(
        """
        SELECT e.title, v.name as venue_name, e.assigned_to 
        FROM "Events" e 
        JOIN venues v ON e.venue_id = v.id 
        WHERE e.id = %s
        """,
        (event_id,)
    )

    db.execute_query(
        "UPDATE \"Events\" SET status = 'Cancelled', cancellation_reason = %s WHERE id = %s",
        (reason, event_id)
    )

    if event:
        mailer.notify_event_cancellation("pro@saintgits.org", event["title"], event["venue_name"], reason)

    flash("Event cancelled successfully.", "info")
    return redirect(url_for("dashboard"))


# ==================== APIs & General Routes ====================

@app.route("/venue", methods=['GET'])
def venue():
    locations = db.fetch_all("SELECT * FROM location ORDER BY name ASC")
    types = db.fetch_all("SELECT * FROM venue_type ORDER BY type_name ASC")
    facilities = db.fetch_all("SELECT * FROM facilities ORDER BY f_name ASC")
    return render_template("venue.html", locations=locations, venue_types=types, facilities=facilities)


@app.route('/api/calendar-events', methods=['GET'])
def get_calendar_events():
    try:
        events = db.fetch_all("SELECT * FROM events_view")
        formatted = []
        for i in events:
            formatted.append({
                'id': str(i['id']),
                'title': f"{i['title']} ({i['venue_name']})",
                'start': str(i['start_time']),
                'end': str(i['end_time']),
                'backgroundColor': '#2563eb',
                'borderColor': '#1d4ed8'
            })
        return jsonify(formatted), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/event-types', methods=['GET'])
def get_event_types():
    try:
        types = db.fetch_all("SELECT id, event_type_name AS name FROM event_types ORDER BY event_type_name ASC")
        return jsonify(types), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clubs', methods=['GET'])
def get_clubs():
    clubs = db.fetch_all("SELECT id, name FROM clubs ORDER BY name ASC")
    return jsonify(clubs), 200


@app.route('/api/venues', methods=['GET'])
def get_venues():
    venues = db.fetch_all("SELECT id, name FROM venues WHERE is_active = true ORDER BY name ASC")
    return jsonify(venues), 200


@app.route('/api/facilities/all', methods=['GET'])
def get_all_facilities():
    try:
        facilities = db.fetch_all("SELECT id, f_name as name FROM facilities ORDER BY f_name ASC")
        return jsonify(facilities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/facilities/<venue_id>', methods=['GET'])
def get_facilities_for_venue(venue_id):
    try:
        facilities = db.fetch_all(
            """
            SELECT vf.quantity, f.id, f.f_name as name 
            FROM venue_facilities vf 
            JOIN facilities f ON vf.facility_id = f.id 
            WHERE vf.venue_id = %s
            """,
            (venue_id,)
        )
        return jsonify(facilities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", 5000)),
        debug=(os.getenv("APP_ENV") == "development")
    )