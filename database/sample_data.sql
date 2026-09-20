
-- ============================================
-- SAMPLE DATA (for testing)
-- ============================================

-- Insert sample departments
INSERT INTO department (name, code) VALUES
('Computer Science & Engineering', 'CSE'),
('Electrical & Electronics Engineering', 'EEE'),
('Mechanical Engineering', 'ME'),
('Civil Engineering', 'CE'),
('Information Technology', 'IT')
ON CONFLICT DO NOTHING;

-- Insert sample admin & HOD users (Password for all sample accounts: password123)
INSERT INTO users (email, password_hash, user_name, role, department) VALUES
('admin@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'System Administrator', 'admin', 'Administration'),
('pro@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'Public Relations Officer', 'pro', 'Administration'),
('hodcse@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'HOD Computer Science', 'hod', 'Computer Science & Engineering'),
('hodeee@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'HOD Electrical Engineering', 'hod', 'Electrical & Electronics Engineering'),
('hodmech@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'HOD Mechanical Engineering', 'hod', 'Mechanical Engineering'),
('hodcivil@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'HOD Civil Engineering', 'hod', 'Civil Engineering'),
('hodit@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'HOD Information Technology', 'hod', 'Information Technology'),
('principal@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'Principal', 'principal', 'Administration'),
('student@saintgits.org', '$2b$12$OpW0Y84gq41zG1/kroh2tOxLxvEZ08ERMS9PluexFf.tzebgDIfrq', 'John Doe', 'student', 'Computer Science & Engineering')
ON CONFLICT (email) DO NOTHING;

-- Insert sample venues
INSERT INTO venues (name, location, description) VALUES
('RB Seminar Hall', 'Ramanujan Block', 'CS Department Seminar Hall'),
('EEE Seminar Hall', 'Electrical Block', 'EEE Department Seminar Hall'),
('Mech Seminar Hall', 'Mechanical Block', 'Mechanical Department Seminar Hall'),
('VB Seminar Hall', 'Visvesvaraya Block', 'Civil Department Seminar Hall'),
('IT Lab', 'Ramanujan Block 2nd Floor', 'Information Technology Laboratory'),
('AK Seminar Hall', 'Abdul Kalam Block', 'Central Seminar Hall'),
('Mini Auditorium', 'Behind CLC', 'Central Auditorium'),
('High-Tech Lab', 'Main Building', 'Central High-Tech Computing Facility')
ON CONFLICT DO NOTHING;

-- Insert sample clubs
INSERT INTO clubs (name, description) VALUES
('ACM Student Chapter', 'Association for Computing Machinery student chapter'),
('Coding Club', 'Institutional coding club'),
('Tech Club', 'Technology and innovation club');

-- Insert sample facilities (logistics)
INSERT INTO facilities (f_name, description) VALUES
('Chairs', 'Standard event seating chairs'),
('Tables', 'Conference and display tables'),
('Microphones', 'Wireless handheld & collar mics'),
('Podium', 'Presentation podium'),
('Projector & Screen', 'High-definition HDMI projector'),
('Sound System', 'Amplifier and speaker system')
ON CONFLICT DO NOTHING;

-- Insert sample venue items
INSERT INTO venue_items (venue_id, item_name, quantity, description) 
SELECT id, 'Microphone', 4, 'Wireless handheld microphone' FROM venues WHERE name = 'AK Seminar Hall'
UNION ALL
SELECT id, 'Laptop', 2, 'Presentation laptop with HDMI' FROM venues WHERE name = 'AK Seminar Hall'
UNION ALL
SELECT id, 'Pointer', 3, 'Laser pointer' FROM venues WHERE name = 'AK Seminar Hall';

-- Insert sample event types
INSERT INTO event_types (event_type_name) VALUES
('Workshop'),
('Seminar'),
('Conference'),
('Cultural Event'),
('Tech Fest'),
('Department Meeting'),
('Guest Lecture'),
('Other')
ON CONFLICT DO NOTHING;