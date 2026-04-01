import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Try to load environment variables from .env
load_dotenv()

def get_resume_feedback(resume_text, jd_text, custom_api_key=None):
    """
    Sends the parsed resume and JD to Gemini and asks for structured feedback.
    Returns a dictionary with strengths, weaknesses, and suggestions.
    Supports injecting a custom_api_key from the UI.
    """
    api_key = custom_api_key or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return {
            "strengths": ["None - API Key not provided."],
            "weaknesses": ["Cannot perform AI analysis without Gemini API Key."],
            "suggestions": ["Please provide a valid GEMINI_API_KEY in the sidebar or via the .env file."]
        }
        
    try:
        genai.configure(api_key=api_key)
        
        prompt = f"""
You are an expert ATS (Applicant Tracking System) and Senior Technical Recruiter.
Your task is to analyze how well the candidate's resume matches the job description.

Job Description:
{jd_text[:3000]} # Trimmed for context safety

Candidate Resume:
{resume_text[:3000]} # Trimmed for context safety

Provide the output strictly as a JSON object with the following exact keys:
"strengths": An array of strings highlighting the positive matches and strong points (max 4).
"weaknesses": An array of strings highlighting missing skills or weak points (max 4).
"suggestions": An array of actionable steps the candidate can take to improve their resume (max 4).

Respond ONLY with valid JSON matching the structure. Do not include markdown wrappers (like ```json), just the raw JSON object.
"""
        # Using gemini-pro (falls back appropriately depending on available standard API keys)
        # Using gemini-1.5-pro or flash depending on key access. 'gemini-pro' historically defaults well.
        model = genai.GenerativeModel('gemini-pro') 
        response = model.generate_content(prompt)
        
        raw_text = response.text.strip()
        
        # Strip potential markdown formatting that LLMs sometimes stubbornly add
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1)
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1)
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        raw_text = raw_text.strip()
        
        result = json.loads(raw_text)
        return {
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "suggestions": result.get("suggestions", [])
        }
        
    except Exception as e:
        return {
            "strengths": [],
            "weaknesses": [f"Error occurred during LLM processing: {str(e)}"],
            "suggestions": ["The API key might be invalid or quota exhausted. Please check your credentials and try again."]
        }
