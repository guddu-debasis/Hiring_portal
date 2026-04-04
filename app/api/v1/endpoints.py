from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import shutil

from app.core.database import get_db
from app.models.candidate import JobPost, Candidate, User
from app.schemas.candidate import JobCreate, JobResponse, CandidateResponse
from app.services.ai_service import extract_text, calculate_match_score
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "username": user.username, 
        "role": user.role
    }

@router.post("/signup")
def signup(username: str, password: str, role: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(username=username, password=hash_password(password), role=role)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# ---------------------------------------------------------
# JOB MANAGEMENT
# ---------------------------------------------------------

@router.post("/jobs/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = JobPost(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/jobs/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(JobPost).all()

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Cascade delete: Remove all candidates who applied for this job
    db.query(Candidate).filter(Candidate.job_id == job_id).delete()
    db.delete(job)
    db.commit()
    return {"message": "Job and all associated applications deleted"}

# ---------------------------------------------------------
# CANDIDATE & AI SCORING
# ---------------------------------------------------------

@router.post("/apply/")
async def apply_job(
    job_id: int = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. PREVENT DUPLICATES: Check if this email already applied for THIS job
    existing_application = db.query(Candidate).filter(
        Candidate.job_id == job_id, 
        Candidate.email == email
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=400, 
            detail="You have already applied for this position."
        )

    # 2. FILE HANDLING: Ensure directory exists and save PDF
    os.makedirs("uploads", exist_ok=True)
    filename = f"{uuid.uuid4()}_{file.filename}"
    upload_path = os.path.join("uploads", filename)
    
    with open(upload_path, "wb") as buffer:
        buffer.write(await file.read())

    # 3. AI ANALYSIS
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Extract text and calculate score using your services
    extracted_text = extract_text(upload_path) 
    score = calculate_match_score(extracted_text, job.requirements)

    # Generate insights for the UI
    ai_summary = f"Candidate shows a {score}% match for the {job.title} role based on extracted skills."
    # Optional: If your ai_service can extract a list of skills, replace this placeholder
    ai_skills = "Extracted from Resume Analysis" 

    # 4. SAVE TO DATABASE
    new_candidate = Candidate(
        job_id=job_id,
        full_name=full_name,
        email=email,
        file_path=filename,           # Key for PDF preview
        resume_text=extracted_text,   # Key for raw text box
        resume_summary=ai_summary,    # Key for AI Insights
        skills=ai_skills,             # Key for Skills section
        score=float(score),
        status="Pending"
    )
    
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    
    return {"message": "Application submitted successfully", "score": new_candidate.score}

@router.get("/jobs/{job_id}/shortlist", response_model=List[CandidateResponse])
def get_shortlist(job_id: int, db: Session = Depends(get_db)):
    # Returns candidates for a specific job, highest scores first
    return db.query(Candidate).filter(
        Candidate.job_id == job_id
    ).order_by(Candidate.score.desc()).all()

@router.put("/candidates/{candidate_id}/status")
def update_candidate_status(candidate_id: int, status: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate.status = status
    db.commit()
    return {"message": f"Candidate status updated to {status}"}

@router.get("/my-applications/{email}", response_model=List[CandidateResponse])
def get_my_applications(email: str, db: Session = Depends(get_db)):
    """
    Returns application status including the Job Title using a SQL Join.
    """
    results = db.query(Candidate, JobPost.title).join(
        JobPost, Candidate.job_id == JobPost.id
    ).filter(Candidate.email == email).all()
    
    response_data = []
    for candidate, title in results:
        # Map SQLAlchemy object to Pydantic schema and inject job_title
        c_dict = CandidateResponse.from_orm(candidate)
        c_dict.job_title = title
        response_data.append(c_dict)
        
    return response_data