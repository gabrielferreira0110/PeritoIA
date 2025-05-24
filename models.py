from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    laudos = db.relationship('Laudo', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Laudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='incompleto')  # incompleto, completo
    current_stage = db.Column(db.String(50), default='inicio')  # para acompanhar o progresso
    
    # Relacionamentos
    secoes = db.relationship('LaudoSecao', backref='laudo', lazy='dynamic', cascade="all, delete-orphan")
    arquivos = db.relationship('Arquivo', backref='laudo', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Laudo {self.title}>'

class LaudoSecao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    laudo_id = db.Column(db.Integer, db.ForeignKey('laudo.id'), nullable=False)
    secao_tipo = db.Column(db.String(50), nullable=False)  # preambulo, palavras_chave, etc.
    conteudo = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LaudoSecao {self.secao_tipo} para Laudo {self.laudo_id}>'

class Arquivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    laudo_id = db.Column(db.Integer, db.ForeignKey('laudo.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    filetype = db.Column(db.String(50), nullable=False)  # documento, audio
    processed = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Para áudios
    transcricao = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Arquivo {self.filename} para Laudo {self.laudo_id}>'
