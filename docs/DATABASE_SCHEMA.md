# Database Schema Documentation
## Venue Booking System

### Overview
This database schema is designed for Supabase (PostgreSQL) and implements a comprehensive venue booking system with role-based access control, conflict prevention, and audit logging.

---

## Database Design

### Core Tables

#### 1. **users**
Stores all system users with role-based access control.

**Roles:**
- `student` - Read-only access to view bookings
- `hod` - Head of Department, can approve and create booking requests
- `principal` - Can approve booking requests
- `pro` - Public Relations Officer, full booking control
- `admin` - Full system access

**Key Fields:**
- `email` - Unique identifier and login credential
- `role` - Determines access permissions
- `department` - User's department affiliation

#### 2. **venues**
Central database of all bookable spaces.

**Venue Types:**
- Seminar halls
- Labs
- Auditoriums
- Classrooms
- Sports facilities
- Other

**Key Fields:**
- `capacity` - Maximum number of people
- `facilities` - Array of available amenities (projector, AC, etc.)
- `is_active` - Controls visibility
- `booking_allowed` - Controls whether venue can be booked

#### 3. **venue_items**
Individual items/components within venues that can be booked.

**Examples:**
- Microphones
- Laptops
- Projectors
- Sound systems

**Key Fields:**
- `quantity` - Total available items
- `is_bookable` - Whether item can be independently requested

#### 4. **bookings**
The main booking records with complete workflow support.

**Booking Status Flow:**
1. `pending` - Initial state after creation
2. `approved` - Approved by HOD/Principal after letter review
3. `confirmed` - Digitally blocked by PRO
4. `cancelled` - Booking cancelled
5. `rejected` - Approval denied

**Key Fields:**
- `booking_date`, `start_time`, `end_time` - Scheduling information
- `approval_letter_path` - Reference to uploaded approval document
- `created_by` - Who created the booking (PRO/HOD)
- `approved_by` - Who approved the booking
- `special_requirements` - Public notes
- `internal_notes` - Private notes for authorized personnel only

#### 5. **booking_items**
Junction table linking bookings to venue items.

Tracks which items are requested and allocated for each booking.

#### 6. **clubs**
Centralized database of institutional clubs and organizations.

**Key Fields:**
- `name` - Club name
- `description` - Club purpose and activities
- `email` - Official club contact

#### 7. **club_coordinators**
Maps users to clubs with specific roles.

**Features:**
- Time-bounded assignments (`assigned_from`, `assigned_until`)
- Multiple coordinators per club
- Role specification (president, secretary, etc.)

#### 8. **booking_audit_log**
Complete audit trail of all booking actions.

**Logged Actions:**
- Creation
- Updates
- Status changes
- Approvals
- Cancellations

Stores both old and new values in JSONB format for complete history.

---

## Key Features

### 1. Conflict Prevention
The `check_booking_conflict()` function automatically detects overlapping bookings:
- Same venue
- Same date
- Overlapping time ranges

### 2. Audit Logging
Automatic triggers log all booking changes:
- Who made the change
- When it was made
- What changed (before/after values)

### 3. Row Level Security (RLS)
Supabase RLS policies enforce access control:
- Students can only view confirmed bookings
- Authorized personnel have full access
- Automatic enforcement at database level

### 4. Calendar Views

**calendar_view**: Public-facing calendar showing confirmed bookings
- Read-only access for students
- Shows essential booking information
- Filters only confirmed/approved bookings

**booking_details**: Comprehensive booking information
- Includes venue details
- Shows booked items
- Displays approval chain
- For authorized users only

**venue_availability**: Quick overview of venue usage
- Shows upcoming booking counts
- Helps in venue selection
- Only active, bookable venues

---

## Usage Examples

### Check for Booking Conflicts
```sql
SELECT check_booking_conflict(
    'venue-uuid'::UUID,
    '2026-03-15'::DATE,
    '10:00:00'::TIME,
    '12:00:00'::TIME
);
-- Returns true if conflict exists, false if slot is available
```

### View Calendar (Student Access)
```sql
SELECT * FROM calendar_view
WHERE booking_date >= CURRENT_DATE
ORDER BY booking_date, start_time;
```

### Create a New Booking
```sql
INSERT INTO bookings (
    venue_id, 
    event_name, 
    event_description,
    organizer_name,
    organizer_email,
    booking_date,
    start_time,
    end_time,
    club_id,
    expected_attendees,
    created_by,
    status
) VALUES (
    'venue-uuid',
    'Tech Workshop',
    'Annual coding workshop',
    'John Doe',
    'john@institution.edu',
    '2026-03-20',
    '14:00:00',
    '17:00:00',
    'club-uuid',
    50,
    'pro-user-uuid',
    'pending'
);
```

### Add Items to Booking
```sql
INSERT INTO booking_items (
    booking_id,
    venue_item_id,
    quantity_requested
) VALUES 
    ('booking-uuid', 'microphone-item-uuid', 2),
    ('booking-uuid', 'laptop-item-uuid', 1);
```

### View Booking History
```sql
SELECT 
    action,
    performed_by,
    created_at,
    new_values->>'status' as status
FROM booking_audit_log
WHERE booking_id = 'booking-uuid'
ORDER BY created_at DESC;
```

---

## Deployment to Supabase

### Step 1: Create Project
1. Log in to [Supabase](https://supabase.com)
2. Create a new project
3. Wait for database provisioning

### Step 2: Run Schema
1. Go to SQL Editor in Supabase dashboard
2. Create a new query
3. Copy entire contents of `schema.sql`
4. Execute the query

### Step 3: Configure Authentication
1. Enable Email authentication in Supabase Auth settings
2. Configure email templates
3. Set up user sign-up flow

### Step 4: Verify Setup
```sql
-- Check if all tables are created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

---

## Security Considerations

### Authentication
- Use Supabase Auth for user authentication
- Enforce email verification
- Implement strong password policies

### Authorization
- RLS policies are active on all tables
- Role-based access enforced at database level
- Students cannot modify any data
- Only PRO can finalize bookings

### Data Protection
- Sensitive notes in `internal_notes` field
- Approval letters stored securely
- Audit log preserves complete history
- Soft deletes preferred over hard deletes

---

## Indexes for Performance

Indexes are created on:
- Frequently queried fields (date, status, venue_id)
- Foreign key relationships
- Fields used in WHERE clauses
- Composite indexes for common query patterns

This ensures fast queries even with thousands of bookings.

---

## Sample Data

The schema includes sample data for testing:
- 5 users (admin, PRO, HOD, principal, student)
- 4 venues (seminar hall, lab, auditorium, conference room)
- 3 clubs (ACM, Drama, Tech)
- 3 venue items

Remove or modify sample data before production deployment.

---

## Future Enhancements

Potential additions to consider:
1. **Recurring bookings** - Weekly/monthly booking patterns
2. **Waiting list** - Queue system for popular venues
3. **Notifications** - Email/SMS alerts for booking updates
4. **Reports** - Usage statistics and analytics
5. **Mobile API** - REST endpoints for mobile app
6. **Payment integration** - If booking fees are introduced
7. **Resource optimization** - AI-based venue suggestions

---

## Support

For questions or issues:
1. Check the functional requirements document
2. Review this schema documentation
3. Examine the SQL comments in schema.sql
4. Test queries in Supabase SQL Editor

---

## Version History

- **v1.0** (2026-03-05) - Initial schema design
  - Core tables and relationships
  - RLS policies
  - Audit logging
  - Sample data
