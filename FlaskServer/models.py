
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to logs
    logs = db.relationship('VideoLog', backref='user', lazy=True)

class VideoLog(db.Model):
    __tablename__ = 'video_logs'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True) # Nullable for anonymous uploads
    filename = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    classification = db.Column(db.String(50), nullable=False)
    people_count = db.Column(db.Integer, default=0)
    report_summary = db.Column(db.Text, nullable=True)
    severity_score = db.Column(db.Integer, default=0)
