-- Venue Booking System Database Schema for Neon PostgreSQL
-- Designed for complete venue booking, department routing, and PRO logistics workflows

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clean existing tables to prevent schema mismatch
DROP TABLE IF EXISTS event_facilities CASCADE;
DROP TABLE IF EXISTS "Events" CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS venue_facilities CASCADE;
DROP TABLE IF EXISTS venue_items CASCADE;
DROP TABLE IF EXISTS booking_items CASCADE;
DROP TABLE IF EXISTS club_coordinators CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS department CASCADE;
DROP TABLE IF EXISTS venues CASCADE;
DROP TABLE IF EXISTS venue_type CASCADE;
DROP TABLE IF EXISTS location CASCADE;
DROP TABLE IF EXISTS facilities CASCADE;
DROP TABLE IF EXISTS clubs CASCADE;
DROP TABLE IF EXISTS event_types CASCADE;

-- Drop legacy enums if they exist to prevent table/type name collisions
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'venue_type') THEN
        DROP TYPE venue_type CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        DROP TYPE user_role CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'booking_status') THEN
        DROP TYPE booking_status CASCADE;
    END IF;
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- ============================================
-- TABLES
-- ============================================

-- Department Table
CREATE TABLE IF NOT EXISTS department (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50),
    hod_id UUID,
    hod_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    user_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    role VARCHAR(50) NOT NULL DEFAULT 'student', -- student, hod, pro, principal, admin
    department VARCHAR(100),
    department_id UUID REFERENCES department(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add Foreign Key for department.hod_id after users table creation
ALTER TABLE department 
ADD CONSTRAINT fk_department_hod 
FOREIGN KEY (hod_id) REFERENCES users(id) ON DELETE SET NULL;

-- Location Table
CREATE TABLE IF NOT EXISTS location (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venue Type Table
CREATE TABLE IF NOT EXISTS venue_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venues Table
CREATE TABLE IF NOT EXISTS venues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    venue_type_id UUID REFERENCES venue_type(id) ON DELETE SET NULL,
    location_id UUID REFERENCES location(id) ON DELETE SET NULL,
    department_id UUID REFERENCES department(id) ON DELETE SET NULL,
    location VARCHAR(255),
    floor VARCHAR(50),
    room_number VARCHAR(50),
    capacity INTEGER DEFAULT 50,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    booking_allowed BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venue Items Table
CREATE TABLE IF NOT EXISTS venue_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    is_bookable BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Facilities Table (Logistics: chairs, tables, mic, podium, sound system)
CREATE TABLE IF NOT EXISTS facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    f_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venue Facilities Bridge Table
CREATE TABLE IF NOT EXISTS venue_facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(venue_id, facility_id)
);

-- Clubs Table
CREATE TABLE IF NOT EXISTS clubs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Event Types Table
CREATE TABLE IF NOT EXISTS event_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Events Table (Active Booking Applications)
CREATE TABLE IF NOT EXISTS "Events" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE RESTRICT,
    club_id UUID REFERENCES clubs(id) ON DELETE SET NULL,
    event_type_id UUID REFERENCES event_types(id) ON DELETE SET NULL,
    
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    
    faculty_coordinator VARCHAR(255),
    contact_number VARCHAR(50),
    permission_file_url TEXT,
    
    assigned_to VARCHAR(255), -- UUID of HOD or 'pro'
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'Pending', -- Pending, Approved, Rejected, Cancelled
    pro_status VARCHAR(50) DEFAULT 'Pending',
    pro_remarks TEXT,
    rejection_reason TEXT,
    cancellation_reason TEXT,
    
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Event Facilities Requested Table (Logistics Copy sent to PRO)
CREATE TABLE IF NOT EXISTS event_facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES "Events"(id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    requested_quantity INTEGER DEFAULT 1,
    allocated_quantity INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Finalized Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES "Events"(id) ON DELETE SET NULL,
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE RESTRICT,
    event_name VARCHAR(255) NOT NULL,
    event_description TEXT,
    club_id UUID REFERENCES clubs(id) ON DELETE SET NULL,
    
    booking_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    
    approval_letter_path TEXT,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- VIEWS FOR CALENDAR & DASHBOARD
-- ============================================

CREATE OR REPLACE VIEW dashboard_events_view AS
SELECT 
    e.id,
    e.title,
    e.description,
    e.start_time,
    e.end_time,
    e.venue_id,
    v.name AS venue_name,
    e.club_id,
    c.name AS club_name,
    e.event_type_id,
    et.event_type_name,
    e.faculty_coordinator,
    e.faculty_coordinator AS faculty_name,
    e.contact_number,
    e.contact_number AS phone,
    e.permission_file_url,
    e.assigned_to,
    e.approved_by,
    e.status,
    e.pro_status,
    e.pro_remarks,
    e.rejection_reason,
    e.cancellation_reason,
    e.created_by,
    e.created_at
FROM "Events" e
LEFT JOIN venues v ON e.venue_id = v.id
LEFT JOIN clubs c ON e.club_id = c.id
LEFT JOIN event_types et ON e.event_type_id = et.id;

CREATE OR REPLACE VIEW events_view AS
SELECT 
    e.id,
    e.title,
    e.start_time,
    e.end_time,
    v.name AS venue_name,
    e.status
FROM "Events" e
LEFT JOIN venues v ON e.venue_id = v.id
WHERE e.status IN ('Approved', 'Confirmed', 'approved', 'confirmed');