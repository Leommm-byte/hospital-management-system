from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, desc
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = f'{os.environ.get("SECRET_KEY")}'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://hospitalmanagement.postgres.database.azure.com:5432/hosmanage?user=hms&password={os.environ.get("PGPASSWORD")}&sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class User(UserMixin, db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    image_file = db.Column(db.String(256), nullable=False, default='default.png')
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(User):
    age = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=True)
    health_status = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(3), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    @classmethod
    def get_unique_patient_count(cls):
        return db.session.query(cls).count()

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    doctors = db.relationship('Doctor', backref='department', lazy=True)

    @classmethod
    def get_top_departments(cls, limit=4):

        # Fetch the top departments with the highest patient count
        departments = db.session.query(cls, func.count(Appointment.id)).join(Doctor, Doctor.department_id == cls.id).join(Appointment, Appointment.doctor_id == Doctor.id).group_by(cls.id).order_by(desc(func.count(Appointment.id))).limit(limit).all()

        # Return a list of department names and patient counts
        return [(department.name, count) for department, count in departments]

class Doctor(User):
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

    @classmethod
    def get_unique_doctor_count(cls):
        return db.session.query(cls).count()

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    time = db.Column(db.Time, nullable=False, default=datetime.utcnow().time())
    patient_id = db.Column(UUID(as_uuid=True), db.ForeignKey('patient.id'), nullable=False, default=uuid.uuid4)
    doctor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('doctor.id'), nullable=False, default=uuid.uuid4)
    comment = db.Column(db.Text, nullable=True)

    @classmethod
    def get_gender_counts(cls):
        male_counts = db.session.query(cls.date, func.count(cls.id)).join(Patient, cls.patient_id == Patient.id).filter(Patient.gender == 'Male').group_by(cls.date).all()
        female_counts = db.session.query(cls.date, func.count(cls.id)).join(Patient, cls.patient_id == Patient.id).filter(Patient.gender == 'Female').group_by(cls.date).all()
        return [(str(date), count) for date, count in male_counts], [(str(date), count) for date, count in female_counts]
    
    @classmethod
    def get_total_appointment_count(cls):
        return db.session.query(cls).count()

class Admin(User):
    # Add any additional fields for Admin here
    pass

with app.app_context():
    db.create_all()


def upload_file_to_azure(file, filename):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING_PREFIX') + os.environ.get('AZURE_STORAGE_CONNECTION_STRING_SUFFIX'))
        blob_client = blob_service_client.get_blob_client(os.environ.get('AZURE_CONTAINER_NAME'), filename)
        blob_client.upload_blob(file)
        # Generate blob url and return
        blob_url = blob_client.url
        return blob_url
    except Exception as e:
        print(e)
        return None