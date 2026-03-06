-- Venue Booking System Database Schema
-- Designed for Supabase (PostgreSQL)
-- Created: 2026-03-05

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUMS
-- ============================================

-- User roles enum
CREATE TYPE user_role AS ENUM ('student', 'hod', 'principal', 'pro', 'admin');

-- Booking status enum
CREATE TYPE booking_status AS ENUM ('pending', 'approved', 'confirmed', 'cancelled', 'rejected');

-- Venue type enum
CREATE TYPE venue_type AS ENUM ('seminar_hall', 'lab', 'auditorium', 'classroom', 'amphitheater', 'other');

-- Day of week enum for recurring schedules
CREATE TYPE day_of_week AS ENUM ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday');

-- ============================================
-- TABLES
-- ============================================

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    role user_role NOT NULL DEFAULT 'student',
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Clubs Table
CREATE TABLE clubs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Club Coordinators Junction Table
CREATE TABLE club_coordinators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'coordinator', -- coordinator, president, secretary, etc.
    assigned_from DATE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(club_id, user_id, assigned_from)
);

-- Venues Table
CREATE TABLE venues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    venue_type venue_type NOT NULL,
    location VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    booking_allowed BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venue Items/Components Table
CREATE TABLE venue_items (
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

-- Bookings Table
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE RESTRICT,
    event_name VARCHAR(255) NOT NULL,
    event_description TEXT,
    club_id UUID REFERENCES clubs(id) ON DELETE SET NULL,
    
    -- Date and time information
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    -- Status and approval workflow
    status booking_status DEFAULT 'pending',
    approval_letter_path VARCHAR(500), -- Path to uploaded approval letter
    approval_notes TEXT,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Booking management
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cancelled_by UUID REFERENCES users(id) ON DELETE SET NULL,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    
    -- Additional fields
    special_requirements TEXT,
    internal_notes TEXT, -- Only visible to authorized personnel
    
    -- Constraints
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

-- Booking Items Junction Table (items booked along with venue)
CREATE TABLE booking_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    venue_item_id UUID NOT NULL REFERENCES venue_items(id) ON DELETE RESTRICT,
    quantity_requested INTEGER DEFAULT 1,
    quantity_allocated INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_quantity CHECK (quantity_requested > 0)
);


-- ============================================
-- INDEXES
-- ============================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Venues indexes
CREATE INDEX idx_venues_type ON venues(venue_type);
CREATE INDEX idx_venues_active ON venues(is_active);
CREATE INDEX idx_venues_booking_allowed ON venues(booking_allowed);

-- Bookings indexes
CREATE INDEX idx_bookings_venue ON bookings(venue_id);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_created_by ON bookings(created_by);
CREATE INDEX idx_bookings_club ON bookings(club_id);
CREATE INDEX idx_bookings_date_time ON bookings(booking_date, start_time, end_time);
CREATE INDEX idx_bookings_venue_date ON bookings(venue_id, booking_date);

-- Venue items indexes
CREATE INDEX idx_venue_items_venue ON venue_items(venue_id);
CREATE INDEX idx_venue_items_bookable ON venue_items(is_bookable);

-- Booking items indexes
CREATE INDEX idx_booking_items_booking ON booking_items(booking_id);
CREATE INDEX idx_booking_items_venue_item ON booking_items(venue_item_id);

-- ============================================
-- VIEWS
-- ============================================

-- View for calendar display (read-only access for students)
CREATE VIEW calendar_view AS
SELECT 
    b.id,
    b.event_name,
    v.name AS venue_name,
    v.venue_type,
    v.location,
    v.description,
    b.booking_date,
    b.start_time,
    b.end_time,
    b.status,
    c.name AS club_name,
    b.created_at
FROM bookings b
JOIN venues v ON b.venue_id = v.id
LEFT JOIN clubs c ON b.club_id = c.id
WHERE b.status IN ('confirmed', 'approved')
ORDER BY b.booking_date, b.start_time;

-- View for available venues with upcoming bookings
CREATE VIEW venue_availability AS
SELECT 
    v.id AS venue_id,
    v.name AS venue_name,
    v.venue_type,
    v.location,
    COUNT(b.id) FILTER (WHERE b.booking_date >= CURRENT_DATE AND b.status = 'confirmed') AS upcoming_bookings
FROM venues v
LEFT JOIN bookings b ON v.id = b.venue_id
WHERE v.is_active = true AND v.booking_allowed = true
GROUP BY v.id, v.name, v.venue_type, v.location;

-- View for booking details with all related information
CREATE VIEW booking_details AS
SELECT 
    b.id,
    b.event_name,
    b.event_description,
    v.name AS venue_name,
    v.venue_type,
    v.location,
    b.booking_date,
    b.start_time,
    b.end_time,
    b.status,
    c.name AS club_name,
    creator.user_name AS created_by_name,
    creator.email AS created_by_email,
    approver.user_name AS approved_by_name,
    b.approved_at,
    b.special_requirements,
    b.created_at,
    b.updated_at,
    ARRAY_AGG(
        DISTINCT JSONB_BUILD_OBJECT(
            'item_name', vi.item_name,
            'quantity_requested', bi.quantity_requested,
            'quantity_allocated', bi.quantity_allocated
        )
    ) FILTER (WHERE vi.id IS NOT NULL) AS booked_items
FROM bookings b
JOIN venues v ON b.venue_id = v.id
LEFT JOIN clubs c ON b.club_id = c.id
LEFT JOIN users creator ON b.created_by = creator.id
LEFT JOIN users approver ON b.approved_by = approver.id
LEFT JOIN booking_items bi ON b.id = bi.booking_id
LEFT JOIN venue_items vi ON bi.venue_item_id = vi.id
GROUP BY 
    b.id, b.event_name, b.event_description, v.name, v.venue_type, v.location,
    b.booking_date, b.start_time, b.end_time, b.status,
    c.name, creator.user_name, creator.email, approver.user_name,
    b.approved_at, b.special_requirements, b.created_at, b.updated_at;


-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clubs ENABLE ROW LEVEL SECURITY;
ALTER TABLE club_coordinators ENABLE ROW LEVEL SECURITY;
ALTER TABLE venues ENABLE ROW LEVEL SECURITY;
ALTER TABLE venue_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_items ENABLE ROW LEVEL SECURITY;