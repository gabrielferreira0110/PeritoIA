import os
import json
import logging
from io import StringIO
import PyPDF2

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        text = f"Error extracting text: {str(e)}"
    
    return text

def extract_text_from_txt(file_path):
    """Extract text from a TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        except Exception as e:
            logging.error(f"Error extracting text from TXT: {str(e)}")
            text = f"Error extracting text: {str(e)}"
    except Exception as e:
        logging.error(f"Error extracting text from TXT: {str(e)}")
        text = f"Error extracting text: {str(e)}"
    
    return text

def extract_document_info(file_path):
    """Extract information from a document file"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_ext == '.txt':
        text = extract_text_from_txt(file_path)
    elif file_ext in ['.doc', '.docx']:
        # Note: This is a placeholder. In a real implementation, 
        # you would use a library like python-docx to extract text from Word documents
        text = "Documento Word detectado. Extração de texto não implementada nesta versão."
    else:
        text = "Formato de arquivo não suportado para extração de texto."
    
    # Basic info extraction (very simplified)
    # In a real implementation, you would use NLP or other techniques to extract
    # structured information from the document
    
    result = {
        'file_path': file_path,
        'file_type': file_ext,
        'text_content': text[:5000],  # Limit text content size
        'extracted_entities': extract_entities_from_text(text)
    }
    
    return result

def extract_entities_from_text(text):
    """
    Extract entities from text
    This is a very simplified version - in a real implementation, 
    you would use NLP libraries or AI to extract entities
    """
    entities = {
        'process_number': extract_process_number(text),
        'parties': extract_parties(text),
        'court': extract_court(text),
        'forensic_questions': extract_forensic_questions(text)
    }
    
    return entities

def extract_process_number(text):
    """
    Extract process number from text
    This is a very simplified implementation using patterns
    """
    import re
    # Look for patterns like 0000000-00.0000.0.00.0000
    pattern = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    match = re.search(pattern, text)
    
    if match:
        return match.group(0)
    
    # More general pattern
    pattern = r'processo\s*[nº°.:]*\s*(\d[\d\.\/-]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1)
    
    return "Número do processo não identificado"

def extract_parties(text):
    """
    Extract parties from text
    This is a very simplified implementation
    """
    import re
    parties = {
        'author': '',
        'defendant': ''
    }
    
    # Look for author patterns
    author_patterns = [
        r'autor[a]?[:\s]+([^.;]+)[.;]',
        r'requerente[:\s]+([^.;]+)[.;]',
        r'reclamante[:\s]+([^.;]+)[.;]'
    ]
    
    for pattern in author_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parties['author'] = match.group(1).strip()
            break
    
    # Look for defendant patterns
    defendant_patterns = [
        r'réu[:\s]+([^.;]+)[.;]',
        r'requerido[a]?[:\s]+([^.;]+)[.;]',
        r'reclamado[a]?[:\s]+([^.;]+)[.;]'
    ]
    
    for pattern in defendant_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parties['defendant'] = match.group(1).strip()
            break
    
    return parties

def extract_court(text):
    """
    Extract court information from text
    This is a very simplified implementation
    """
    import re
    court_patterns = [
        r'((\d+)[aª]?\s*vara\s*[^,;.]+)',
        r'(juiz[o]?\s*[^,;.]+)',
        r'(tribunal\s*[^,;.]+)'
    ]
    
    for pattern in court_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Informação do juízo não identificada"

def extract_forensic_questions(text):
    """
    Extract forensic questions from text
    This is a very simplified implementation
    """
    import re
    questions = []
    
    # Look for sections that might contain questions
    question_sections = [
        r'quesitos[:\s]+(.*?)(?:\n\n|\Z)',
        r'perguntas[:\s]+(.*?)(?:\n\n|\Z)',
        r'questões[:\s]+(.*?)(?:\n\n|\Z)'
    ]
    
    for pattern in question_sections:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            question_text = match.group(1).strip()
            
            # Try to split into individual questions
            potential_questions = re.split(r'\n\d+[.)\s]+|\n[a-z][.)\s]+', question_text)
            
            for q in potential_questions:
                q = q.strip()
                if q and len(q) > 10:  # Simple filter for valid questions
                    questions.append(q)
            
            if questions:
                break
    
    return questions if questions else ["Quesitos periciais não identificados"]
