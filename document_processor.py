import os
import PyPDF2
import tempfile
from openai_utils import analyze_document_content

def extract_text_from_pdf(pdf_path):
    """
    Extrai o texto de um arquivo PDF
    """
    try:
        text = ""
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        return text
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

def extract_information_from_pdf(pdf_path):
    """
    Processa um arquivo PDF para extrair informações relevantes para o laudo
    """
    try:
        # Extrair texto do PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Se o texto estiver vazio, pode ser um PDF digitalizado
        if not text.strip():
            return {
                "warning": "O PDF parece ser digitalizado e não possui texto extraível",
                "text": "",
                "structured_data": {}
            }
        
        # Analisar o conteúdo com OpenAI para extrair informações estruturadas
        structured_data = analyze_document_content(text)
        
        return {
            "text": text,
            "structured_data": structured_data
        }
    except Exception as e:
        raise Exception(f"Erro ao processar o PDF: {str(e)}")
