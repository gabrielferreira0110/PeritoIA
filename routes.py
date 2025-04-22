import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from docx import Document
from io import BytesIO

from app import app, db
from models import User, Laudo, LaudoSecao, Arquivo
from forms import LoginForm, RegistrationForm, NewLaudoForm, UploadProcessoForm, UploadAudioForm, SecaoForm
from openai_utils import generate_section_content, transcribe_audio_file
from document_processor import extract_information_from_pdf
from report_generator import generate_docx_report

# Rotas de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    return render_template('login.html', title='Entrar', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro realizado com sucesso! Você já pode fazer login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Registro', form=form)

# Rotas Principais
@app.route('/')
def index():
    return render_template('index.html', title='Perito IA - Sistema de Laudos Periciais')

@app.route('/dashboard')
@login_required
def dashboard():
    laudos = Laudo.query.filter_by(user_id=current_user.id).order_by(Laudo.updated_at.desc()).all()
    return render_template('dashboard.html', title='Painel do Perito', laudos=laudos)

@app.route('/laudos')
@login_required
def laudo_list():
    laudos = Laudo.query.filter_by(user_id=current_user.id).order_by(Laudo.updated_at.desc()).all()
    return render_template('laudo_list.html', title='Meus Laudos', laudos=laudos)

@app.route('/laudos/novo', methods=['GET', 'POST'])
@login_required
def laudo_create():
    form = NewLaudoForm()
    if form.validate_on_submit():
        laudo = Laudo(
            title=form.title.data,
            user_id=current_user.id,
            status='incompleto',
            current_stage='inicio'
        )
        db.session.add(laudo)
        db.session.commit()
        
        # Criar seções padrão para o laudo
        secoes = [
            'preambulo', 'palavras_chave', 'apresentacao_demanda', 
            'objeto_pericia', 'metodologia', 'descricao', 
            'discussao', 'conclusao'
        ]
        
        for secao in secoes:
            nova_secao = LaudoSecao(
                laudo_id=laudo.id,
                secao_tipo=secao,
                conteudo='',
                completed=False
            )
            db.session.add(nova_secao)
        
        db.session.commit()
        flash('Novo laudo criado com sucesso!', 'success')
        return redirect(url_for('laudo_view', laudo_id=laudo.id))
    
    return render_template('laudo_create.html', title='Novo Laudo', form=form)

@app.route('/laudos/<int:laudo_id>')
@login_required
def laudo_view(laudo_id):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    secoes = LaudoSecao.query.filter_by(laudo_id=laudo.id).all()
    arquivos = Arquivo.query.filter_by(laudo_id=laudo.id).all()
    
    return render_template('laudo_view.html', title=laudo.title, 
                          laudo=laudo, secoes=secoes, arquivos=arquivos)

@app.route('/laudos/<int:laudo_id>/upload-processo', methods=['GET', 'POST'])
@login_required
def upload_processo(laudo_id):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    form = UploadProcessoForm()
    
    if form.validate_on_submit():
        file = form.processo_file.data
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # Salvar referência do arquivo no banco de dados
        arquivo = Arquivo(
            laudo_id=laudo.id,
            filename=filename,
            filepath=filepath,
            filetype='documento',
            processed=False
        )
        db.session.add(arquivo)
        
        # Atualizar estágio do laudo
        laudo.current_stage = 'documento_anexado'
        db.session.commit()
        
        # Processar o documento PDF para extrair informações
        try:
            extracted_info = extract_information_from_pdf(filepath)
            
            # Marcar o arquivo como processado
            arquivo.processed = True
            db.session.commit()
            
            flash('Documento processado com sucesso!', 'success')
            return redirect(url_for('laudo_view', laudo_id=laudo.id))
        except Exception as e:
            flash(f'Erro ao processar o documento: {str(e)}', 'danger')
    
    return render_template('upload_process.html', title='Anexar Processo', form=form, laudo=laudo)

@app.route('/laudos/<int:laudo_id>/upload-audio', methods=['GET', 'POST'])
@login_required
def upload_audio(laudo_id):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    form = UploadAudioForm()
    
    if form.validate_on_submit():
        file = form.audio_file.data
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # Salvar referência do arquivo no banco de dados
        arquivo = Arquivo(
            laudo_id=laudo.id,
            filename=filename,
            filepath=filepath,
            filetype='audio',
            processed=False
        )
        db.session.add(arquivo)
        db.session.commit()
        
        # Iniciar a transcrição em background ou diretamente
        try:
            transcricao = transcribe_audio_file(filepath)
            arquivo.transcricao = transcricao
            arquivo.processed = True
            db.session.commit()
            
            flash('Áudio transcrito com sucesso!', 'success')
            return redirect(url_for('laudo_view', laudo_id=laudo.id))
        except Exception as e:
            flash(f'Erro ao transcrever o áudio: {str(e)}', 'danger')
    
    return render_template('upload_audio.html', title='Upload de Áudio', form=form, laudo=laudo)

@app.route('/laudos/<int:laudo_id>/secoes/<string:secao_tipo>', methods=['GET', 'POST'])
@login_required
def edit_secao(laudo_id, secao_tipo):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    secao = LaudoSecao.query.filter_by(laudo_id=laudo.id, secao_tipo=secao_tipo).first_or_404()
    
    form = SecaoForm()
    if form.validate_on_submit():
        secao.conteudo = form.conteudo.data
        secao.completed = True
        secao.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Seção {secao.secao_tipo} atualizada com sucesso!', 'success')
        return redirect(url_for('laudo_view', laudo_id=laudo.id))
    elif request.method == 'GET':
        form.conteudo.data = secao.conteudo
    
    secao_titulo = {
        'preambulo': 'Preâmbulo',
        'palavras_chave': 'Palavras-Chave',
        'apresentacao_demanda': 'Apresentação da Demanda',
        'objeto_pericia': 'Objeto da Perícia',
        'metodologia': 'Metodologia',
        'descricao': 'Descrição',
        'discussao': 'Discussão',
        'conclusao': 'Conclusão'
    }
    
    return render_template('laudo_edit.html', title=f'Editar {secao_titulo.get(secao_tipo, secao_tipo)}', 
                           form=form, laudo=laudo, secao=secao, secao_titulo=secao_titulo.get(secao_tipo, secao_tipo))

@app.route('/laudos/<int:laudo_id>/secoes/<string:secao_tipo>/gerar', methods=['POST'])
@login_required
def gerar_conteudo_secao(laudo_id, secao_tipo):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    secao = LaudoSecao.query.filter_by(laudo_id=laudo.id, secao_tipo=secao_tipo).first_or_404()
    
    try:
        # Obter transcrições de áudio se existirem
        audios = Arquivo.query.filter_by(laudo_id=laudo.id, filetype='audio', processed=True).all()
        transcricoes = [audio.transcricao for audio in audios if audio.transcricao]
        
        # Obter outras seções já completadas
        outras_secoes = LaudoSecao.query.filter_by(laudo_id=laudo.id, completed=True).all()
        contexto_secoes = {s.secao_tipo: s.conteudo for s in outras_secoes}
        
        # Gerar conteúdo com o OpenAI
        conteudo_gerado = generate_section_content(secao_tipo, transcricoes, contexto_secoes)
        
        # Atualizar a seção
        secao.conteudo = conteudo_gerado
        secao.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'content': conteudo_gerado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/laudos/<int:laudo_id>/gerar-relatorio', methods=['GET'])
@login_required
def gerar_relatorio(laudo_id):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    secoes = LaudoSecao.query.filter_by(laudo_id=laudo.id).all()
    
    return render_template('generate_report.html', title='Gerar Relatório', laudo=laudo, secoes=secoes)

@app.route('/laudos/<int:laudo_id>/gerar-docx', methods=['POST'])
@login_required
def gerar_docx(laudo_id):
    laudo = Laudo.query.filter_by(id=laudo_id, user_id=current_user.id).first_or_404()
    secoes = LaudoSecao.query.filter_by(laudo_id=laudo.id).all()
    
    # Verificar se todas as seções estão completas
    secoes_incompletas = [s.secao_tipo for s in secoes if not s.completed]
    if secoes_incompletas:
        secoes_nomes = {
            'preambulo': 'Preâmbulo',
            'palavras_chave': 'Palavras-Chave',
            'apresentacao_demanda': 'Apresentação da Demanda',
            'objeto_pericia': 'Objeto da Perícia',
            'metodologia': 'Metodologia',
            'descricao': 'Descrição',
            'discussao': 'Discussão',
            'conclusao': 'Conclusão'
        }
        missing = [secoes_nomes.get(s, s) for s in secoes_incompletas]
        flash(f'As seguintes seções estão incompletas: {", ".join(missing)}', 'warning')
        return redirect(url_for('laudo_view', laudo_id=laudo.id))
    
    try:
        # Preparar os dados para o relatório
        dados_secoes = {s.secao_tipo: s.conteudo for s in secoes}
        
        # Gerar o documento DOCX
        docx_buffer = generate_docx_report(laudo.title, dados_secoes, current_user.username)
        
        # Atualizar o status do laudo para completo
        laudo.status = 'completo'
        laudo.current_stage = 'finalizado'
        db.session.commit()
        
        # Enviar o arquivo gerado para download
        buffer = BytesIO(docx_buffer.getvalue())
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Laudo_Pericial_{laudo.id}_{datetime.now().strftime('%Y%m%d')}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        flash(f'Erro ao gerar o documento: {str(e)}', 'danger')
        return redirect(url_for('laudo_view', laudo_id=laudo.id))

@app.route('/arquivos/<int:arquivo_id>/download')
@login_required
def download_arquivo(arquivo_id):
    arquivo = Arquivo.query.filter_by(id=arquivo_id).first_or_404()
    laudo = Laudo.query.filter_by(id=arquivo.laudo_id).first_or_404()
    
    # Verificar permissão
    if laudo.user_id != current_user.id:
        flash('Você não tem permissão para baixar este arquivo', 'danger')
        return redirect(url_for('dashboard'))
    
    return send_file(
        arquivo.filepath,
        as_attachment=True,
        download_name=arquivo.filename
    )

@app.route('/arquivos/<int:arquivo_id>/transcricao')
@login_required
def view_transcricao(arquivo_id):
    arquivo = Arquivo.query.filter_by(id=arquivo_id).first_or_404()
    laudo = Laudo.query.filter_by(id=arquivo.laudo_id).first_or_404()
    
    # Verificar permissão
    if laudo.user_id != current_user.id:
        flash('Você não tem permissão para visualizar esta transcrição', 'danger')
        return redirect(url_for('dashboard'))
    
    if not arquivo.transcricao:
        flash('Este arquivo não possui transcrição', 'warning')
        return redirect(url_for('laudo_view', laudo_id=laudo.id))
    
    return render_template('transcricao.html', title='Transcrição', arquivo=arquivo, laudo=laudo)
