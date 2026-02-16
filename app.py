from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)

DATABASE = 'appointments.db'

# Serve static files and home page
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Ensure the database is initialized when the app starts (including under Gunicorn)
init_db()

# Send confirmation email
def send_confirmation_email(name, email, phone, service, date, time):
    try:
        sender_email = os.environ.get('SMTP_EMAIL')
        sender_password = os.environ.get('SMTP_PASSWORD')
        
        # If credentials not set, just log to console
        if not sender_email or not sender_password:
            print(f"\n[EMAIL LOG] Email would be sent to {email}")
            print(f"Subject: Appointment Confirmation - Nisha Health Clinic")
            print("(To enable real emails, set SMTP_EMAIL and SMTP_PASSWORD environment variables)\n")
            return True
        
        subject = "Appointment Confirmation - Nisha Health Clinic"
        
        body = f"""Dear {name},

Thank you for booking an appointment at Nisha Health Clinic.

Appointment Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service: {service}
Date: {date}
Time: {time}
Phone: {phone}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We will contact you shortly via WhatsApp at {phone} to confirm the appointment.

If you need to reschedule, please call us at +977-9800000000

Best regards,
Nisha Health Clinic Team
"""
        
        # Create MIME message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"✗ Email authentication failed. Check your SMTP_EMAIL and SMTP_PASSWORD.")
        return False
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.json
        
        # Validate input
        required_fields = ['name', 'email', 'phone', 'service', 'date', 'time']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO appointments (name, email, phone, service, date, time, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (data['name'], data['email'], data['phone'], data['service'], 
              data['date'], data['time'], data.get('notes', '')))
        
        conn.commit()
        appointment_id = c.lastrowid
        conn.close()
        
        # Send confirmation email
        send_confirmation_email(
            data['name'], 
            data['email'], 
            data['phone'], 
            data['service'], 
            data['date'], 
            data['time']
        )
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'id': appointment_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM appointments ORDER BY date DESC, time DESC')
        appointments = [dict(row) for row in c.fetchall()]
        
        conn.close()
        return jsonify(appointments), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/appointments/<int:appointment_id>/confirm', methods=['PUT'])
def confirm_appointment(appointment_id):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('UPDATE appointments SET status = ? WHERE id = ?', ('confirmed', appointment_id))
        conn.commit()
        
        # Get appointment details
        c.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,))
        apt = c.fetchone()
        conn.close()
        
        if apt:
            print(f"Appointment {appointment_id} confirmed. WhatsApp notification would be sent to {apt[3]}")
        
        return jsonify({'message': 'Appointment confirmed'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Appointment deleted'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/appointments/stats', methods=['GET'])
def get_stats():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM appointments')
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'")
        confirmed = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
        pending = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total': total,
            'confirmed': confirmed,
            'pending': pending
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Server is running'}), 200

if __name__ == '__main__':
    print("Starting Nisha Health Clinic Appointment System...")
    print("Server running on http://localhost:5000")
    print("API endpoints:")
    print("  POST   /api/book-appointment")
    print("  GET    /api/appointments")
    print("  PUT    /api/appointments/<id>/confirm")
    print("  DELETE /api/appointments/<id>")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
