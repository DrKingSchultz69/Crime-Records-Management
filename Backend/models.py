from app import db
from datetime import datetime
import uuid

class Location(db.Model):
    __tablename__ = 'locations'
    location_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    city = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    police_station = db.Column(db.String(255))
    district = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PoliceStation(db.Model):
    __tablename__ = 'police_stations'
    station_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    district = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    officer_in_charge = db.Column(db.String(255), nullable=False)
    jurisdiction = db.Column(db.String(255), nullable=False)
    department_categories = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PoliceDepartment(db.Model):
    __tablename__ = 'police_departments'
    department_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    head_officer = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PoliceRank(db.Model):
    __tablename__ = 'police_ranks'
    rank_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    abbreviation = db.Column(db.String(50), nullable=False)
    category = db.Column(db.Enum('IPS', 'SPS', 'Non-Gazetted'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    raw_user_meta_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    roles = db.relationship('UserRole', backref='user', cascade='all, delete-orphan')

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255))
    badge_number = db.Column(db.String(100))
    rank_id = db.Column(db.BigInteger, db.ForeignKey('police_ranks.rank_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.Enum('admin', 'moderator', 'officer', 'user'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class CrimeRecord(db.Model):
    __tablename__ = 'crime_records'
    crime_id = db.Column(db.BigInteger, autoincrement=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    crime_type = db.Column(db.String(255), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    location_id = db.Column(db.BigInteger, db.ForeignKey('locations.location_id'), nullable=False)
    department_category = db.Column(db.String(255))
    progress = db.Column(db.Integer)
    priority = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical'), default='Medium')
    status = db.Column(db.Enum('open', 'closed'), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    location = db.relationship('Location', backref='crime_records')
    investigations = db.relationship('Investigation', backref='crime_record', cascade='all, delete-orphan')
    suspects = db.relationship('Suspect', backref='crime_record', cascade='all, delete-orphan')
    victims = db.relationship('Victim', backref='crime_record', cascade='all, delete-orphan')
    witnesses = db.relationship('Witness', backref='crime_record', cascade='all, delete-orphan')
    evidence = db.relationship('Evidence', backref='crime_record', cascade='all, delete-orphan')

class Investigation(db.Model):
    __tablename__ = 'investigations'
    investigation_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    officer_id = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=False)
    crime_id = db.Column(db.String(36), db.ForeignKey('crime_records.id'), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    progress_notes = db.Column(db.Text)
    assigned_department = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Report(db.Model):
    __tablename__ = 'reports'
    report_id = db.Column(db.BigInteger, autoincrement=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('profiles.id'))
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Suspect(db.Model):
    __tablename__ = 'suspects'
    suspect_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    crime_id = db.Column(db.String(36), db.ForeignKey('crime_records.id'), nullable=False)
    address = db.Column(db.Text)
    prior_records = db.Column(db.Text)
    status = db.Column(db.Enum('Wanted', 'In Custody', 'Released', 'Unknown'), default='Unknown')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Victim(db.Model):
    __tablename__ = 'victims'
    victim_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)
    statement = db.Column(db.Text)
    crime_id = db.Column(db.String(36), db.ForeignKey('crime_records.id'), nullable=False)
    address = db.Column(db.Text)
    case_followup = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Witness(db.Model):
    __tablename__ = 'witnesses'
    witness_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    contact_info = db.Column(db.String(255))
    crime_id = db.Column(db.String(36), db.ForeignKey('crime_records.id'), nullable=False)
    address = db.Column(db.Text)
    credibility_assessment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Evidence(db.Model):
    __tablename__ = 'evidence'
    evidence_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    description = db.Column(db.Text, nullable=False)
    evidence_type = db.Column(db.String(255), nullable=False)
    crime_id = db.Column(db.String(36), db.ForeignKey('crime_records.id'), nullable=False)
    collection_date = db.Column(db.DateTime)
    storage_location = db.Column(db.String(255))
    chain_of_custody = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    complaint_id = db.Column(db.BigInteger, autoincrement=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    complainant_name = db.Column(db.String(255), nullable=False)
    complainant_contact = db.Column(db.String(255), nullable=False)
    complaint_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Enum('pending', 'resolved', 'Submitted', 'Under Review', 'Assigned', 'In Progress', 'Rejected', 'False'), default='pending')
    reference_number = db.Column(db.String(255), unique=True, nullable=False)
    progress = db.Column(db.Integer, default=0)
    assigned_to = db.Column(db.String(36), db.ForeignKey('profiles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    preference = db.Column(db.JSON)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Statistic(db.Model):
    __tablename__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    month = db.Column(db.String(20))
    total_crimes = db.Column(db.Integer)
    resolved_complaints = db.Column(db.Integer)
