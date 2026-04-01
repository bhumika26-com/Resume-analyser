import streamlit as st
import plotly.graph_objects as go
import re

from utils.parser import extract_text_from_pdf, extract_text_from_docx
from utils.analyzer import extract_keywords, find_sections
from utils.scorer import calculate_similarity, calculate_ats_score
from utils.llm_helper import get_resume_feedback

# -------------- PAGE CONFIG --------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# -------------- CSS STYLES --------------
# Adding some basic modern styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .big-score {
        font-size: 80px;
        font-weight: 800;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0px;
    }
    .score-label {
        font-size: 20px;
        font-weight: 500;
        text-align: center;
        color: gray;
        margin-top: -10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -------------- HELPER FUNCTION --------------
def make_gauge_chart(score):
    """Creates a beautiful Plotly Gauge chart for the ATS Score."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "ATS Match Score", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#1f77b4"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ff4b4b'},
                {'range': [40, 70], 'color': '#ffa500'},
                {'range': [70, 100], 'color': '#00cc96'}],
        }
    ))
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=50, b=10))
    return fig

# -------------- SIDEBAR --------------
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key (Optional)", type="password", help="Needed for AI Suggestions")
    st.markdown("---")
    st.markdown("""
    **📋 How it works:**
    1. Upload your Resume (PDF/DOCX).
    2. Paste the Target Job Description.
    3. Click Analyze.
    
    The system uses NLP (spaCy + TF-IDF) to calculate an ATS score and identifies passing/missing keywords.
    """)

# -------------- MAIN APP --------------
st.title("📄 AI Resume Analyzer (ATS Simulator)")
st.markdown("Optimize your resume against your target job description to bypass the Applicant Tracking System.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume in PDF or DOCX format", type=["pdf", "docx"])

with col2:
    st.subheader("2. Target Job Description")
    jd_text = st.text_area("Paste the job description here", height=200, placeholder="e.g. We are looking for a Senior Python Engineer with 5+ years of experience in Django, AWS, and PostgreSQL...")

analyze_button = st.button("🚀 Analyze Resume", use_container_width=True, type="primary")

# -------------- PROCESSING LOGIC --------------
if analyze_button:
    if not uploaded_file:
        st.error("Please upload a resume to proceed.")
    elif not jd_text.strip():
        st.error("Please provide a Job Description to compare against.")
    else:
        with st.spinner("Analyzing document structure..."):
            # 1. Text Extraction
            file_bytes = uploaded_file.read()
            if uploaded_file.name.endswith('.pdf'):
                resume_text = extract_text_from_pdf(file_bytes)
            else:
                resume_text = extract_text_from_docx(file_bytes)
                
            if resume_text.startswith("Error"):
                st.error(f"Failed to read file: {resume_text}")
                st.stop()
                
        with st.spinner("Running NLP Processing & Keyword Extraction..."):
            # 2. Section Detection
            sections = find_sections(resume_text)
            completeness_score = (sum(sections.values()) / len(sections)) * 100
            
            # 3. Keyword Extraction
            resume_keywords = extract_keywords(resume_text)
            jd_keywords = extract_keywords(jd_text)
            
            # 4. Keyword Match Calculation
            if len(jd_keywords) == 0:
                keyword_match_pct = 0
            else:
                matched_keywords = jd_keywords.intersection(resume_keywords)
                keyword_match_pct = (len(matched_keywords) / len(jd_keywords)) * 100
            missing_keywords = jd_keywords - resume_keywords
            
            # 5. Semantic Similarity
            sim_score = calculate_similarity(resume_text, jd_text)
            
            # 6. Final ATS Score
            final_ats_score = calculate_ats_score(keyword_match_pct, sim_score, completeness_score)
            
        with st.spinner("Generating AI Feedback using Gemini..."):
            # 7. LLM Feedback
            ai_feedback = get_resume_feedback(resume_text, jd_text, custom_api_key=api_key)

        # -------------- RESULT DASHBOARD --------------
        st.success("Analysis Complete!")
        st.markdown("---")
        
        # Display ATS Score
        score_col, chart_col = st.columns([1, 2])
        
        with score_col:
            st.markdown(f'<div class="big-score">{int(final_ats_score)}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="score-label">Overall Match Score</div>', unsafe_allow_html=True)
            
            st.write("**Breakdown:**")
            st.progress(int(keyword_match_pct))
            st.caption(f"Keyword Match ({int(keyword_match_pct)}%)")
            
            st.progress(int(sim_score))
            st.caption(f"Semantic Similarity ({int(sim_score)}%)")
            
            st.progress(int(completeness_score))
            st.caption(f"Section Completeness ({int(completeness_score)}%)")
            
        with chart_col:
            st.plotly_chart(make_gauge_chart(final_ats_score), use_container_width=True)

        st.markdown("---")
        
        # Display Tabs for detailed breakdowns
        tab1, tab2, tab3 = st.tabs(["🔑 Keyword Analysis", "🤖 AI Suggestions", "📂 Structure Check"])
        
        with tab1:
            st.header("Keyword Analysis")
            k_col1, k_col2 = st.columns(2)
            
            with k_col1:
                st.subheader(f"✅ Matched Keywords ({len(matched_keywords)})")
                if matched_keywords:
                    # Creating a styled wrap for keywords (like tags)
                    tags = " ".join([f"<span style='background-color:#d4edda; color:#155724; padding:5px; border-radius:5px; margin:2px; display:inline-block;'>{kw}</span>" for kw in list(matched_keywords)[:30]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.write("No matching keywords found.")
                    
            with k_col2:
                st.subheader(f"❌ Missing Keywords ({len(missing_keywords)})")
                if missing_keywords:
                    tags = " ".join([f"<span style='background-color:#f8d7da; color:#721c24; padding:5px; border-radius:5px; margin:2px; display:inline-block;'>{kw}</span>" for kw in list(missing_keywords)[:30]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.write("Awesome! You matched all major keywords.")
                    
        with tab2:
            st.header("AI Driven Feedback")
            if "None - API Key not provided" in ai_feedback.get("strengths", [""])[0] or "Error" in ai_feedback.get("weaknesses", [""])[0]:
                st.warning("⚠️ For detailed AI feedback, please provide a Gemini API Key in the sidebar or `.env` file.")
            
            st.subheader("💪 Strengths")
            for item in ai_feedback.get("strengths", []):
                st.markdown(f"- {item}")
                
            st.subheader("🚧 Weaknesses")
            for item in ai_feedback.get("weaknesses", []):
                st.markdown(f"- {item}")
                
            st.subheader("💡 Suggestions for Improvement")
            for item in ai_feedback.get("suggestions", []):
                st.markdown(f"- {item}")
                
        with tab3:
            st.header("Resume Structure Check")
            st.write("A good resume format helps Applicant Tracking Systems parse your details accurately.")
            
            for section, found in sections.items():
                if found:
                    st.success(f"**{section}** section detected.")
                else:
                    st.error(f"**{section}** section is MISSING. Consider adding clear headers.")
