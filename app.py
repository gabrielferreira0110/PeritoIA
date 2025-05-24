import os
import logging
from datetime import datetime, timedelta

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///perito_ia.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Upload configuration
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32MB max upload
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Import extensions
from extensions import db, login_manager

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Import models (after initializing extensions)
from models import User

# Configure user loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create all database tables
with app.app_context():
    db.create_all()

# Routes

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/test')
def test():
    return '<h1>Perito IA Test Page</h1><p>If you can see this, the Flask application is working correctly.</p>'

@app.route('/dashboard')
@login_required
def dashboard():
    # Mock data for demonstration
    laudos = [
        {'id': 1, 'title': 'Laudo de Perícia Criminal', 'date': '2025-05-20', 'status': 'completo', 
         'created_at': datetime.now() - timedelta(days=5), 'updated_at': datetime.now() - timedelta(hours=12)},
        {'id': 2, 'title': 'Análise de Local de Crime', 'date': '2025-05-22', 'status': 'incompleto',
         'created_at': datetime.now() - timedelta(days=3), 'updated_at': datetime.now() - timedelta(hours=2),
         'current_stage': 'Coleta de Evidências'},
        {'id': 3, 'title': 'Exame Pericial', 'date': '2025-05-23', 'status': 'incompleto',
         'created_at': datetime.now() - timedelta(days=1), 'updated_at': datetime.now() - timedelta(minutes=30),
         'current_stage': 'Análise Preliminar'}
    ]
    return render_template('dashboard.html', laudos=laudos)

@app.route('/laudos')
@login_required
def laudo_list():
    # Mock data for demonstration
    laudos = [
        {'id': 1, 'title': 'Laudo de Perícia Criminal', 'date': '2025-05-20', 'status': 'completo', 
         'created_at': datetime.now() - timedelta(days=5), 'updated_at': datetime.now() - timedelta(hours=12)},
        {'id': 2, 'title': 'Análise de Local de Crime', 'date': '2025-05-22', 'status': 'incompleto',
         'created_at': datetime.now() - timedelta(days=3), 'updated_at': datetime.now() - timedelta(hours=2),
         'current_stage': 'Coleta de Evidências'},
        {'id': 3, 'title': 'Exame Pericial', 'date': '2025-05-23', 'status': 'incompleto',
         'created_at': datetime.now() - timedelta(days=1), 'updated_at': datetime.now() - timedelta(minutes=30),
         'current_stage': 'Análise Preliminar'},
        {'id': 4, 'title': 'Laudo de Balística', 'date': '2025-05-19', 'status': 'completo', 
         'created_at': datetime.now() - timedelta(days=7), 'updated_at': datetime.now() - timedelta(days=1)},
        {'id': 5, 'title': 'Análise de Impressões Digitais', 'date': '2025-05-18', 'status': 'completo', 
         'created_at': datetime.now() - timedelta(days=8), 'updated_at': datetime.now() - timedelta(days=2)},
        {'id': 6, 'title': 'Exame de DNA', 'date': '2025-05-24', 'status': 'incompleto',
         'created_at': datetime.now() - timedelta(hours=6), 'updated_at': datetime.now() - timedelta(minutes=15),
         'current_stage': 'Coleta de Amostras'}
    ]
    return render_template('laudo_list.html', laudos=laudos)

@app.route('/laudos/<int:laudo_id>')
@login_required
def laudo_view(laudo_id):
    # Mock data for demonstration
    laudos_data = {
        1: {
            'id': 1, 
            'title': 'Laudo de Perícia Criminal', 
            'date': '2025-05-20', 
            'status': 'completo',
            'created_at': datetime.now() - timedelta(days=5),
            'updated_at': datetime.now() - timedelta(hours=12),
            'client': 'Delegacia de Polícia Civil', 
            'case_number': '2025/0123', 
            'perito': 'Dr. Carlos Silva',
            'deadline': datetime.now() + timedelta(days=5),
            'progress': 100
        },
        2: {
            'id': 2, 
            'title': 'Análise de Local de Crime', 
            'date': '2025-05-22', 
            'status': 'incompleto',
            'created_at': datetime.now() - timedelta(days=3),
            'updated_at': datetime.now() - timedelta(hours=2),
            'current_stage': 'Coleta de Evidências', 
            'progress': 35,
            'client': 'Ministério Público', 
            'case_number': '2025/0456', 
            'perito': 'Dra. Ana Oliveira',
            'deadline': datetime.now() + timedelta(days=10)
        }
    }
    
    # Mapping for section titles
    secoes_titulos = {
        'preambulo': 'Preâmbulo',
        'palavras_chave': 'Palavras-chave',
        'apresentacao_demanda': 'Apresentação da Demanda',
        'objeto_pericia': 'Objeto da Perícia',
        'metodologia': 'Metodologia',
        'descricao': 'Descrição',
        'discussao': 'Discussão',
        'conclusao': 'Conclusão'
    }
    
    # Mock secoes data for demonstration
    if laudo_id == 1:
        secoes = [
            {'secao_tipo': 'preambulo', 'completed': True, 'conteudo': 'Este laudo pericial foi elaborado a pedido da autoridade policial para esclarecer as circunstâncias do crime ocorrido em 15/05/2025.'},
            {'secao_tipo': 'palavras_chave', 'completed': True, 'conteudo': 'Homicídio, arma de fogo, balística, medicina legal'},
            {'secao_tipo': 'apresentacao_demanda', 'completed': True, 'conteudo': 'A demanda consiste na análise pericial do local do crime e do corpo da vítima para determinar a causa da morte e coletar evidências que possam auxiliar na identificação do autor.'},
            {'secao_tipo': 'objeto_pericia', 'completed': True, 'conteudo': 'O objeto da perícia é o corpo da vítima encontrado no local do crime, bem como os vestígios materiais presentes no ambiente.'},
            {'secao_tipo': 'metodologia', 'completed': True, 'conteudo': 'Foram utilizados métodos de fotografia forense, coleta de impressões digitais, exame de balística e análise de DNA para a realização desta perícia.'},
            {'secao_tipo': 'descricao', 'completed': False},
            {'secao_tipo': 'discussao', 'completed': False},
            {'secao_tipo': 'conclusao', 'completed': False}
        ]
    else:
        secoes = [
            {'secao_tipo': 'preambulo', 'completed': True, 'conteudo': 'Este laudo pericial foi elaborado a pedido da autoridade policial para esclarecer as circunstâncias do roubo ocorrido na residência localizada na Rua das Flores, 123.'},
            {'secao_tipo': 'palavras_chave', 'completed': True, 'conteudo': 'Roubo, residência, arrombamento, impressões digitais'},
            {'secao_tipo': 'apresentacao_demanda', 'completed': True, 'conteudo': 'A demanda consiste na análise pericial do local do crime para determinar o modo de entrada dos criminosos e coletar evidências que possam auxiliar na identificação dos autores.'},
            {'secao_tipo': 'objeto_pericia', 'completed': False},
            {'secao_tipo': 'metodologia', 'completed': False},
            {'secao_tipo': 'descricao', 'completed': False},
            {'secao_tipo': 'discussao', 'completed': False},
            {'secao_tipo': 'conclusao', 'completed': False}
        ]
    
    # Get the laudo or return 404
    laudo = laudos_data.get(laudo_id)
    if not laudo:
        flash('Laudo não encontrado', 'danger')
        return redirect(url_for('laudo_list'))
        
    return render_template('laudo_view.html', laudo=laudo, secoes=secoes, secoes_titulos=secoes_titulos)

@app.route('/laudos/create', methods=['GET', 'POST'])
@login_required
def laudo_create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        case_number = request.form.get('case_number')
        
        if not title:
            flash('O título do laudo é obrigatório', 'danger')
            return render_template('laudo_create.html')
        
        # Em uma aplicação real, aqui seria feita a inserção no banco de dados
        flash('Laudo criado com sucesso!', 'success')
        return redirect(url_for('laudo_list'))
    
    return render_template('laudo_create.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        # Check password
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
