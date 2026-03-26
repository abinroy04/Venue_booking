# API Documentation
## Venue Booking System - Complete API Reference

**Version**: 1.0  
**Base URL**: `http://localhost:5000/api` (Development)  
**Authentication**: Bearer Token (JWT)

---

## Table of Contents
1. [Authentication](#authentication)
2. [Bookings API](#bookings-api)
3. [Venues API](#venues-api)
4. [Clubs API](#clubs-api)
5. [Users API](#users-api)
6. [File Upload API](#file-upload-api)
7. [Error Handling](#error-handling)

---

## Authentication

### Login
**POST** `/auth/login`

Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "email": "hod@institution.edu",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid-here",
      "email": "hod@institution.edu",
      "full_name": "Dr. Jane Smith",
      "role": "hod",
      "department": "Computer Science"
    }
  }
}
```

**Error** (401 Unauthorized):
```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

---

### Logout
**POST** `/auth/logout`

Invalidate current session.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### Get Current User
**GET** `/auth/me`

Get current authenticated user details.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "email": "hod@institution.edu",
    "full_name": "Dr. Jane Smith",
    "role": "hod",
    "department": "Computer Science",
    "phone": "9876543210"
  }
}
```

---

## Bookings API

### Get All Bookings (Public)
**GET** `/bookings`

Get all confirmed bookings visible to public.

**Query Parameters**:
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `venue_id` (optional): Filter by venue UUID
- `club_id` (optional): Filter by club UUID
- `search` (optional): Search by event name

**Example Request**:
```
GET /api/bookings?start_date=2026-03-01&end_date=2026-03-31&venue_id=abc-123
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "booking-uuid-1",
      "event_name": "Tech Workshop 2026",
      "event_description": "Annual coding workshop",
      "venue": {
        "id": "venue-uuid",
        "name": "Main Seminar Hall",
        "venue_type": "seminar_hall",
        "location": "Block A, Floor 1",
        "capacity": 200
      },
      "booking_date": "2026-03-20",
      "start_time": "14:00:00",
      "end_time": "17:00:00",
      "organizer_name": "Jane Smith",
      "department": "Computer Science",
      "club": {
        "id": "club-uuid",
        "name": "Tech Club"
      },
      "staff_in_charge": "Dr. John Doe",
      "expected_attendees": 50,
      "status": "confirmed",
      "venue_items": [
        {
          "item_name": "Microphone",
          "quantity": 2
        },
        {
          "item_name": "Laptop",
          "quantity": 1
        }
      ],
      "special_requirements": "Need sound system setup by 1:30 PM"
    }
  ],
  "meta": {
    "total": 1,
    "count": 1
  }
}
```

---

### Get Booking by ID
**GET** `/bookings/:id`

Get detailed information for a specific booking.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "booking-uuid-1",
    "event_name": "Tech Workshop 2026",
    "event_description": "Annual coding and innovation workshop",
    "venue": {
      "id": "venue-uuid",
      "name": "Main Seminar Hall",
      "venue_type": "seminar_hall",
      "location": "Block A, Floor 1",
      "building": "Academic Block A",
      "floor": 1,
      "capacity": 200,
      "facilities": ["projector", "ac", "sound_system", "whiteboard"]
    },
    "booking_date": "2026-03-20",
    "start_time": "14:00:00",
    "end_time": "17:00:00",
    "organizer_name": "Jane Smith",
    "organizer_email": "jane@institution.edu",
    "organizer_phone": "9876543210",
    "department": "Computer Science",
    "club": {
      "id": "club-uuid",
      "name": "Tech Club",
    },
    "coordinator": {
      "id": "user-uuid",
      "full_name": "John Doe",
      "email": "john@institution.edu"
    },
    "expected_attendees": 50,
    "status": "confirmed",
    "venue_items": [
      {
        "id": "item-uuid-1",
        "item_name": "Wireless Microphone",
        "quantity_requested": 2,
        "quantity_allocated": 2
      },
      {
        "id": "item-uuid-2",
        "item_name": "AC",
        "quantity_requested": 1,
        "quantity_allocated": 1
      }
    ],
    "special_requirements": "Need sound system setup by 1:30 PM",
    "approval_document_url": "https://storage.supabase.co/...",
    "created_by": {
      "full_name": "Dr. Jane Smith",
      "role": "hod"
    },
    "approved_by": {
      "full_name": "PRO Officer",
      "role": "pro"
    },
    "approved_at": "2026-03-06T10:30:00Z",
    "created_at": "2026-03-05T15:45:00Z"
  }
}
```

---

### Create Booking Request (HOD)
**POST** `/bookings`

Create a new booking request.

**Required Fields**:
1. Event Title
2. Description
3. Faculty Coordinator Name
4. Faculty Coordinator Phone Number
5. Event Type (Department / College)
6. Event Date (Start and End Date/Time)
7. Associated Club
8. Venue
9. Venue Amenities
10. Approved Letter Upload

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body** (form-data):
```
event_title: Tech Workshop 2026
description: Annual coding and innovation workshop
faculty_coordinator_name: Dr. Jane Smith
faculty_coordinator_phone_number: 9876543210
event_type: department
start_date: 2026-03-20
start_time: 14:00
end_date: 2026-03-20
end_time: 17:00
associated_club_id: club-uuid
venue_id: venue-uuid
venue_amenities: projector, sound_system
venue_items: [{"item_id": "uuid1", "quantity": 2}, {"item_id": "uuid2", "quantity": 1}]
approval_document: <file> (PDF/Image)

**Dropdown Values**:
- `event_type`: `department` or `college`
- `associated_club_id`: Club UUID selected from Clubs dropdown
- `venue_id`: Venue UUID selected from Venue dropdown
- `venue_amenities`: Selected amenity values from Venue Amenities dropdown
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Booking request created successfully",
  "data": {
    "id": "new-booking-uuid",
    "event_title": "Tech Workshop 2026",
    "event_type": "department",
    "status": "pending",
    "start_date": "2026-03-20",
    "start_time": "14:00:00",
    "end_date": "2026-03-20",
    "end_time": "17:00:00",
    "venue": {
      "name": "Main Seminar Hall"
    },
    "created_at": "2026-03-05T15:45:00Z"
  }
}
```

**Error** (409 Conflict):
```json
{
  "success": false,
  "error": {
    "code": "BOOKING_CONFLICT",
    "message": "Venue is already booked for the selected time slot",
    "details": {
      "conflicting_booking": {
        "id": "existing-booking-uuid",
        "event_name": "Existing Event",
        "start_time": "13:00:00",
        "end_time": "16:00:00"
      }
    }
  }
}
```

---

### Check Availability
**POST** `/bookings/check-availability`

Check if a venue is available for a given time slot.

**Request Body**:
```json
{
  "venue_id": "venue-uuid",
  "booking_date": "2026-03-20",
  "start_time": "14:00",
  "end_time": "17:00"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "available": true,
    "venue_name": "RB Seminar Hall",
    "conflicts": []
  }
}
```

**Response when NOT available**:
```json
{
  "success": true,
  "data": {
    "available": false,
    "venue_name": "RB Seminar Hall",
    "conflicts": [
      {
        "booking_id": "conflict-uuid",
        "event_name": "Existing Event",
        "start_time": "13:00:00",
        "end_time": "16:00:00"
      }
    ]
  }
}
```

---

### Get My Requests (HOD)
**GET** `/bookings/my-requests`

Get all booking requests created by the authenticated HOD.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `status` (optional): Filter by status (pending, approved, rejected, confirmed, cancelled)

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "booking-uuid",
      "event_name": "Tech Workshop 2026",
      "venue_name": "RB Seminar Hall",
      "booking_date": "2026-03-20",
      "start_time": "14:00:00",
      "end_time": "17:00:00",
      "status": "pending",
      "club_name": "Tech Club",
      "created_at": "2026-03-05T15:45:00Z",
      "can_edit": true
    },
    {
      "id": "booking-uuid-2",
      "event_name": "Coding Competition",
      "venue_name": "CS Lab 1",
      "booking_date": "2026-03-15",
      "start_time": "10:00:00",
      "end_time": "16:00:00",
      "status": "approved",
      "club_name": "ACM Chapter",
      "approved_at": "2026-03-06T10:30:00Z",
      "approved_by": "PRO Officer",
      "can_edit": false
    }
  ],
  "meta": {
    "total": 2,
    "pending": 1,
    "approved": 1
  }
}
```

---

### Update Booking Request (HOD)
**PUT** `/bookings/:id`

Update a pending booking request. Only allowed for requests in 'pending' status.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "event_name": "Updated Tech Workshop 2026",
  "expected_attendees": 60,
  "special_requirements": "Updated requirements"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Booking request updated successfully",
  "data": {
    "id": "booking-uuid",
    "event_name": "Updated Tech Workshop 2026",
    "updated_at": "2026-03-05T16:00:00Z"
  }
}
```

**Error** (403 Forbidden):
```json
{
  "success": false,
  "error": {
    "code": "BOOKING_CANNOT_EDIT",
    "message": "Cannot edit booking in 'approved' status"
  }
}
```

---

### Get Pending Requests (PRO)
**GET** `/bookings/pending`

Get all pending booking requests requiring PRO approval.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "booking-uuid",
      "event_name": "Tech Workshop 2026",
      "event_description": "Annual coding workshop",
      "venue": {
        "name": "Main Seminar Hall",
        "capacity": 200
      },
      "booking_date": "2026-03-20",
      "start_time": "14:00:00",
      "end_time": "17:00:00",
      "expected_attendees": 50,
      "club": {
        "name": "Tech Club"
      },
      "coordinator": {
        "full_name": "John Doe"
      },
      "created_by": {
        "full_name": "Dr. Jane Smith",
        "email": "hod@institution.edu",
        "department": "Computer Science"
      },
      "venue_items": [
        {"item_name": "Microphone", "quantity": 2},
        {"item_name": "Laptop", "quantity": 1}
      ],
      "approval_document_url": "https://storage.supabase.co/...",
      "has_conflicts": false,
      "created_at": "2026-03-05T15:45:00Z"
    }
  ],
  "meta": {
    "total": 3,
    "urgent": 1
  }
}
```

---

### Approve Booking (PRO)
**POST** `/bookings/:id/approve`

Approve a pending booking request and confirm the slot.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "approval_notes": "Approved. Ensure setup is done by 1:30 PM.",
  "internal_notes": "Notify facilities team for early setup"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Booking approved and confirmed successfully",
  "data": {
    "id": "booking-uuid",
    "status": "confirmed",
    "approved_at": "2026-03-05T16:30:00Z",
    "approved_by": "PRO Officer"
  }
}
```

---

### Reject Booking (PRO)
**POST** `/bookings/:id/reject`

Reject a pending booking request.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "rejection_reason": "Venue already reserved for institutional event on that date. Please select alternate date."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Booking request rejected",
  "data": {
    "id": "booking-uuid",
    "status": "rejected",
    "rejected_at": "2026-03-05T16:30:00Z"
  }
}
```

---

### Cancel Booking (PRO)
**POST** `/bookings/:id/cancel`

Cancel a confirmed booking.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "cancellation_reason": "Event postponed by organizer"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Booking cancelled successfully",
  "data": {
    "id": "booking-uuid",
    "status": "cancelled",
    "cancelled_at": "2026-03-05T16:30:00Z"
  }
}
```

---

### Get Booking History (PRO)
**GET** `/bookings/history`

Get complete history of all bookings with filters.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `start_date` (optional): From date
- `end_date` (optional): To date
- `status` (optional): Filter by status
- `venue_id` (optional): Filter by venue
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "booking-uuid",
      "event_name": "Tech Workshop 2026",
      "venue_name": "Main Seminar Hall",
      "booking_date": "2026-03-20",
      "start_time": "14:00:00",
      "end_time": "17:00:00",
      "status": "confirmed",
      "club_name": "Tech Club",
      "department": "Computer Science",
      "created_by": "Dr. Jane Smith",
      "approved_by": "PRO Officer",
      "created_at": "2026-03-05T15:45:00Z",
      "approved_at": "2026-03-05T16:30:00Z"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "pages": 8
  }
}
```

---

## Venues API

### Get All Venues
**GET** `/venues`

Get list of all active venues.

**Query Parameters**:
- `venue_type` (optional): Filter by type
- `booking_allowed` (optional): true/false

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "venue-uuid-1",
      "name": "Main Seminar Hall",
      "venue_type": "seminar_hall",
      "location": "Block A, Floor 1",
      "building": "Academic Block A",
      "floor": 1,
      "capacity": 200,
      "facilities": ["projector", "ac", "sound_system", "whiteboard"],
      "booking_allowed": true,
      "upcoming_bookings_count": 5
    },
    {
      "id": "venue-uuid-2",
      "name": "CS Lab 1",
      "venue_type": "lab",
      "location": "Block B, Floor 2",
      "building": "Computer Science Block",
      "floor": 2,
      "capacity": 60,
      "facilities": ["computers", "projector", "ac"],
      "booking_allowed": true,
      "upcoming_bookings_count": 3
    }
  ],
  "meta": {
    "total": 4
  }
}
```

---

### Create Venue
**POST** `/venues`

Create a new venue.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Required Fields**:
1. Venue name
2. Venue type (dropdown UUID)
3. Location
4. Description

**Request Body**:
```json
{
  "venue_name": "Innovation Hall",
  "venue_type_id": "6f25d4a8-9c3d-4f63-8ea8-96eec7f5fca2",
  "location": "Academic Block C, Floor 2",
  "description": "Large hall for department and college-level events"
}
```

**Field Notes**:
- `venue_type_id`: UUID selected from Venue Type dropdown.
- `venue_name`: Must be unique within active venues.

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Venue created successfully",
  "data": {
    "id": "venue-uuid-3",
    "name": "Innovation Hall",
    "venue_type_id": "6f25d4a8-9c3d-4f63-8ea8-96eec7f5fca2",
    "location": "Academic Block C, Floor 2",
    "description": "Large hall for department and college-level events",
    "is_active": true,
    "booking_allowed": true,
    "created_at": "2026-03-26T10:15:00Z"
  }
}
```

**Error** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Missing required fields: venue_name, venue_type_id"
  }
}
```

---

### Get Venue by ID
**GET** `/venues/:id`

Get detailed information for a specific venue.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "venue-uuid-1",
    "name": "Main Seminar Hall",
    "venue_type": "seminar_hall",
    "location": "Block A, Floor 1",
    "building": "Academic Block A",
    "floor": 1,
    "capacity": 200,
    "description": "Main seminar hall with modern facilities",
    "facilities": ["projector", "ac", "sound_system", "whiteboard"],
    "booking_allowed": true,
    "venue_items": [
      {
        "id": "item-uuid-1",
        "item_name": "Wireless Microphone",
        "description": "Handheld wireless microphone",
        "quantity": 4,
        "available": 4,
        "is_bookable": true
      },
      {
        "id": "item-uuid-2",
        "item_name": "Laptop",
        "description": "Presentation laptop with HDMI",
        "quantity": 2,
        "available": 2,
        "is_bookable": true
      }
    ],
    "upcoming_bookings": [
      {
        "id": "booking-uuid",
        "event_name": "Tech Workshop",
        "booking_date": "2026-03-20",
        "start_time": "14:00:00",
        "end_time": "17:00:00"
      }
    ]
  }
}
```

---

### Get Venue Items
**GET** `/venues/:id/items`

Get all bookable items for a specific venue.

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "item-uuid-1",
      "item_name": "Wireless Microphone",
      "description": "Handheld wireless microphone",
      "quantity": 4,
      "is_bookable": true
    },
    {
      "id": "item-uuid-2",
      "item_name": "Laptop",
      "description": "Presentation laptop with HDMI",
      "quantity": 2,
      "is_bookable": true
    },
    {
      "id": "item-uuid-3",
      "item_name": "Laser Pointer",
      "description": "Red laser pointer",
      "quantity": 3,
      "is_bookable": true
    }
  ]
}
```

---

## Clubs API

### Get All Clubs
**GET** `/clubs`

Get list of all active clubs.

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "club-uuid-1",
      "name": "ACM Student Chapter",
      "description": "Association for Computing Machinery student chapter",
      "email": "acm@institution.edu",
      "is_active": true
    },
    {
      "id": "club-uuid-2",
      "name": "Tech Club",
      "description": "Technology and innovation club",
      "email": "tech@institution.edu",
      "is_active": true
    }
  ]
}
```

---

### Create Club
**POST** `/clubs`

Create a new club.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Required Fields**:
1. Club name
2. Description

**Request Body**:
```json
{
  "name": "Innovation Club",
  "description": "Club focused on product innovation and startup activities"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Club created successfully",
  "data": {
    "id": "club-uuid-3",
    "name": "Innovation Club",
    "description": "Club focused on product innovation and startup activities",
    "is_active": true,
    "created_at": "2026-03-26T11:20:00Z"
  }
}
```

**Error** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Missing required fields: name, description"
  }
}
```

---

## Users API

### Get All Users (Admin/PRO only)
**GET** `/users`

Get list of all users.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `role` (optional): Filter by role
- `department` (optional): Filter by department

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "user-uuid",
      "email": "hod@institution.edu",
      "full_name": "Dr. Jane Smith",
      "role": "hod",
      "department": "Computer Science",
      "phone": "9876543210",
      "is_active": true
    }
  ]
}
```

---

## File Upload API

### Upload Approval Document
**POST** `/upload/approval-document`

Upload approval document for booking request.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body** (form-data):
```
file: <PDF/Image file>
booking_id: booking-uuid (optional, for existing booking)
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "file_id": "file-uuid",
    "file_name": "approval_letter.pdf",
    "file_url": "https://storage.supabase.co/object/public/approval-letters/...",
    "file_size": 245678,
    "uploaded_at": "2026-03-05T15:45:00Z"
  }
}
```

**Error** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only PDF and image files are allowed"
  }
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `AUTH_UNAUTHORIZED` | 401 | Missing or invalid token |
| `AUTH_FORBIDDEN` | 403 | Insufficient permissions |
| `BOOKING_CONFLICT` | 409 | Time slot already booked |
| `BOOKING_NOT_FOUND` | 404 | Booking does not exist |
| `BOOKING_CANNOT_EDIT` | 403 | Cannot edit booking in current status |
| `VENUE_NOT_FOUND` | 404 | Venue does not exist |
| `VENUE_NOT_AVAILABLE` | 409 | Venue not available for booking |
| `INVALID_INPUT` | 400 | Invalid request data |
| `INVALID_FILE_TYPE` | 400 | Unsupported file type |
| `FILE_TOO_LARGE` | 400 | File exceeds size limit |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

- **Public API**: 100 requests per minute per IP
- **Authenticated API**: 300 requests per minute per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 250
X-RateLimit-Reset: 1678012800
```

---

## Authentication Flow

1. **Login**: POST `/auth/login` → Receive JWT token
2. **Include token**: Add `Authorization: Bearer <token>` header to all requests
3. **Token expiry**: Tokens expire after 24 hours
4. **Refresh**: Re-login when token expires

---

## Example Usage

### JavaScript (Fetch API)
```javascript
// Login
const login = async (email, password) => {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.data.token);
    return data.data.user;
  }
  throw new Error(data.error.message);
};

// Get bookings
const getBookings = async (startDate, endDate) => {
  const response = await fetch(
    `http://localhost:5000/api/bookings?start_date=${startDate}&end_date=${endDate}`
  );
  
  const data = await response.json();
  return data.data;
};

// Create booking (HOD)
const createBooking = async (bookingData) => {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  
  Object.keys(bookingData).forEach(key => {
    formData.append(key, bookingData[key]);
  });
  
  const response = await fetch('http://localhost:5000/api/bookings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  const data = await response.json();
  return data;
};
```

### Python (Requests)
```python
import requests

# Login
def login(email, password):
    response = requests.post(
        'http://localhost:5000/api/auth/login',
        json={'email': email, 'password': password}
    )
    data = response.json()
    if data['success']:
        return data['data']['token']
    raise Exception(data['error']['message'])

# Get bookings
def get_bookings(token, start_date, end_date):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'start_date': start_date, 'end_date': end_date}
    
    response = requests.get(
        'http://localhost:5000/api/bookings',
        headers=headers,
        params=params
    )
    
    return response.json()['data']
```

---

## WebSocket Events (Optional Enhancement)

For real-time updates:

### Connection
```javascript
const socket = io('http://localhost:5000');
socket.emit('authenticate', { token: 'your-jwt-token' });
```

### Events
- `booking:created` - New booking created
- `booking:updated` - Booking status changed
- `booking:approved` - Booking approved by PRO
- `booking:rejected` - Booking rejected

---

**Document Version**: 1.0  
**Last Updated**: March 5, 2026  
**Maintained By**: Backend Team
