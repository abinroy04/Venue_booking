"""
Create User Script
Helper script to create users with different roles for Venue Booking System

Usage:
    python create_user.py
    
Then follow the prompts to create a new user.
"""

import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client with SERVICE role key (bypasses RLS for admin operations)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")
    print("💡 Tip: This script requires the service role key to bypass Row Level Security")
    print("   Add SUPABASE_SERVICE_KEY to your .env file (found in Supabase Project Settings > API)")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def get_user_by_email(email):
    """Check if email already exists"""
    try:
        response = supabase.table('users').select('id, email').eq('email', email).execute()
        return response.data[0] if response.data and len(response.data) > 0 else None
    except Exception as e:
        print(f"Error checking email: {e}")
        return None


def create_user(email, password, user_name, role, department=None, phone_number=None):
    """
    Create a new user
    
    Args:
        email: User's email (unique)
        password: Plain text password
        user_name: User's full name
        role: User role ('student', 'hod', 'principal', 'pro', 'admin')
        department: User's department (optional)
        phone_number: User's phone number (optional)
    
    Returns:
        New user ID (UUID) or None if failed
    """
    # Check if email already exists
    if get_user_by_email(email):
        print(f"❌ Email {email} already exists")
        return None
    
    # Validate role
    valid_roles = ['student', 'hod', 'principal', 'pro', 'admin']
    if role not in valid_roles:
        print(f"❌ Invalid role: {role}. Must be one of {valid_roles}")
        return None
    
    # Hash password
    password_hash = hash_password(password)
    
    try:
        # Insert new user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'user_name': user_name,
            'role': role,
            'department': department,
            'phone_number': phone_number,
            'is_active': True
        }
        
        response = supabase.table('users').insert(user_data).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['id']
        return None
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def get_all_users():
    """Get all users from database"""
    try:
        response = supabase.table('users').select(
            'id, email, user_name, role, department, phone_number, is_active, created_at'
        ).order('created_at', desc=True).execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return []


def create_user_interactive(email, password, user_name, role, department=None, phone_number=None):
    """
    Create a new user in the database
    
    Args:
        email: Unique email for login
        password: Plain text password (will be hashed)
        user_name: User's full name
        role: 'student', 'hod', 'principal', 'pro', or 'admin'
        department: User's department (optional)
        phone_number: User's phone number (optional)
    
    Returns:
        User ID if successful, None otherwise
    """
    try:
        user_id = create_user(email, password, user_name, role, department, phone_number)
        
        if user_id:
            print(f"✅ User '{email}' created successfully!")
            print(f"   User ID: {user_id}")
            print(f"   Name: {user_name}")
            print(f"   Role: {role}")
            if department:
                print(f"   Department: {department}")
            if phone_number:
                print(f"   Phone: {phone_number}")
            return user_id
        else:
            print(f"❌ Error: Could not create user. Email may already exist.")
            return None
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def list_users():
    """List all users in the system"""
    try:
        users = get_all_users()
        
        if users:
            print("\n" + "="*100)
            print("EXISTING USERS")
            print("="*100)
            print(f"{'Email':<30} {'Name':<25} {'Role':<12} {'Department':<20} {'Active':<8}")
            print("-"*100)
            for user in users:
                email = user.get('email', '')[:29]
                name = user.get('user_name', '')[:24]
                role = user.get('role', '')
                dept = (user.get('department') or '')[:19]
                active = '✓' if user.get('is_active') else '✗'
                print(f"{email:<30} {name:<25} {role:<12} {dept:<20} {active:<8}")
            print("="*100 + "\n")
        else:
            print("\n⚠️  No users found in database\n")
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")


def interactive_create():
    """Interactive user creation"""
    print("\n" + "="*60)
    print("CREATE NEW USER - VENUE BOOKING SYSTEM")
    print("="*60)
    
    # Get email
    while True:
        email = input("\nEmail: ").strip().lower()
        if not email:
            print("❌ Email cannot be empty!")
            continue
        if '@' not in email:
            print("❌ Invalid email format!")
            continue
        break
    
    # Get password
    while True:
        password = input("Password: ").strip()
        if not password:
            print("❌ Password cannot be empty!")
            continue
        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            continue
        
        confirm_password = input("Confirm Password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match!")
            continue
        break
    
    # Get full name
    while True:
        user_name = input("Full Name: ").strip()
        if not user_name:
            print("❌ Name cannot be empty!")
            continue
        break
    
    # Get role
    print("\nUser Roles:")
    print("  1. Student    - Read-only access to public calendar")
    print("  2. HOD        - Can create booking requests")
    print("  3. Principal  - Can approve booking requests")
    print("  4. PRO        - Can confirm bookings and manage venues")
    print("  5. Admin      - Full system access")
    
    while True:
        choice = input("\nSelect role (1-5): ").strip()
        if choice == '1':
            role = 'student'
            break
        elif choice == '2':
            role = 'hod'
            break
        elif choice == '3':
            role = 'principal'
            break
        elif choice == '4':
            role = 'pro'
            break
        elif choice == '5':
            role = 'admin'
            break
        else:
            print("❌ Invalid choice! Please select 1-5.")
    
    # Get department (optional)
    department = input("\nDepartment (optional, press Enter to skip): ").strip()
    if not department:
        department = None
    
    # Get phone number (optional)
    phone_number = input("Phone Number (optional, press Enter to skip): ").strip()
    if not phone_number:
        phone_number = None
    
    # Confirm
    print("\n" + "-"*60)
    print("REVIEW USER DETAILS:")
    print(f"  Email: {email}")
    print(f"  Name: {user_name}")
    print(f"  Role: {role}")
    if department:
        print(f"  Department: {department}")
    if phone_number:
        print(f"  Phone: {phone_number}")
    print("-"*60)
    
    confirm = input("\nCreate this user? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        create_user_interactive(email, password, user_name, role, department, phone_number)
    else:
        print("❌ User creation cancelled.")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("VENUE BOOKING SYSTEM - USER MANAGEMENT")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. Create new user")
        print("  2. List existing users")
        print("  3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            interactive_create()
        elif choice == '2':
            list_users()
        elif choice == '3':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice! Please select 1, 2, or 3.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
