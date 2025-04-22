from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User
from app import db

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = db.session.query(User).filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        user = db.session.query(User).filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este email já está registrado. Por favor, use outro email.')

class NewLaudoForm(FlaskForm):
    title = StringField('Título do Laudo', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Criar Laudo')

class UploadProcessoForm(FlaskForm):
    processo_file = FileField('Arquivo do Processo (PDF)', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'Somente arquivos PDF são permitidos!')
    ])
    submit = SubmitField('Enviar Arquivo')

class UploadAudioForm(FlaskForm):
    audio_file = FileField('Arquivo de Áudio', validators=[
        FileRequired(),
        FileAllowed(['mp3', 'wav', 'ogg', 'm4a'], 'Somente arquivos de áudio são permitidos!')
    ])
    submit = SubmitField('Enviar Áudio')

class SecaoForm(FlaskForm):
    conteudo = TextAreaField('Conteúdo', validators=[DataRequired()])
    submit = SubmitField('Salvar Seção')
