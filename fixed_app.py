from flask import Flask, render_template, redirect, url_for, flash, request, session
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "development_secret_key"

# Dados mock para demonstração
laudos = [
    {'id': 1, 'title': 'Laudo de Perícia Criminal', 'date': '2025-05-20', 'status': 'completo', 
     'created_at': datetime.now() - timedelta(days=5), 'updated_at': datetime.now() - timedelta(hours=12),
     'progress': 100},
    {'id': 2, 'title': 'Análise de Local de Crime', 'date': '2025-05-22', 'status': 'incompleto',
     'created_at': datetime.now() - timedelta(days=3), 'updated_at': datetime.now() - timedelta(hours=2),
     'current_stage': 'Coleta de Evidências', 'progress': 35},
    {'id': 3, 'title': 'Exame Pericial', 'date': '2025-05-23', 'status': 'incompleto',
     'created_at': datetime.now() - timedelta(days=1), 'updated_at': datetime.now() - timedelta(minutes=30),
     'current_stage': 'Análise Preliminar', 'progress': 20}
]

# Rotas
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Autenticação simplificada para demonstração
        if username == 'lucas' and password == '011326':
            session['user'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', laudos=laudos[:3], user=session['user'])

@app.route('/laudos')
def laudo_list():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('laudo_list.html', laudos=laudos, user=session['user'])

@app.route('/laudos/<int:laudo_id>')
def laudo_view(laudo_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Buscar o laudo pelo ID
    laudo = next((l for l in laudos if l['id'] == laudo_id), None)
    if not laudo:
        flash('Laudo não encontrado', 'danger')
        return redirect(url_for('laudo_list'))
    
    # Dados mock para as seções do laudo
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
    
    return render_template('laudo_view.html', laudo=laudo, secoes=secoes, secoes_titulos=secoes_titulos, user=session['user'])

@app.route('/laudos/create', methods=['GET', 'POST'])
def laudo_create():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        case_number = request.form.get('case_number')
        
        if not title:
            flash('O título do laudo é obrigatório', 'danger')
            return render_template('laudo_create.html', user=session['user'])
        
        # Em uma aplicação real, aqui seria feita a inserção no banco de dados
        flash('Laudo criado com sucesso!', 'success')
        return redirect(url_for('laudo_list'))
    
    return render_template('laudo_create.html', user=session['user'])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
