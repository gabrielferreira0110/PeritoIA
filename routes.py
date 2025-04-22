import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, session, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from models import User, Report, ReportSection, AudioTranscription, DocumentExtraction
from utils.ai_assistant import (generate_preamble, generate_keywords, 
                               generate_demand_presentation, generate_forensic_object,
                               generate_description, generate_discussion,
                               generate_conclusion, generate_methodology,
                               analyze_forensic_document)
from utils.audio_processor import transcribe_audio_file, analyze_transcription
from utils.document_processor import extract_document_info
from utils.docx_generator import generate_report_docx

ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_document_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('register'))
            
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Nome de usuário ou e-mail já existente', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Agora você pode fazer login', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Nome de usuário ou senha inválidos', 'danger')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')
            
        flash('Login realizado com sucesso!', 'success')
        return redirect(next_page)
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get stats for the dashboard
    total_reports = Report.query.filter_by(user_id=current_user.id).count()
    completed_reports = Report.query.filter_by(user_id=current_user.id, status='completo').count()
    in_progress_reports = Report.query.filter_by(user_id=current_user.id, status='em_andamento').count()
    
    # Get the latest 5 reports
    latest_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.updated_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_reports=total_reports,
                           completed_reports=completed_reports,
                           in_progress_reports=in_progress_reports,
                           latest_reports=latest_reports)

@app.route('/reports')
@login_required
def reports():
    # Get all reports for the current user
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.updated_at.desc()).all()
    return render_template('reports.html', reports=user_reports)

@app.route('/report/create', methods=['GET', 'POST'])
@login_required
def create_report():
    if request.method == 'POST':
        title = request.form.get('title')
        
        if not title:
            flash('O título do laudo é obrigatório', 'danger')
            return redirect(url_for('create_report'))
            
        new_report = Report(
            title=title,
            user_id=current_user.id,
            status='em_andamento',
            current_step='documento'
        )
        
        db.session.add(new_report)
        db.session.commit()
        
        flash('Laudo criado com sucesso!', 'success')
        return redirect(url_for('edit_report', report_id=new_report.id))
        
    return render_template('create_report.html')

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para visualizar este laudo', 'danger')
        return redirect(url_for('reports'))
        
    sections = ReportSection.query.filter_by(report_id=report_id).all()
    
    return render_template('report_preview.html', report=report, sections=sections)

@app.route('/report/<int:report_id>/edit')
@login_required
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para editar este laudo', 'danger')
        return redirect(url_for('reports'))
        
    # Get sections if they exist
    sections = {section.section_type: section for section in report.sections.all()}
    
    return render_template('edit_report.html', report=report, sections=sections)

@app.route('/report/<int:report_id>/sections')
@login_required
def report_sections(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para editar este laudo', 'danger')
        return redirect(url_for('reports'))
        
    # Get sections if they exist
    sections = {section.section_type: section for section in report.sections.all()}
    
    return render_template('report_sections.html', report=report, sections=sections)

@app.route('/report/<int:report_id>/upload-document', methods=['GET', 'POST'])
@login_required
def upload_document(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para editar este laudo', 'danger')
        return redirect(url_for('reports'))
        
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'document' not in request.files:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(request.url)
            
        file = request.files['document']
        
        # If the user doesn't select a file, the browser submits an empty file
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
            
        if file and allowed_document_file(file.filename):
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            secure_name = f"{report.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', secure_name)
            
            file.save(file_path)
            
            # Update the report with the document path
            report.document_path = file_path
            report.current_step = 'preambulo'
            db.session.commit()
            
            # Process the document to extract information
            try:
                extracted_info = extract_document_info(file_path)
                
                # Save the extracted information
                doc_extraction = DocumentExtraction(
                    report_id=report.id,
                    document_path=file_path,
                    extracted_data=json.dumps(extracted_info)
                )
                db.session.add(doc_extraction)
                db.session.commit()
                
                flash('Documento enviado e processado com sucesso!', 'success')
            except Exception as e:
                flash(f'Documento enviado, mas houve um erro ao processá-lo: {str(e)}', 'warning')
                
            return redirect(url_for('report_sections', report_id=report.id))
        else:
            flash('Tipo de arquivo não permitido', 'danger')
            return redirect(request.url)
            
    return render_template('document_upload.html', report=report)

@app.route('/report/<int:report_id>/upload-audio', methods=['GET', 'POST'])
@login_required
def upload_audio(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para editar este laudo', 'danger')
        return redirect(url_for('reports'))
        
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'audio' not in request.files:
            flash('Nenhum arquivo de áudio enviado', 'danger')
            return redirect(request.url)
            
        file = request.files['audio']
        
        # If the user doesn't select a file, the browser submits an empty file
        if file.filename == '':
            flash('Nenhum arquivo de áudio selecionado', 'danger')
            return redirect(request.url)
            
        if file and allowed_audio_file(file.filename):
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            secure_name = f"{report.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', secure_name)
            
            file.save(file_path)
            
            # Update the report with the audio path
            report.audio_path = file_path
            db.session.commit()
            
            # Process the audio to transcribe it
            try:
                transcription = transcribe_audio_file(file_path)
                
                # Save the transcription
                audio_trans = AudioTranscription(
                    report_id=report.id,
                    audio_path=file_path,
                    transcription=transcription
                )
                db.session.add(audio_trans)
                db.session.commit()
                
                flash('Áudio enviado e transcrito com sucesso!', 'success')
                
                # If we have a transcription, try to analyze it
                if transcription:
                    analysis = analyze_transcription(transcription)
                    # Update relevant sections with analysis data
                    if analysis:
                        for section_type, content in analysis.items():
                            section = ReportSection.query.filter_by(
                                report_id=report.id, 
                                section_type=section_type
                            ).first()
                            
                            if section:
                                section.content = content
                                db.session.commit()
                                flash(f'Seção {section_type} atualizada com base na análise do áudio', 'info')
                            
            except Exception as e:
                flash(f'Áudio enviado, mas houve um erro ao transcrevê-lo: {str(e)}', 'warning')
                
            return redirect(url_for('report_sections', report_id=report.id))
        else:
            flash('Tipo de arquivo de áudio não permitido', 'danger')
            return redirect(request.url)
            
    return render_template('audio_upload.html', report=report)

@app.route('/report/<int:report_id>/generate-section/<section_type>', methods=['POST'])
@login_required
def generate_section(report_id, section_type):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Você não tem permissão para editar este laudo'})
    
    # Check if any document extraction exists
    doc_extraction = DocumentExtraction.query.filter_by(report_id=report.id).first()
    extracted_data = json.loads(doc_extraction.extracted_data) if doc_extraction else {}
    
    # Check if any audio transcription exists
    audio_trans = AudioTranscription.query.filter_by(report_id=report.id).first()
    transcription = audio_trans.transcription if audio_trans else ""
    
    # Get existing sections
    sections = {section.section_type: section.content for section in report.sections.all()}
    
    # Generate content based on section type
    if section_type == 'preambulo':
        content = generate_preamble(report.title, extracted_data, sections)
    elif section_type == 'palavras_chave':
        content = generate_keywords(extracted_data, sections, transcription)
    elif section_type == 'apresentacao_demanda':
        content = generate_demand_presentation(extracted_data, sections)
    elif section_type == 'objeto_pericia':
        content = generate_forensic_object(extracted_data, sections)
    elif section_type == 'metodologia':
        content = generate_methodology(extracted_data, sections)
    elif section_type == 'descricao':
        content = generate_description(extracted_data, sections, transcription)
    elif section_type == 'discussao':
        content = generate_discussion(extracted_data, sections, transcription)
    elif section_type == 'conclusao':
        content = generate_conclusion(extracted_data, sections, transcription)
    else:
        return jsonify({'success': False, 'message': 'Tipo de seção inválido'})
    
    # Save or update the section
    section = ReportSection.query.filter_by(report_id=report.id, section_type=section_type).first()
    
    if section:
        section.content = content
    else:
        section = ReportSection(
            report_id=report.id,
            section_type=section_type,
            content=content
        )
        db.session.add(section)
    
    # Update report status
    if section_type == 'conclusao':
        # Check if all required sections exist
        required_sections = ['preambulo', 'palavras_chave', 'apresentacao_demanda', 
                             'objeto_pericia', 'metodologia', 'descricao', 
                             'discussao', 'conclusao']
        existing_section_types = [s.section_type for s in report.sections.all()]
        
        if all(rs in existing_section_types for rs in required_sections):
            report.status = 'completo'
    
    # Update the current step to the next section
    section_order = ['preambulo', 'palavras_chave', 'apresentacao_demanda', 
                      'objeto_pericia', 'metodologia', 'descricao', 
                      'discussao', 'conclusao']
    
    current_index = section_order.index(section_type)
    if current_index < len(section_order) - 1:
        report.current_step = section_order[current_index + 1]
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Seção gerada com sucesso',
        'content': content
    })

@app.route('/report/<int:report_id>/update-section/<section_type>', methods=['POST'])
@login_required
def update_section(report_id, section_type):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Você não tem permissão para editar este laudo'})
    
    content = request.form.get('content')
    
    if not content:
        return jsonify({'success': False, 'message': 'Conteúdo não pode estar vazio'})
    
    # Save or update the section
    section = ReportSection.query.filter_by(report_id=report.id, section_type=section_type).first()
    
    if section:
        section.content = content
    else:
        section = ReportSection(
            report_id=report.id,
            section_type=section_type,
            content=content
        )
        db.session.add(section)
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Seção atualizada com sucesso'
    })

@app.route('/report/<int:report_id>/analyze-document', methods=['POST'])
@login_required
def analyze_document(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Você não tem permissão para analisar este laudo'})
    
    # Check if document exists
    if not report.document_path or not os.path.exists(report.document_path):
        return jsonify({'success': False, 'message': 'Documento não encontrado'})
    
    try:
        # Analyze the document
        analysis_results = analyze_forensic_document(report.document_path)
        
        # Update sections based on analysis results
        for section_type, content in analysis_results.items():
            section = ReportSection.query.filter_by(report_id=report.id, section_type=section_type).first()
            
            if section:
                section.content = content
            else:
                section = ReportSection(
                    report_id=report.id,
                    section_type=section_type,
                    content=content
                )
                db.session.add(section)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Documento analisado com sucesso',
            'results': analysis_results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao analisar documento: {str(e)}'})

@app.route('/report/<int:report_id>/generate-docx')
@login_required
def generate_docx(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para gerar este laudo', 'danger')
        return redirect(url_for('reports'))
    
    # Get all sections
    sections = ReportSection.query.filter_by(report_id=report.id).all()
    
    if not sections:
        flash('O laudo não tem seções para gerar o documento', 'warning')
        return redirect(url_for('report_sections', report_id=report.id))
    
    try:
        # Generate the DOCX file
        docx_path = generate_report_docx(report, sections)
        
        # Update the report with the path to the generated DOCX
        report.report_path = docx_path
        db.session.commit()
        
        # Return the file for download
        return send_file(docx_path, as_attachment=True, download_name=f"laudo_pericial_{report.id}.docx")
    
    except Exception as e:
        flash(f'Erro ao gerar o documento DOCX: {str(e)}', 'danger')
        return redirect(url_for('report_sections', report_id=report.id))

@app.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id:
        flash('Você não tem permissão para excluir este laudo', 'danger')
        return redirect(url_for('reports'))
    
    # Delete related files
    if report.document_path and os.path.exists(report.document_path):
        os.remove(report.document_path)
    
    if report.audio_path and os.path.exists(report.audio_path):
        os.remove(report.audio_path)
    
    if report.report_path and os.path.exists(report.report_path):
        os.remove(report.report_path)
    
    # Delete the report and all related sections
    db.session.delete(report)
    db.session.commit()
    
    flash('Laudo excluído com sucesso', 'success')
    return redirect(url_for('reports'))
