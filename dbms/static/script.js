document.addEventListener('DOMContentLoaded', () => {
    // Load Doctors into dropdown
    fetch('/doctors')
        .then(response => response.json())
        .then(data => {
            const doctorsSelect = document.getElementById('appointment-doctor');
            data.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = doctor.name;
                doctorsSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading doctors:', error));

    // Load Patients into dropdown
    fetch('/patients')
        .then(response => response.json())
        .then(data => {
            const patientsSelect = document.getElementById('appointment-patient');
            data.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = patient.name;
                patientsSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading patients:', error));

    // Load Appointments List
    fetch('/appointments')
        .then(response => response.json())
        .then(data => {
            const appointmentsList = document.getElementById('appointments-list');
            appointmentsList.innerHTML = '';

            data.forEach(appt => {
                const div = document.createElement('div');
                div.classList.add('appointment-card');
                div.innerHTML = `
                    <strong>${appt.appointment_date} @ ${appt.appointment_time}</strong><br>
                    Doctor: ${appt.doctor_name} <br>
                    Patient: ${appt.patient_name}
                `;
                appointmentsList.appendChild(div);
            });
        })
        .catch(error => console.error('Error loading appointments:', error));
});

// Add Appointment
document.getElementById('add-appointment-form').addEventListener('submit', (e) => {
    e.preventDefault();

    const doctorId = document.getElementById('appointment-doctor').value;
    const patientId = document.getElementById('appointment-patient').value;
    const appointmentDate = document.getElementById('appointment-date').value;
    const appointmentTime = document.getElementById('appointment-time').value;

    fetch('/appointments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            doctor_id: doctorId,
            patient_id: patientId,
            appointment_date: appointmentDate,
            appointment_time: appointmentTime
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || 'Appointment added!');
        window.location.reload(); // Reload to see the new appointment
    })
    .catch(error => console.error('Error adding appointment:', error));
});