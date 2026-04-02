import fitz  # PyMuPDF
from groq import Groq
import os
from app.core.config import settings

# Initialize Groq Client
client = Groq(api_key=settings.GROQ_API_KEY)

def extract_text(file_path: str) -> str:
    """Extracts raw text from a PDF file."""
    with fitz.open(file_path) as doc:
        return "".join([page.get_text() for page in doc])

def calculate_match_score(resume_text: str, requirements: str) -> float:
    """
    Uses LLM to evaluate the candidate.
    It understands context, synonyms, and experience levels.
    """
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
            temperature=0, # Keep it consistent
        )
        # Extract the score from the response
        score_str = response.choices[0].message.content.strip()
        # Clean the string in case the LLM adds extra text
        score = float(''.join(filter(lambda x: x.isdigit() or x == '.', score_str)))
        return min(max(score, 0.0), 100.0) # Ensure it stays between 0-100
    except Exception as e:
        print(f"AI Error: {e}")
        return 0.0