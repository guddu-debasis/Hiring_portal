import fitz  # PyMuPDF
from groq import Groq
import os
from app.core.config import settings

# Initialize Groq Client
client = Groq(api_key=settings.GROQ_API_KEY)

def extract_text(file_content: bytes) -> str:
    """
    Extracts raw text from PDF bytes. 
    This avoids needing a local file path, making it Cloud-ready.
    """
    try:
        # Open the PDF from memory (stream) instead of a file on disk
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            return "".join([page.get_text() for page in doc])
    except Exception as e:
        print(f"Extraction Error: {e}")
        return ""

def calculate_match_score(resume_text: str, requirements: str) -> float:
    """
    Uses LLM (Llama 3.3 via Groq) to evaluate the candidate.
    """
    if not resume_text.strip():
        return 0.0

    prompt = f"""
    You are an expert HR Technical Recruiter. 
    Compare the following Resume against the Job Requirements.
    
    Job Requirements: {requirements}
    Candidate Resume: {resume_text}
    
    Provide a Match Score from 0 to 100 based on:
    1. Skill alignment (Technical stack)
    2. Experience level (Years and depth)
    3. Project relevance
    
    Return ONLY a number (the score). Do not include any text or explanations.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
            temperature=0, # Keep it consistent for scores
        )
        # Extract the score from the response
        score_str = response.choices[0].message.content.strip()
        
        # Clean the string to ensure we only get a float
        clean_score = ''.join(filter(lambda x: x.isdigit() or x == '.', score_str))
        score = float(clean_score) if clean_score else 0.0
        
        return min(max(score, 0.0), 100.0) # Boundary check 0-100
    except Exception as e:
        print(f"AI Error: {e}")
        return 0.0