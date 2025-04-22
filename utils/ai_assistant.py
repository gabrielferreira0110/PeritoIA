import os
import json
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_content(prompt, model="gpt-4o", system_message=None):
    """Generate content using OpenAI API"""
    try:
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating AI content: {str(e)}")
        return f"Erro ao gerar conteúdo: {str(e)}"

def generate_preamble(title, extracted_data, existing_sections):
    """Generate preamble section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em elaborar preâmbulos para laudos periciais. "
        "Forneça um preâmbulo formal, profissional e completo para um laudo pericial, "
        "com base nas informações do processo."
    )
    
    prompt = (
        f"Elabore um preâmbulo para um laudo pericial com o título '{title}'. "
        "O preâmbulo deve incluir a identificação formal do perito, do juízo, "
        "do processo e das partes envolvidas. "
        f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}"
    )
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_keywords(extracted_data, existing_sections, transcription=None):
    """Generate keywords section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em identificar as palavras-chave "
        "mais relevantes para um laudo pericial."
    )
    
    prompt = (
        "Liste entre 5 e 10 palavras-chave relevantes para este laudo pericial, "
        "separadas por vírgula. Considere o contexto do processo, as partes envolvidas "
        "e o objeto da perícia.\n\n"
    )
    
    if existing_sections.get('preambulo'):
        prompt += f"Preâmbulo do laudo: {existing_sections.get('preambulo')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}\n\n"
    
    if transcription:
        prompt += f"Transcrição de áudio relevante: {transcription[:1000]}..."
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_demand_presentation(extracted_data, existing_sections):
    """Generate demand presentation section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em apresentar claramente a demanda "
        "que motivou a perícia."
    )
    
    prompt = (
        "Elabore uma apresentação clara e objetiva da demanda que motivou esta perícia. "
        "A apresentação deve incluir o contexto do processo, o que está sendo questionado "
        "e quais são os principais pontos que a perícia deve esclarecer.\n\n"
    )
    
    if existing_sections.get('preambulo'):
        prompt += f"Preâmbulo do laudo: {existing_sections.get('preambulo')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}"
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_forensic_object(extracted_data, existing_sections):
    """Generate forensic object section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em definir com precisão o objeto "
        "de uma perícia judicial."
    )
    
    prompt = (
        "Defina o objeto desta perícia de forma clara e precisa. O objeto deve indicar "
        "exatamente o que será analisado, avaliado ou investigado durante a perícia, "
        "estabelecendo o escopo do trabalho pericial.\n\n"
    )
    
    if existing_sections.get('preambulo'):
        prompt += f"Preâmbulo do laudo: {existing_sections.get('preambulo')}\n\n"
    
    if existing_sections.get('apresentacao_demanda'):
        prompt += f"Apresentação da demanda: {existing_sections.get('apresentacao_demanda')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}"
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_methodology(extracted_data, existing_sections):
    """Generate methodology section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em metodologias de investigação "
        "e análise pericial."
    )
    
    prompt = (
        "Descreva a metodologia utilizada nesta perícia. Inclua os procedimentos, "
        "técnicas, normas, referências e métodos científicos adotados para realizar "
        "a investigação pericial e chegar às conclusões.\n\n"
    )
    
    if existing_sections.get('objeto_pericia'):
        prompt += f"Objeto da perícia: {existing_sections.get('objeto_pericia')}\n\n"
    
    if existing_sections.get('apresentacao_demanda'):
        prompt += f"Apresentação da demanda: {existing_sections.get('apresentacao_demanda')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}"
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_description(extracted_data, existing_sections, transcription=None):
    """Generate description section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em descrever minuciosamente "
        "os elementos analisados em uma perícia."
    )
    
    prompt = (
        "Elabore uma descrição detalhada dos elementos analisados nesta perícia. "
        "A descrição deve ser objetiva, imparcial e completa, relatando fielmente "
        "o que foi observado, sem incluir opiniões ou conclusões.\n\n"
    )
    
    if existing_sections.get('objeto_pericia'):
        prompt += f"Objeto da perícia: {existing_sections.get('objeto_pericia')}\n\n"
    
    if existing_sections.get('metodologia'):
        prompt += f"Metodologia: {existing_sections.get('metodologia')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}\n\n"
    
    if transcription:
        prompt += f"Transcrição de áudio relevante: {transcription[:1500]}..."
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_discussion(extracted_data, existing_sections, transcription=None):
    """Generate discussion section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em analisar e discutir as evidências "
        "e achados de uma perícia judicial."
    )
    
    prompt = (
        "Elabore a seção de discussão deste laudo pericial. Na discussão, você deve "
        "analisar as evidências descritas, interpretar os achados à luz da metodologia "
        "adotada e da literatura especializada, e discutir as possíveis implicações "
        "para o caso em questão.\n\n"
    )
    
    if existing_sections.get('objeto_pericia'):
        prompt += f"Objeto da perícia: {existing_sections.get('objeto_pericia')}\n\n"
    
    if existing_sections.get('metodologia'):
        prompt += f"Metodologia: {existing_sections.get('metodologia')}\n\n"
    
    if existing_sections.get('descricao'):
        prompt += f"Descrição: {existing_sections.get('descricao')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}\n\n"
    
    if transcription:
        prompt += f"Transcrição de áudio relevante: {transcription[:1500]}..."
    
    return generate_ai_content(prompt, system_message=system_message)

def generate_conclusion(extracted_data, existing_sections, transcription=None):
    """Generate conclusion section for forensic report"""
    system_message = (
        "Você é um perito judicial especializado em formular conclusões objetivas "
        "e fundamentadas para laudos periciais."
    )
    
    prompt = (
        "Elabore a conclusão deste laudo pericial. A conclusão deve responder "
        "objetivamente às questões formuladas no objeto da perícia, sintetizar "
        "os principais achados e apresentar as respostas fundamentadas nas evidências "
        "e na discussão realizada. Evite incluir novos elementos ou análises não "
        "mencionados anteriormente.\n\n"
    )
    
    if existing_sections.get('objeto_pericia'):
        prompt += f"Objeto da perícia: {existing_sections.get('objeto_pericia')}\n\n"
    
    if existing_sections.get('descricao'):
        prompt += f"Descrição: {existing_sections.get('descricao')}\n\n"
    
    if existing_sections.get('discussao'):
        prompt += f"Discussão: {existing_sections.get('discussao')}\n\n"
    
    prompt += f"Informações do processo: {json.dumps(extracted_data, ensure_ascii=False)}\n\n"
    
    if transcription:
        prompt += f"Transcrição de áudio relevante: {transcription[:1000]}..."
    
    return generate_ai_content(prompt, system_message=system_message)

def analyze_forensic_document(document_path):
    """Analyze forensic document and suggest sections for report"""
    # This is a placeholder for document analysis using AI
    # In a real implementation, this would extract text from the document
    # and use AI to analyze it
    
    system_message = (
        "Você é um sistema de análise de documentos periciais especializado em extrair "
        "informações relevantes para a elaboração de laudos."
    )
    
    prompt = (
        f"Com base no documento pericial localizado em {document_path}, "
        "analise o conteúdo e sugira seções para um laudo pericial. "
        "Indique o que deve ser incluído em cada uma das seguintes seções: "
        "preâmbulo, palavras-chave, apresentação da demanda, objeto da perícia, "
        "metodologia, descrição, discussão e conclusão."
    )
    
    # This is a placeholder - in a real implementation, we would extract
    # the text from the document and include it in the prompt
    
    response = generate_ai_content(prompt, system_message=system_message)
    
    # Parse the response into sections - this is simplified
    # In a real implementation, we would parse the AI response more carefully
    sections = {}
    current_section = None
    content = []
    
    for line in response.split('\n'):
        line = line.strip()
        
        if line.lower().startswith('preâmbulo:') or line.lower() == 'preâmbulo':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'preambulo'
            content = []
            continue
        elif line.lower().startswith('palavras-chave:') or line.lower() == 'palavras-chave':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'palavras_chave'
            content = []
            continue
        elif line.lower().startswith('apresentação da demanda:') or line.lower() == 'apresentação da demanda':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'apresentacao_demanda'
            content = []
            continue
        elif line.lower().startswith('objeto da perícia:') or line.lower() == 'objeto da perícia':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'objeto_pericia'
            content = []
            continue
        elif line.lower().startswith('metodologia:') or line.lower() == 'metodologia':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'metodologia'
            content = []
            continue
        elif line.lower().startswith('descrição:') or line.lower() == 'descrição':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'descricao'
            content = []
            continue
        elif line.lower().startswith('discussão:') or line.lower() == 'discussão':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'discussao'
            content = []
            continue
        elif line.lower().startswith('conclusão:') or line.lower() == 'conclusão':
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = 'conclusao'
            content = []
            continue
        
        if current_section and line:
            content.append(line)
    
    # Add the last section
    if current_section and content:
        sections[current_section] = '\n'.join(content)
    
    return sections
