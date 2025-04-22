import os
import json
import logging
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio_file(audio_file_path):
    """Transcribe an audio file using OpenAI Whisper API"""
    if not os.path.exists(audio_file_path):
        logging.error(f"Audio file not found: {audio_file_path}")
        return "Arquivo de áudio não encontrado."
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="pt"  # Portuguese language
            )
        
        return response.text
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        return f"Erro na transcrição: {str(e)}"

def analyze_transcription(transcription):
    """
    Analyze the transcription of audio to extract relevant information
    for different sections of the forensic report.
    """
    if not transcription or len(transcription.strip()) < 10:
        return None
    
    try:
        system_message = (
            "Você é um assistente especializado em análise de transcrições de áudio "
            "para laudos periciais. Sua tarefa é extrair informações relevantes "
            "da transcrição para diferentes seções do laudo."
        )
        
        prompt = (
            "Analise a seguinte transcrição de áudio relacionada a uma perícia "
            "e extraia informações relevantes para as seguintes seções do laudo pericial:\n"
            "1. Descrição (fatos, observações e elementos analisados)\n"
            "2. Discussão (análise técnica dos achados)\n"
            "3. Conclusão (síntese das principais conclusões)\n\n"
            f"Transcrição do áudio:\n{transcription}\n\n"
            "Forneça sua resposta no formato JSON com as chaves 'descricao', 'discussao' e 'conclusao', "
            "com o conteúdo sugerido para cada seção. Se não houver informações suficientes "
            "para alguma seção, indique isso."
        )
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        
        # Map the keys to our section types
        return {
            'descricao': result.get('descricao', ''),
            'discussao': result.get('discussao', ''),
            'conclusao': result.get('conclusao', '')
        }
    except Exception as e:
        logging.error(f"Error analyzing transcription: {str(e)}")
        return None
