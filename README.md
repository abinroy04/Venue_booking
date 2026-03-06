# Venue Booking System

A comprehensive venue booking management system designed for educational institutions, featuring role-based access control, conflict prevention, and transparent tracking of venue bookings.

## 🎯 Overview

This system digitizes the venue booking process while maintaining institutional approval protocols. It provides read-only calendar access to students while giving authorized personnel (HOD/PRO) full booking control with conflict detection and audit logging.

## 📁 Project Structure

```
Venue_Booking/
├── app.py                      # Main application file
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
├── database/
│   └── schema.sql              # Complete database schema
├── docs/
│   ├── DATABASE_SCHEMA.md      # Schema documentation
│   ├── ER_DIAGRAM.md           # Entity relationship diagram
│   ├── SETUP_GUIDE.md          # Setup instructions
│   └── Venue_Booking_System_FRD.docx  # Functional requirements
├── static/                     # Static assets (CSS, JS, images)
├── templates/                  # HTML templates
└── myenv/                      # Python virtual environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- A Supabase account
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Venue_Booking
```

2. **Set up virtual environment**
```bash
python -m venv myenv
# On Windows:
myenv\Scripts\activate
# On macOS/Linux:
source myenv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
APP_SECRET_KEY=your-secret-key
APP_ENV=development
```

5. **Set up the database**

Follow the detailed instructions in [SETUP_GUIDE.md](docs/SETUP_GUIDE.md):
- Create a Supabase project
- Run `database/schema.sql` in SQL Editor
- Configure authentication
- Set up storage bucket

6. **Run the application**
```bash
python app.py
```

## 🔐 Security Features

### Row Level Security (RLS)
- All tables protected with RLS policies
- Enforced at database level
- Automatic with Supabase Auth

### Access Control
- Students: Read-only access to confirmed bookings
- Authorized Personnel: Full CRUD operations
- Audit trail for all actions

### Data Protection
- Encrypted connections (SSL/TLS)
- Secure password hashing
- Environment variable protection
- Private storage for approval letters

## 🔄 Booking Workflow

```
1. Student checks availability (read-only)
   ↓
2. Student prepares approval letter
   ↓
3. HOD/Principal reviews and approves (offline)
   ↓
4. HOD creates booking request (status: pending)
   ↓
5. Principal approves (status: approved)
   ↓
6. PRO confirms and blocks slot (status: confirmed)
   ↓
7. Calendar updates for all users
```