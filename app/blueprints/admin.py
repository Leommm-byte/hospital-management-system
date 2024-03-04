from flask import Blueprint, render_template, redirect, url_for, flash, request, get_flashed_messages
from flask_login import current_user, login_required, login_user, logout_user
from model import db, Admin, Doctor, Department, Patient, Appointment, app
from functools import wraps
import os
from werkzeug.utils import secure_filename
from uuid import UUID


admin = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role_id != 3:  # Assuming 3 is the role_id for admins
            print(current_user.role_id)
            flash('You are not authorized to view this page', 'danger')
            return redirect(url_for('unauthorized'))  # Redirect to a general page if user is not an admin
        return f(*args, **kwargs)
    return decorated_function



# ---------------------------------- Admin Section ------------------------------------------- #

@admin.route('/unauthorized')
def unauthorized():
    return render_template('landing/error.html')


@admin.route('/')
@login_required
@admin_required
def admin_dashboard():
    admin = Admin.query.filter_by(id=current_user.id).first()
    male_counts, female_counts = Appointment.get_gender_counts()
    top_departments = Department.get_top_departments()
    total_patients = Patient.get_unique_patient_count()
    total_doctors = Doctor.get_unique_doctor_count()
    total_appointments = Appointment.get_total_appointment_count()
    return render_template('admin/index.html', admin=admin, male_counts=male_counts, 
                           female_counts=female_counts, top_departments=top_departments, 
                           total_patients=total_patients, total_doctors=total_doctors,
                           total_appointments=total_appointments)


@admin.route('/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        password = request.form['password']
        role_id = 3
        user = Admin(first_name=first_name, last_name=last_name, email=email, gender=gender, phone_number=phone_number, role_id=role_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered', 'success')
        login_user(user)
        print(user.role_id)
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/signup.html')


@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Admin.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('admin/login.html')


@admin.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))


@admin.route('/add-doctor', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        gender = request.form['gender']
        bio = request.form['comments']
        role_id = 2

        department_id = request.form['department']

        # Handle the file upload
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_file = filename
        else:
            image_file = 'default.jpg'

        user = Doctor(first_name=first_name, last_name=last_name, bio=bio, image_file=image_file, email=email, gender=gender, phone_number=phone_number, role_id=role_id, department_id=department_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin.view_doctors'))
    
    departments = Department.query.all()
    admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('admin/add-doctor.html', departments=departments, admin=admin)


@admin.route('/add-department', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    if request.method == 'POST':
        department = request.form['department']
        department = Department(name=department)
        db.session.add(department)
        db.session.commit()
        flash('Department added successfully', 'success')
        return redirect(url_for('admin.add_department'))
    
    admin = Admin.query.filter_by(id=current_user.id).first()

    return render_template('admin/add-department.html', admin=admin)


@admin.route('/view-doctors')
@login_required
@admin_required
def view_doctors():
    doctors = Doctor.query.all()
    admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('admin/doctors.html', doctors=doctors, admin=admin)


@admin.route('/view-departments')
@login_required
@admin_required
def view_departments():
    departments = Department.query.all()
    admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('admin/departments.html', departments=departments, admin=admin)


# @admin.route('/doctor-profile/<string:id>')
# @login_required
# @admin_required
# def doctor_profile(id):
#     doctor_id = UUID(id)
#     doctor = Doctor.query.filter_by(id=doctor_id).first()
#     return render_template('admin/dr-profile.html', doctor=doctor)


@admin.route('/add-patient', methods=['GET', 'POST'])
@login_required
@admin_required
def add_patient():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        if Patient.query.filter_by(email=email).first() is not None:
            flash("You've already signed up with that email, log in instead!", "danger")
            return redirect(url_for("admin.add_patient"))

        phone_number = request.form['phone_number']
        password = request.form['password']
        age = request.form['age']
        health_status = request.form['health_status']
        blood_group = request.form['blood_group']
        height = request.form['height']
        weight = request.form['weight']
        gender = request.form['gender']
        role_id = 1

        # Handle the file upload
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_file = filename
        else:
            image_file = 'default.jpg'

        user = Patient(first_name=first_name, last_name=last_name, gender=gender, email=email, phone_number=phone_number, role_id=role_id, age=age, health_status=health_status, blood_group=blood_group, height=height, weight=weight, image_file=image_file)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.view_patients'))

    admin = Admin.query.filter_by(id=current_user.id).first()

    return render_template('admin/add-patient.html', admin=admin)


@admin.route('/view-patients')
@login_required
@admin_required
def view_patients():
    patients = Patient.query.all()
    admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('admin/patients.html', patients=patients, admin=admin)


@admin.route('/view-appointments')
@login_required
@admin_required
def view_appointments():
    appointments = Appointment.query.all()
    admin = Admin.query.filter_by(id=current_user.id).first()
    return render_template('admin/appointment.html', appointments=appointments, admin=admin)

