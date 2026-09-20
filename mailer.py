"""
Email Notification Module for Venue Booking System
Handles sending automated emails to HODs, PRO, and Event Coordinators
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)


def send_email(to_email, subject, body_html):
    """
    Send an email via SMTP.
    Fails gracefully without crashing the app if mail credentials are not set.
    """
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        try:
            print(f"[MAIL NOTICE] Mail credentials not set. Skipping email to {to_email} with subject: '{subject}'")
        except Exception:
            print(f"[MAIL NOTICE] Mail credentials not set. Skipping email to {to_email}")
        return False
        
    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = MAIL_DEFAULT_SENDER
        msg['To'] = to_email
        
        part = MIMEText(body_html, "html", "utf-8")
        msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_DEFAULT_SENDER, [to_email], msg.as_string())
        server.quit()
        print(f"[MAIL SUCCESS] Email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"[MAIL ERROR] Failed to send email to {to_email}: {e}")
        return False


def notify_new_booking(to_email, event_title, venue_name, event_date, coordinator_name):
    """Notify HOD or PRO of a new booking request waiting for approval"""
    subject = f"Action Required: New Booking Request for {venue_name}"
    body = f"""
    <h2>New Venue Booking Request</h2>
    <p>Dear Approving Authority,</p>
    <p>A new event booking request has been submitted and is awaiting your review:</p>
    <ul>
        <li><strong>Event Name:</strong> {event_title}</li>
        <li><strong>Venue:</strong> {venue_name}</li>
        <li><strong>Date/Time:</strong> {event_date}</li>
        <li><strong>Submitted By:</strong> {coordinator_name}</li>
    </ul>
    <p>Please log in to the <strong>Venue Booking Portal</strong> to review and respond to this request.</p>
    <br>
    <p><em>Saintgits Venue Booking System</em></p>
    """
    return send_email(to_email, subject, body)


def notify_status_update(to_email, event_title, venue_name, status, remarks=None):
    """Notify Event Coordinator when their booking request is Approved or Rejected"""
    color = "#059669" if status.lower() == "approved" else "#dc2626"
    subject = f"Venue Booking Update: {event_title} is {status.upper()}"
    
    remark_html = f"<p><strong>Remarks:</strong> {remarks}</p>" if remarks else ""
    
    body = f"""
    <h2>Booking Status Update</h2>
    <p>Your booking request for <strong>{event_title}</strong> at <strong>{venue_name}</strong> has been updated:</p>
    <h3 style="color: {color};">Status: {status.upper()}</h3>
    {remark_html}
    <p>Log in to your dashboard for full details.</p>
    <br>
    <p><em>Saintgits Venue Booking System</em></p>
    """
    return send_email(to_email, subject, body)


def notify_event_cancellation(to_email, event_title, venue_name, reason):
    """Notify PRO and HOD when an event is cancelled by the coordinator"""
    subject = f"Event Cancelled: {event_title} ({venue_name})"
    body = f"""
    <h2>Event Cancellation Notice</h2>
    <p>The following event has been cancelled by the coordinator:</p>
    <ul>
        <li><strong>Event Title:</strong> {event_title}</li>
        <li><strong>Venue:</strong> {venue_name}</li>
        <li><strong>Cancellation Reason:</strong> {reason}</li>
    </ul>
    <p>The venue slot has been automatically freed on the central calendar.</p>
    <br>
    <p><em>Saintgits Venue Booking System</em></p>
    """
    return send_email(to_email, subject, body)
