# User Flows & Workflows
## Venue Booking System - Complete User Journey Documentation

**Version**: 1.0  
**Date**: March 5, 2026

---

## Table of Contents
1. [Public User Flow](#public-user-flow)
2. [HOD Workflows](#hod-workflows)
3. [PRO Workflows](#pro-workflows)
4. [System Workflows](#system-workflows)

---

## Public User Flow

### Flow 1: View Calendar and Booking Details

**Actors**: Public User / Student

**Steps**:
```
1. User visits landing page
   └─> Calendar loads with confirmed bookings
   
2. User views calendar
   ├─> Can switch between Month/Week/Day views
   ├─> Can navigate to different dates
   └─> Sees all confirmed bookings as events
   
3. User applies filters (optional)
   ├─> Select venue from dropdown
   ├─> Select date range
   └─> Enter search text
   
4. User clicks on a booking event
   └─> Modal opens with detailed information
   
5. Booking detail modal shows:
   ├─> Event name and description
   ├─> Date and time
   ├─> Venue details (name, location, capacity)
   ├─> Organizer information
   ├─> Department and club
   ├─> Staff in charge
   ├─> Venue items booked
   ├─> Expected attendees
   └─> Special requirements
   
6. User closes modal
   └─> Returns to calendar view
   
7. User can click "Login" button
   └─> Redirected to login page
```

---

## HOD Workflows

### Flow 2: HOD Login

**Actors**: HOD (Head of Department)

**Steps**:
```
1. HOD clicks "Login" button on landing page
   └─> Redirected to login page
   
2. Login page displays
   ├─> Email input field
   ├─> Password input field
   └─> "Login" button
   
3. HOD enters credentials
   ├─> Email: hod@institution.edu
   └─> Password: ********
   
4. HOD clicks "Login"
   └─> System validates credentials
   
5a. If credentials valid:
    ├─> JWT token generated and stored
    ├─> User redirected to HOD Dashboard
    └─> Success message shown
    
5b. If credentials invalid:
    ├─> Error message displayed
    └─> User remains on login page
```

**Error Handling**:
- Invalid credentials: "Invalid email or password"
- Network error: "Unable to connect. Please try again."

---

### Flow 3: Create Booking Request

**Actors**: HOD

**Prerequisites**: HOD must be logged in

**Steps**:
```
1. HOD navigates to HOD Dashboard
   └─> Default tab: "Create Request"
   
2. HOD fills Event Details section
   ├─> Event Name (required)
   └─> Event Description (optional)
   
3. HOD selects Venue
   └─> Dropdown shows all available venues
   
4. HOD selects Date and Time
   ├─> Date picker for booking date
   ├─> Time picker for start time
   └─> Time picker for end time
   
5. System checks availability (real-time)
   ├─> API call: POST /api/bookings/check-availability
   ├─> If available: ✓ Green checkmark shown
   └─> If conflict: ⚠ Warning with conflict details
   
6. If conflict exists:
   ├─> System shows conflicting booking details
   ├─> HOD can choose different time or venue
   └─> Repeat from step 3 or 4
   
7. HOD selects Venue Items (optional)
   ├─> System loads items for selected venue
   ├─> HOD checks items needed
   ├─> HOD enters quantity for each item
   └─> System validates quantity against availability
   
8. HOD selects Club
   └─> Dropdown shows all active clubs (Coordinator selected automatically)
    
9. HOD enters Special Requirements (optional)
    └─> Text area for additional notes
    
10. HOD uploads Approval Document (required)
    ├─> Click "Choose File" button
    ├─> Select PDF or image file (max 10MB)
    ├─> File name displayed after selection
    └─> Validation: Must be PDF or image
    
12. HOD reviews all information
    └─> All required fields filled and valid
    
13. HOD clicks "Submit Request"
    └─> System validates all inputs
    
14a. If validation passes:
     ├─> API call: POST /api/bookings (with file upload)
     ├─> Booking request created with status "pending"
     ├─> Success message displayed
     ├─> Form cleared
     └─> HOD redirected to "My Requests" tab
     
14b. If validation fails:
     ├─> Error messages shown for invalid fields
     └─> HOD corrects errors and resubmits
     
15. Confirmation message shown:
    "Booking request submitted successfully! 
     PRO will review and approve your request."
```


**UI States**:
- Loading: Show spinner during availability check
- Error: Show red warning for conflicts
- Disabled: Disable submit button until all required fields valid

---

### Flow 4: View and Edit My Requests

**Actors**: HOD

**Prerequisites**: HOD must be logged in

**Steps**:
```
1. HOD clicks "My Requests" tab
   └─> System loads HOD's booking requests
   
2. System displays list of requests
   ├─> Grouped by status (Pending, Approved, Rejected)
   └─> Sorted by date (newest first)
   
3. Each request card shows:
   ├─> Event name
   ├─> Date and time
   ├─> Venue name
   ├─> Club name
   ├─> Status badge (color-coded)
   ├─> Submission date
   └─> Action buttons
   
4. HOD can filter requests
   └─> Dropdown: All / Pending / Approved / Rejected / Cancelled
   
5. HOD clicks on a request
   └─> Full details modal opens
   
6a. For PENDING requests:
    ├─> [View Details] button - Opens detail modal
    ├─> [Edit] button - Opens edit form
    └─> [Cancel Request] button - Cancels the request
    
6b. For APPROVED/CONFIRMED requests:
    └─> [View Details] button only (read-only)
    
6c. For REJECTED requests:
    ├─> [View Details] button
    └─> Shows rejection reason
    
7. If HOD clicks [Edit]:
   ├─> Edit form opens with pre-filled data
   ├─> HOD can modify:
   │   ├─> Event details
   │   ├─> Contact information
   │   ├─> Special requirements
   │   └─> Upload new approval document
   ├─> Cannot modify: Venue, Date, Time (must create new request)
   └─> HOD saves changes
   
8. If HOD clicks [Cancel Request]:
   ├─> Confirmation dialog appears
   ├─> "Are you sure you want to cancel this request?"
   ├─> [No, Keep It] [Yes, Cancel]
   └─> If confirmed, request status changed to "cancelled"
   
9. System updates the list
   └─> Changes reflected immediately
```

**Status Badge Colors**:
- Pending: Yellow/Orange
- Approved: Green
- Confirmed: Dark Green
- Rejected: Red
- Cancelled: Gray

---

## PRO Workflows

### Flow 5: PRO Login

**Actors**: PRO (Public Relations Officer)

**Steps**:
```
Same as Flow 2 (HOD Login) but:
- PRO credentials used
- Redirected to PRO Dashboard
- More features available
```

---

### Flow 6: Review and Approve Booking Requests

**Actors**: PRO

**Prerequisites**: PRO must be logged in

**Steps**:
```
1. PRO navigates to PRO Dashboard
   └─> Default tab: "Pending Requests"
   
2. System loads all pending booking requests
   ├─> API call: GET /api/bookings/pending
   └─> Displays count: "Pending Requests (3)"
   
3. System displays each request as expanded card with:
   ├─> Event name and description
   ├─> Requested by (HOD name, email, department)
   ├─> Date, time, and duration
   ├─> Venue details
   ├─> Club and coordinator information
   ├─> Expected attendees
   ├─> Venue items requested
   ├─> Approval document link
   ├─> Submission date
   ├─> Conflict check status
   └─> Action buttons
   
4. PRO reviews the request details
   ├─> Clicks [View PDF] to see approval document
   ├─> Document opens in new tab or modal
   └─> PRO verifies approval signatures
   
5. System shows conflict check results
   ├─> ✓ "No conflicts" (green) - Safe to approve
   └─> ⚠ "Conflict detected" (red) - Shows conflicting booking
   
6. PRO can add internal notes (optional)
   └─> Private notes visible only to PRO/Admin
   
7a. PRO decides to APPROVE:
    ├─> PRO clicks [✓ Approve Request] button
    ├─> Approval confirmation dialog appears
    ├─> PRO can add approval notes (optional)
    ├─> PRO clicks [Confirm Approval]
    ├─> API call: POST /api/bookings/{id}/approve
    ├─> Booking status changed to "confirmed"
    ├─> Slot is digitally blocked
    ├─> Success message: "Booking approved and confirmed"
    ├─> Email notification sent to HOD
    └─> Request removed from pending list
    
7b. PRO decides to REJECT:
    ├─> PRO clicks [✗ Reject Request] button
    ├─> Rejection dialog appears
    ├─> PRO must enter rejection reason (required)
    ├─> PRO clicks [Confirm Rejection]
    ├─> API call: POST /api/bookings/{id}/reject
    ├─> Booking status changed to "rejected"
    ├─> Email notification sent to HOD with reason
    └─> Request removed from pending list
    
8. System updates pending count
   └─> "Pending Requests (2)" - decremented
   
9. PRO continues reviewing next request
   └─> Repeat from step 4
```

**Business Rules**:
- PRO can only approve if no conflicts exist
- Approval automatically confirms the booking
- Rejection requires a reason (minimum 10 characters)
- All actions are logged in audit trail
- Email notifications sent automatically

**Error Handling**:
- If conflict emerges during approval: "Booking conflict detected. Please review."
- If approval fails: "Unable to approve. Please try again."
- Network error: "Connection lost. Please check and retry."

---

### Flow 7: View All Bookings

**Actors**: PRO

**Steps**:
```
1. PRO clicks "All Bookings" tab
   └─> System loads all bookings (all statuses)
   
2. PRO sees calendar view (same as public)
   ├─> But includes pending bookings (different color)
   └─> Color legend shown
   
3. PRO can toggle between views:
   ├─> [📅 Calendar View] - Visual calendar
   └─> [📋 List View] - Tabular list
   
4. PRO applies filters:
   ├─> Status: All / Pending / Confirmed / Rejected / Cancelled
   ├─> Venue: All / Specific venue
   ├─> Date Range: Custom date range
   └─> Search: Event name or organizer
   
5. In List View, PRO sees:
   ├─> Sortable columns (Date, Event, Venue, Status)
   ├─> Quick action buttons per row
   └─> Export options (Excel, PDF)
   
6. PRO clicks on any booking
   └─> Full details modal opens (read-only or editable)
   
7. For confirmed bookings, PRO can:
   ├─> View full details
   ├─> Add internal notes
   └─> [Cancel Booking] if necessary
```

---

### Flow 8: View Complete History

**Actors**: PRO

**Steps**:
```
1. PRO clicks "History" tab
   └─> System loads complete booking history
   
2. PRO sets date range
   ├─> From Date: [Date Picker]
   └─> To Date: [Date Picker]
   
3. System displays paginated history
   ├─> Columns: Date, Event, Venue, Status, Created By, Approved By
   ├─> 20 records per page (default)
   └─> Pagination controls at bottom
   
4. PRO can export data:
   ├─> [📥 Export to Excel] button
   ├─> [📄 Export to PDF] button
   └─> File downloaded with selected date range
   
5. PRO clicks [View] on any record
   └─> Complete details shown including:
       ├─> All booking information
       ├─> Approval/rejection timeline
       ├─> Internal notes
       └─> Audit trail (if admin)
       
6. PRO uses history for:
   ├─> Reporting
   ├─> Analytics
   ├─> Conflict resolution
   └─> Audit purposes
```

---

### Flow 9: Cancel Confirmed Booking

**Actors**: PRO

**Prerequisites**: Booking must be in "confirmed" status

**Steps**:
```
1. PRO finds the booking to cancel
   └─> Via "All Bookings" tab or search
   
2. PRO clicks on the booking
   └─> Detail view opens
   
3. PRO clicks [Cancel Booking] button
   └─> Cancellation dialog appears
   
4. Dialog shows:
   ├─> Event details
   ├─> Warning: "This will free up the venue slot"
   └─> Reason input field (required)
   
5. PRO enters cancellation reason
   └─> Example: "Event postponed by organizer"
   
6. PRO clicks [Confirm Cancellation]
   ├─> API call: POST /api/bookings/{id}/cancel
   ├─> Booking status changed to "cancelled"
   ├─> Venue slot becomes available
   ├─> Email notification sent to HOD
   └─> Success message shown
   
7. Booking removed from calendar
   └─> Slot available for new bookings
```

---

## System Workflows

### Workflow 10: Conflict Detection

**Triggered**: When HOD selects venue, date, and time

**Steps**:
```
1. User completes venue, date, and time selection
   └─> onChange event triggered
   
2. System debounces (waits 500ms for final input)
   └─> Prevents excessive API calls
   
3. System makes API call:
   ├─> POST /api/bookings/check-availability
   ├─> Payload: { venue_id, booking_date, start_time, end_time }
   └─> Loading indicator shown
   
4. Backend executes conflict detection function:
   └─> SQL: check_booking_conflict()
   
5a. If NO conflict:
    ├─> API returns: { available: true, conflicts: [] }
    ├─> UI shows: ✓ "Venue available for selected time"
    └─> Submit button enabled
    
5b. If conflict EXISTS:
    ├─> API returns: { available: false, conflicts: [...] }
    ├─> UI shows: ⚠ "Venue already booked"
    ├─> Conflicting booking details displayed:
    │   ├─> Event name
    │   ├─> Time: 1:00 PM - 4:00 PM
    │   └─> Status: Confirmed
    ├─> Submit button disabled
    └─> Suggestion: "Please select different time or venue"
    
6. User adjusts time or venue
   └─> Repeat from step 1
```

**Technical Details**:
- Debounce delay: 500ms
- Maximum allowed overlap: 0 minutes (strict)
- Conflict check includes: pending, approved, confirmed bookings
- Excludes: rejected, cancelled bookings

---

### Workflow 11: File Upload

**Triggered**: When HOD uploads approval document

**Steps**:
```
1. HOD clicks [Choose File] button
   └─> OS file picker opens
   
2. HOD selects file
   └─> File validation begins (client-side)
   
3. Client-side validation:
   ├─> Check file type: PDF, JPG, JPEG, PNG only
   ├─> Check file size: <= 10MB
   └─> If valid: Show file name and size
   
4a. If validation passes:
    ├─> File stored temporarily in browser
    ├─> Preview icon shown (if image)
    └─> [Remove] button appears
    
4b. If validation fails:
    ├─> Error message shown
    ├─> "Invalid file type. Please upload PDF or image."
    └─> OR "File too large. Maximum size is 10MB."
    
5. When HOD submits form:
   ├─> File included in multipart/form-data request
   └─> API call: POST /api/bookings
   
6. Server-side upload:
   ├─> Validate file again (security)
   ├─> Generate unique filename
   ├─> Upload to Supabase Storage
   ├─> Get public URL
   └─> Store URL in database
   
7. If upload successful:
   ├─> File URL saved in booking.approval_letter_path
   └─> File accessible for PRO review
   
8. If upload fails:
   ├─> Booking creation rolled back
   └─> Error message shown to HOD
```

**Storage Structure**:
```
approval-letters/
  ├─ {user_id}/
  │   ├─ {booking_id}_approval.pdf
  │   ├─ {booking_id}_approval.jpg
  │   └─ ...
```

---

### Workflow 12: Email Notifications

**Triggered**: On booking status changes

**Events and Recipients**:

1. **Booking Request Submitted** (HOD creates request)
   - To: PRO
   - Subject: "New Booking Request - [Event Name]"
   - Content: Event details, HOD info, link to review

2. **Booking Approved** (PRO approves)
   - To: HOD who created request
   - Subject: "Booking Approved - [Event Name]"
   - Content: Confirmation, venue details, reminder

3. **Booking Rejected** (PRO rejects)
   - To: HOD who created request
   - Subject: "Booking Request Rejected - [Event Name]"
   - Content: Rejection reason, suggestion to modify and resubmit

4. **Booking Cancelled** (PRO cancels)
   - To: HOD who created request
   - Subject: "Booking Cancelled - [Event Name]"
   - Content: Cancellation reason, apology

**Email Template Structure**:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Professional email styling */
  </style>
</head>
<body>
  <div class="header">
    <h1>Venue Booking System</h1>
  </div>
  
  <div class="content">
    <h2>[Subject]</h2>
    <p>Dear [Recipient Name],</p>
    <p>[Message content]</p>
    
    <div class="details">
      <h3>Booking Details:</h3>
      <ul>
        <li>Event: [Event Name]</li>
        <li>Date: [Date]</li>
        <li>Time: [Time]</li>
        <li>Venue: [Venue Name]</li>
      </ul>
    </div>
    
    <p>[Call to action or additional info]</p>
  </div>
  
  <div class="footer">
    <p>This is an automated message from Venue Booking System.</p>
    <p>Please do not reply to this email.</p>
  </div>
</body>
</html>
```

---

### Workflow 13: Audit Logging

**Triggered**: On any booking modification

**Logged Actions**:
- Created
- Updated
- Status changed
- Approved
- Rejected
- Cancelled

**Log Entry Structure**:
```json
{
  "id": "log-uuid",
  "booking_id": "booking-uuid",
  "action": "approved",
  "performed_by": "user-uuid",
  "old_values": {
    "status": "pending",
    "approved_by": null
  },
  "new_values": {
    "status": "confirmed",
    "approved_by": "pro-uuid",
    "approved_at": "2026-03-05T16:30:00Z"
  },
  "notes": "Approved after document verification",
  "created_at": "2026-03-05T16:30:00Z"
}
```

**Triggered By**: Database trigger (automatic)

---

## Sequence Diagrams

### Booking Creation Sequence

```
HOD          Frontend         Backend         Database       Supabase
 |               |                |               |            Storage
 |---Login------>|                |               |              |
 |<--Token-------|                |               |              |
 |               |                |               |              |
 |--Fill Form--->|                |               |              |
 |               |                |               |              |
 |--Select       |                |               |              |
 |  Venue------->|                |               |              |
 |               |--Check         |               |              |
 |               |  Availability->|--Query------->|              |
 |               |                |<--Result------|              |
 |               |<--Available----|               |              |
 |               |  (✓ No         |               |              |
 |               |   conflict)    |               |              |
 |               |                |               |              |
 |--Upload       |                |               |              |
 |  Document---->|                |               |              |
 |               |--Upload--------|---------------|--Store------>|
 |               |                |               |<--URL--------|
 |               |                |               |              |
 |--Submit------>|--POST          |               |              |
 |               |  /bookings---->|--Insert------>|              |
 |               |                |<-Booking ID---|              |
 |               |                |--Log Action-->|              |
 |               |                |--Send Email-->|              |
 |               |<--Success------|               |              |
 |<--Confirmed---|                |               |              |
 |   Message     |                |               |              |
```

---

## State Transition Diagram

### Booking Status Lifecycle

```
                     ┌─────────────┐
                     │   PENDING   │ <-- HOD creates request
                     └──────┬──────┘
                            │
                ┌───────────┴───────────┐
                │                       │
         PRO Approves              PRO Rejects
                │                       │
                ▼                       ▼
        ┌──────────────┐        ┌─────────────┐
        │  CONFIRMED   │        │   REJECTED  │ (End state)
        └──────┬───────┘        └─────────────┘
               │
        PRO Cancels
               │
               ▼
        ┌──────────────┐
        │  CANCELLED   │ (End state)
        └──────────────┘
```

**State Descriptions**:
- **PENDING**: Initial state after HOD submission, awaiting PRO review
- **CONFIRMED**: Approved by PRO, slot digitally blocked, visible to public
- **REJECTED**: Declined by PRO with reason, cannot be modified
- **CANCELLED**: Previously confirmed booking cancelled by PRO

---

## Mobile Responsiveness Requirements

### Breakpoints

**Desktop** (>= 1024px):
- Full calendar month view
- Side-by-side form layout
- All features visible

**Tablet** (768px - 1023px):
- Calendar week view default
- Stacked form sections
- Collapsible sidebars

**Mobile** (< 768px):
- Calendar day/agenda view
- Single column forms
- Bottom sheet modals
- Hamburger menu

---

## Accessibility Requirements

- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Reader Support**: ARIA labels and roles
- **Color Contrast**: WCAG AA compliant (4.5:1 minimum)
- **Focus Indicators**: Visible keyboard focus
- **Error Messages**: Clear and descriptive
- **Form Labels**: All inputs labeled properly

---

**Document Version**: 1.0  
**Last Updated**: March 5, 2026  
**Maintained By**: Product Team
