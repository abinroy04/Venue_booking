
-- ============================================
-- SAMPLE DATA (for testing)
-- ============================================

-- Insert sample admin user
INSERT INTO users (email, user_name, role, department) VALUES
('admin@sgce.org', 'System Administrator', 'admin', 'Administration'),
('pro@sgce.org', 'Public Relations Officer', 'pro', 'Administration'),
('hod.cs@sgce.org', 'HOD Computer Science', 'hod', 'Computer Science'),
('principal@sgce.org', 'Principal', 'principal', 'Administration'),
('student@sgce.org', 'John Doe', 'student', 'Computer Science');

-- Insert sample venues
INSERT INTO venues (name, venue_type, location, description) VALUES
('AK Seminar Hall', 'seminar_hall', 'Abdul Kalam Block', 'Seminar hall for events in AK Block'),
('Project Lab', 'lab', 'Ramanujan Block', 'Computer science laboratory'),
('Mini Auditorium', 'auditorium', 'Behind CLC', 'Auditorium for lectures and performances'),
('Conference Room', 'classroom', 'Admin Block', 'Small conference room for meetings');

-- Insert sample clubs
INSERT INTO clubs (name, description) VALUES
('ACM Student Chapter', 'Association for Computing Machinery student chapter'),
('Coding Club', 'Institutional coding club'),
('Tech Club', 'Technology and innovation club');

-- Insert sample venue items
INSERT INTO venue_items (venue_id, item_name, quantity, description) 
SELECT id, 'Microphone', 4, 'Wireless handheld microphone' FROM venues WHERE name = 'AK Seminar Hall'
UNION ALL
SELECT id, 'Laptop', 2, 'Presentation laptop with HDMI' FROM venues WHERE name = 'AK Seminar Hall'
UNION ALL
SELECT id, 'Pointer', 3, 'Laser pointer' FROM venues WHERE name = 'AK Seminar Hall';