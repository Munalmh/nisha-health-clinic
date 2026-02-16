# Nisha Health Clinic - Online Appointment System

## Features

### 1. **User Booking Interface** (appointments.html)
- Fill out appointment form with:
  - Name, Email, Phone
  - Service selection (General Checkup, Laboratory Tests, Emergency Care, Consultation)
  - Preferred date & time
  - Additional notes
- Real-time form validation
- Confirmation alerts

### 2. **Admin Dashboard** (admin.html)
- View all appointments in a table format
- Filter by email and service
- Display appointment statistics:
  - Total appointments
  - Confirmed appointments
  - Pending appointments
- Actions:
  - Confirm pending appointments
  - Delete appointments
  - Auto-refresh every 30 seconds

### 3. **Backend API** (app.py)
- Flask server running on port 5000
- SQLite database for data persistence
- Endpoints:
  - `POST /api/book-appointment` - Create new appointment
  - `GET /api/appointments` - Get all appointments
  - `PUT /api/appointments/<id>/confirm` - Confirm appointment
  - `DELETE /api/appointments/<id>` - Delete appointment
  - `GET /api/appointments/stats` - Get statistics

### 4. **Notifications**
- Email confirmation (configured to use SMTP)
- WhatsApp notification trigger (console log for demo)
- Status updates (pending → confirmed)

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
python app.py
```
Server will run on http://localhost:5000

### 3. Access the Application
- Website: http://localhost:8000
- Book Appointment: http://localhost:8000/appointments.html
- Admin Dashboard: http://localhost:8000/admin.html

## Email Configuration (Optional)
To enable actual email sending, set environment variables:
```bash
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-app-password
```

## Database
Appointments are stored in `appointments.db` (SQLite database)
- Automatically created on first run
- Stores: name, email, phone, service, date, time, notes, status, created_at

## API Response Examples

### Book Appointment
```json
POST /api/book-appointment
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+9779800000000",
  "service": "General Checkup",
  "date": "2026-02-20",
  "time": "10:30",
  "notes": "First time patient"
}
```

### Get Appointments
```json
GET /api/appointments
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+9779800000000",
    "service": "General Checkup",
    "date": "2026-02-20",
    "time": "10:30",
    "notes": "First time patient",
    "status": "pending",
    "created_at": "2026-02-16 10:15:30"
  }
]
```

## Features Summary

✓ User-friendly appointment booking form
✓ Real-time form validation
✓ Unique appointment confirmation with ID
✓ Admin dashboard with filtering and sorting
✓ Email notification system (ready for SMTP configuration)
✓ WhatsApp notification triggers
✓ Status management (pending/confirmed)
✓ Complete appointment history
✓ Responsive design for mobile and desktop
✓ Database persistence
✓ CORS enabled for API access
