from flask import Blueprint, render_template, redirect, url_for, flash, request, get_flashed_messages
from flask_login import current_user, login_required, login_user, logout_user
from model import db, Admin, Doctor, Department, Patient, Appointment, app
from functools import wraps
import os
from werkzeug.utils import secure_filename
from uuid import UUID
from sqlalchemy import func


doctor = Blueprint('doctor', __name__)


def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role_id != 2:  # Assuming 3 is the role_id for admins
            print(current_user.role_id)
            flash('You are not authorized to view this page', 'danger')
            return redirect(url_for('unauthorized'))  # Redirect to a general page if user is not an admin
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------- Doctor Section ------------------------------------------- #

@doctor.route('/unauthorized')
def unauthorized():
    return render_template('landing/error.html')



@doctor.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Doctor.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('You have been logged in successfully', 'success')
            return redirect(url_for('doctor.doctor_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('doctor.login'))
    return render_template('landing/doctor-login.html')


@doctor.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')

    return redirect(url_for('doctor.login'))


@doctor.route('/dashboard')
@login_required
@doctor_required
def doctor_dashboard():
    doctor_id = current_user.id
    user = Doctor.query.get(doctor_id)
    doctor_appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    patient_for_doctor = db.session.query(Appointment, Patient).join(Patient, Patient.id == Appointment.patient_id).filter(Appointment.doctor_id == doctor_id).all()
    
    # Query the database for the count of appointments per day
    appointments_per_day = db.session.query(func.date(Appointment.date), func.count(Appointment.id)).filter_by(doctor_id=doctor_id).group_by(func.date(Appointment.date)).all()

    # Convert the result to a dictionary
    appointments_per_day_dict = {str(date): count for date, count in appointments_per_day}
    
    return render_template('landing/doctor-dashboard.html', doctor=user, appointments=doctor_appointments, total_patients=patient_for_doctor, appointments_per_day=appointments_per_day_dict)


@doctor.route('/view-appoinments')
@login_required
@doctor_required
def view_appointments():
    doctor_id = current_user.id
    user = Doctor.query.get(doctor_id)
    doctor_appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    return render_template('landing/doctor-appointment.html', doctor=user, appointments=doctor_appointments)