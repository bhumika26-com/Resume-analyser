import spacy
import spacy.cli
import re

# Try to load the English language model.
# If it's not present, download it dynamically.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading English language model for spacy...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    """
    Cleans text by lowercasing, removing special characters, and extra spaces.
    """
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def extract_keywords(text):
    """
    Extracts relevant keywords (nouns, proper nouns, and non-stop words) using spaCy.
    Returns a set of keyword lemmas.
    """
    # Use the preprocessor to clean before spacy parsing
    clean_text = preprocess_text(text)
    doc = nlp(clean_text)
    
    keywords = set()
    for token in doc:
        # Look for nouns, proper nouns; exclude stop words and single-character tokens
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 1:
            keywords.add(token.lemma_.lower())
    return keywords

def find_sections(text):
    """
    Detects basic resume sections using keyword heuristics.
    Returns a dictionary with boolean flags indicating if a section was found.
    """
    sections = {
        "Experience": False,
        "Education": False,
        "Skills": False,
        "Projects": False
    }
    
    text_lower = text.lower()
    
    # Simple regex matching for common section headers
    if re.search(r'\b(experience|employment|work history)\b', text_lower):
        sections["Experience"] = True
    if re.search(r'\b(education|academic|qualifications|degree)\b', text_lower):
        sections["Education"] = True
    if re.search(r'\b(skills|technologies|core competencies)\b', text_lower):
        sections["Skills"] = True
    if re.search(r'\b(projects|portfolio)\b', text_lower):
        sections["Projects"] = True
        
    return sections
