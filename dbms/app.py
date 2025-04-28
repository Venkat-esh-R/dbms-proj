import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

# Load environment variables from .env
load_dotenv()

# Setup Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Database path
DATABASE_PATH = os.getenv("DATABASE_PATH") or 'hospital_management.db'

# Ensure DB and tables exist
def create_db_if_not_exists():
    if not os.path.exists(DATABASE_PATH):
        logging.info("Database file does not exist. Creating...")
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        with open('hosp.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        logging.info("Database and tables created successfully.")
    else:
        logging.info("Database already exists.")

create_db_if_not_exists()

# DB connection helper
def get_db_connection():
    return sqlite3.connect(DATABASE_PATH, check_same_thread=False, isolation_level=None)

# ---------- Page Routes ----------
@app.route('/')
def index_page():
    logging.info("Serving index page")
    return render_template('index.html')

@app.route('/doctors')
def doctors_page():
    logging.info("Serving doctors page")
    return render_template('doctors.html')

@app.route('/patients')
def patients_page():
    logging.info("Serving patients page")
    return render_template('patients.html')

@app.route('/appointments')
def appointments_page():
    logging.info("Serving appointments page")
    return render_template('appointments.html')


# ---------- API Routes ----------

# --- Doctors API ---
@app.route('/doctors', methods=['GET', 'POST'])
def doctors():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM doctors")
        doctors_list = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in doctors_list])

    elif request.method == 'POST':
        try:
            data = request.get_json()
            name = data.get('name')
            specialty = data.get('specialty')
            email = data.get('email')

            cursor.execute("INSERT INTO doctors (name, specialty, email) VALUES (?, ?, ?)",
                        (name, specialty, email))
            conn.commit()
            return jsonify({'message': 'Doctor added successfully'}), 201
        except Exception as e:
            print("Error adding doctor:", e)
            return jsonify({'error': 'Failed to add doctor'}), 500
        finally:
            conn.close()


@app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    logging.info(f"Deleting doctor with ID: {doctor_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Doctor deleted successfully'})


# --- Patients API ---
@app.route('/patients', methods=['GET', 'POST'])
def api_patients():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        logging.info("Fetching list of patients")
        cursor.execute("SELECT * FROM patients")
        patients_list = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in patients_list])

    elif request.method == 'POST':
        data = request.get_json()
        logging.info(f"Received request to add patient: {data}")
        try:
            cursor.execute("INSERT INTO patients (name, email, phone) VALUES (?, ?, ?)",
                           (data['name'], data['email'], data['phone']))
            conn.commit()
            return jsonify({'message': 'Patient added successfully'}), 201
        except Exception as e:
            logging.error(f"Error adding patient: {e}")
            return jsonify({'error': 'Failed to add patient'}), 500
        finally:
            conn.close()

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    logging.info(f"Deleting patient with ID: {patient_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Patient deleted successfully'})


# --- Appointments API ---
@app.route('/api/appointments', methods=['GET', 'POST'])
def api_appointments():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        logging.info("Fetching list of appointments with doctor/patient details")
        cursor.execute("SELECT * FROM appointments")
        appointments_list = cursor.fetchall()

        detailed_appointments = []
        for appt in appointments_list:
            cursor.execute("SELECT name FROM doctors WHERE id = ?", (appt['doctor_id'],))
            doctor = cursor.fetchone()
            doctor_name = doctor['name'] if doctor else "Unknown Doctor"

            cursor.execute("SELECT name FROM patients WHERE id = ?", (appt['patient_id'],))
            patient = cursor.fetchone()
            patient_name = patient['name'] if patient else "Unknown Patient"

            detailed_appointments.append({
                **dict(appt),
                'doctor_name': doctor_name,
                'patient_name': patient_name
            })

        conn.close()
        return jsonify(detailed_appointments)

    elif request.method == 'POST':
        data = request.get_json()
        logging.info(f"Received request to add appointment: {data}")
        try:
            cursor.execute("""
                INSERT INTO appointments (doctor_id, patient_id, appointment_date, appointment_time)
                VALUES (?, ?, ?, ?)
            """, (data['doctor_id'], data['patient_id'], data['appointment_date'], data['appointment_time']))
            conn.commit()
            return jsonify({'message': 'Appointment added successfully'}), 201
        except Exception as e:
            logging.error(f"Error adding appointment: {e}")
            return jsonify({'error': 'Failed to add appointment'}), 500
        finally:
            conn.close()

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    logging.info(f"Deleting appointment with ID: {appointment_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Appointment deleted successfully'})


if __name__ == '__main__':
    logging.info("Starting Flask app on http://localhost:5000")
    app.run(debug=True)
