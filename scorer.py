from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .analyzer import extract_keywords, preprocess_text

def calculate_similarity(resume_text, jd_text):
    """
    Computes cosine similarity between resume text and job description using TF-IDF.
    Returns a score from 0 to 100.
    """
    try:
        # TfidfVectorizer expects a list of strings
        corpus = [resume_text, jd_text]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculate cosine similarity between the two documents
        # tfidf_matrix[0] is resume, tfidf_matrix[1] is JD
        # sim_matrix[0][0] holds the score between the two
        sim_matrix = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
        # Convert to percentage
        return float(sim_matrix[0][0]) * 100
    except Exception as e:
        return 0.0

def calculate_ats_score(keyword_match_pct, sim_score, completeness_pct):
    """
    Calculates the final ATS Score.
    Weighted formula:
    - 50% from keyword match percentage
    - 30% from basic TF-IDF cosine similarity
    - 20% from section completeness
    Returns a number from 0.0 to 100.0.
    """
    final_score = (keyword_match_pct * 0.50) + (sim_score * 0.30) + (completeness_pct * 0.20)
    return round(final_score, 2)
