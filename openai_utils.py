import os
import json
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio_file(audio_file_path):
    """
    Transcreve um arquivo de áudio usando o modelo Whisper da OpenAI
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="pt"
            )
        return response.text
    except Exception as e:
        raise Exception(f"Erro na transcrição: {str(e)}")

def generate_section_content(section_type, transcriptions=None, other_sections=None):
    """
    Gera o conteúdo para uma seção específica do laudo pericial usando o GPT-4o
    """
    if transcriptions is None:
        transcriptions = []
    if other_sections is None:
        other_sections = {}
        
    # Definir o prompt base de acordo com o tipo de seção
    prompts = {
        'preambulo': "Elabore um preâmbulo formal para um laudo pericial médico. O preâmbulo deve incluir a introdução formal do documento.",
        'palavras_chave': "Gere uma lista de palavras-chave relevantes para este laudo pericial, baseado nas informações disponíveis.",
        'apresentacao_demanda': "Elabore uma apresentação da demanda para este laudo pericial, explicando o contexto e o motivo da perícia.",
        'objeto_pericia': "Defina o objeto da perícia de forma clara e objetiva, especificando o que está sendo analisado.",
        'metodologia': "Descreva a metodologia utilizada para a realização da perícia, incluindo procedimentos, técnicas e ferramentas.",
        'descricao': "Elabore uma descrição detalhada dos fatos e elementos observados durante a perícia.",
        'discussao': "Desenvolva uma discussão técnica sobre os achados da perícia, analisando os fatos à luz do conhecimento técnico-científico.",
        'conclusao': "Formule uma conclusão objetiva e fundamentada para o laudo pericial, respondendo à questão principal da perícia."
    }
    
    # Selecionar o prompt base para o tipo de seção
    prompt_base = prompts.get(section_type, "Gere conteúdo para o laudo pericial.")
    
    # Construir o contexto com transcrições e outras seções
    contexto = ""
    
    if transcriptions:
        contexto += "Transcrições de áudio relacionadas:\n\n"
        for i, transcription in enumerate(transcriptions, 1):
            contexto += f"Transcrição {i}:\n{transcription}\n\n"
    
    if other_sections:
        contexto += "Outras seções do laudo:\n\n"
        for section_name, content in other_sections.items():
            if section_name != section_type and content:  # Não incluir a própria seção ou seções vazias
                contexto += f"Seção {section_name}:\n{content[:500]}...\n\n"  # Limitar tamanho para não exceder tokens
    
    # Montar o prompt completo
    prompt_completo = f"""
    {prompt_base}
    
    {contexto}
    
    Importante:
    - O conteúdo deve ser escrito em português formal e técnico
    - Utilize terminologia apropriada para laudos periciais
    - Seja objetivo e claro em sua elaboração
    - Evite afirmações sem embasamento
    - O conteúdo deve ser original e específico para esta seção
    
    Por favor, gere o conteúdo completo para a seção '{section_type}' de um laudo pericial.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado na elaboração de laudos periciais médicos. Seu objetivo é produzir conteúdo técnico, preciso e profissional para cada seção do laudo."},
                {"role": "user", "content": prompt_completo}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Erro ao gerar conteúdo com OpenAI: {str(e)}")

def analyze_document_content(text):
    """
    Analisa o conteúdo de um documento para extrair informações relevantes
    """
    prompt = """
    Analise o seguinte texto extraído de um documento relacionado a um processo pericial:
    
    ```
    {text}
    ```
    
    Extraia e organize as seguintes informações no formato JSON:
    
    1. Tipo de documento
    2. Partes envolvidas (nomes)
    3. Objeto da perícia
    4. Informações relevantes para o laudo
    5. Prazos mencionados
    6. Quesitos a serem respondidos (se houver)
    
    Responda apenas com o JSON, sem texto adicional.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em análise de documentos jurídicos e médicos. Sua função é extrair informações estruturadas de documentos relacionados a processos periciais."},
                {"role": "user", "content": prompt.format(text=text[:4000])}  # Limitando o tamanho para não exceder limite de tokens
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Erro ao analisar documento com OpenAI: {str(e)}")
