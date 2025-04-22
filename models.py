from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reports = db.relationship('Report', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20),
                       default='em_andamento')  # em_andamento, completo
    current_step = db.Column(
        db.String(50),
        default='documento')  # documento, preambulo, palavras_chave, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    document_path = db.Column(db.String(255))
    audio_path = db.Column(db.String(255))
    report_path = db.Column(db.String(255))
    sections = db.relationship('ReportSection',
                               backref='report',
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Report {self.title}>'


class ReportSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer,
                          db.ForeignKey('report.id'),
                          nullable=False)
    section_type = db.Column(db.String(50),
                             nullable=False)  # preambulo, palavras_chave, etc.
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ReportSection {self.section_type} for Report {self.report_id}>'


class AudioTranscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer,
                          db.ForeignKey('report.id'),
                          nullable=False)
    audio_path = db.Column(db.String(255), nullable=False)
    transcription = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    report = db.relationship('Report',
                             backref=db.backref('transcriptions', lazy=True))

    def __repr__(self):
        return f'<AudioTranscription for Report {self.report_id}>'


class DocumentExtraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer,
                          db.ForeignKey('report.id'),
                          nullable=False)
    document_path = db.Column(db.String(255), nullable=False)
    extracted_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    report = db.relationship('Report',
                             backref=db.backref('extractions', lazy=True))

    def __repr__(self):
        return f'<DocumentExtraction for Report {self.report_id}>'
