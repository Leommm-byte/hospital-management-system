from flask import Flask, request, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from .model import Patient, Admin, Doctor, Department, Appointment, db, app
import secrets
from PIL import Image
from werkzeug.utils import secure_filename
from functools import wraps
from .blueprints.admin import admin
from .blueprints.doctors import doctor
from uuid import UUID
from datetime import datetime

load_dotenv()


upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(upload_dir, exist_ok=True)

app.config['UPLOAD_FOLDER'] = upload_dir

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = UUID(user_id)
    except ValueError:
        return None
    for Model in [Patient, Doctor, Admin]:
        user = Model.query.get(user_id)
        if user:
            return user
    return None


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (400, 400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role_id != 1:  # Assuming 3 is the role_id for admins
            print(current_user.role_id)
            flash('You are not authorized to view this page', 'danger')
            return redirect(url_for('unauthorized'))  # Redirect to a general page if user is not an admin
        return f(*args, **kwargs)
    return decorated_function



# ---------------------------- Patient Section ---------------------------- #

@app.route('/unauthorized')
def unauthorized():
    return render_template('landing/error.html')


@app.route('/')
def home():
    return render_template('landing/index-three.html')


@app.route('/dashboard')
@login_required
@patient_required
def index():
    patient_id = current_user.id
    user = Patient.query.get(patient_id)
    patient_appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return render_template('landing/patient-dashboard.html', patient=user, appointments=patient_appointments)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
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
            image_file = 'default.png'

        user = Patient(first_name=first_name, last_name=last_name, gender=gender, email=email, phone_number=phone_number, role_id=role_id, age=age, health_status=health_status, blood_group=blood_group, height=height, weight=weight, image_file=image_file)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered', 'success')
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('landing/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Patient.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('landing/login.html')


@app.route('/logout')
@login_required
@patient_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
@patient_required
def profile():
    return render_template('profile.html')


@app.route('/update-profile', methods=['GET', 'POST'])
@login_required
@patient_required
def update_profile():
    if request.method == 'POST':
        user = Patient.query.get(current_user.id)
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        user.bio = request.form['bio']
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    return render_template('update-profile.html')

# def update_profile():
#     form = UpdateProfileForm()
#     if form.validate_on_submit():
#         if form.picture.data:
#             picture_file = save_picture(form.picture.data)
#             current_user.image_file = picture_file
#         current_user.bio = form.bio.data
#         db.session.commit()
#         flash('Your profile has been updated!')
#         return redirect(url_for('profile'))
#     elif request.method == 'GET':
#         form.bio.data = current_user.bio
#     image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
#     return render_template('update_profile.html', title='Update Profile', image_file=image_file, form=form)


@app.route('/book-appointment', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment():
    if request.method == 'POST':

        doctor_id = request.form['doctor']
        if not doctor_id:
            doctor_id = None
        else:
            doctor_id = UUID(doctor_id)

        patient_id = current_user.id
        appointment_type = request.form['appointment_type']
        comments = request.form['comments']
        # status = 'pending'
        
        if appointment_type == 'online':
            appointment_date = request.form['date']
            appointment_time = request.form['time']

            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()

            appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, date=appointment_date, time=appointment_time, comment=comments)
        else:
            appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, comment=comments)

        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('index'))

    doctors = Doctor.query.all()
    patient_id = current_user.id
    user = Patient.query.get(patient_id)

    return render_template('landing/booking-appointment.html', doctors=doctors, patient=user) 





app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(doctor, url_prefix='/doctor')


if __name__ == '__main__':
    app.run(debug=True)
