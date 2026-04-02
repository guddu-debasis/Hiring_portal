from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

from app.core.database import get_db
from app.models.candidate import JobPost, Candidate, User
from app.schemas.candidate import JobCreate, JobResponse, CandidateResponse
from app.services.ai_service import extract_text, calculate_match_score
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

# ---------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# ---------------------------------------------------------

from app.core.security import create_access_token, verify_password, hash_password

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate Token
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
        raise HTTPException(status_code=400, detail="Username exists")
    new_user = User(username=username, password=hash_password(password), role=role)
    db.add(new_user)
    db.commit()
    return {"message": "Success"}

# ---------------------------------------------------------
# JOB MANAGEMENT ENDPOINTS
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
    # Clean up candidates for this job first
    db.query(Candidate).filter(Candidate.job_id == job_id).delete()
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}

# ---------------------------------------------------------
# CANDIDATE & AI SCORING ENDPOINTS
# ---------------------------------------------------------

@router.post("/apply/")
async def apply(
    job_id: int = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save PDF temporarily
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Extract and Score
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    resume_text = extract_text(file_path)
    score = calculate_match_score(resume_text, job.requirements)

    # 2. Save to DB
    new_candidate = Candidate(
        job_id=job_id,
        full_name=full_name,
        email=email,
        resume_text=resume_text,
        score=score,
        status="Pending"
    )
    db.add(new_candidate)
    db.commit()
    
    os.remove(file_path) # Clean up
    return {"score": score, "status": "Pending"}

@router.get("/jobs/{job_id}/shortlist", response_model=List[CandidateResponse])
def get_shortlist(job_id: int, db: Session = Depends(get_db)):
    return db.query(Candidate).filter(Candidate.job_id == job_id).order_by(Candidate.score.desc()).all()

@router.put("/candidates/{candidate_id}/status")
def update_candidate_status(candidate_id: int, status: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.status = status
    db.commit()
    return {"message": f"Candidate marked as {status}"}

@router.get("/my-applications/{email}", response_model=List[CandidateResponse])
def get_my_applications(email: str, db: Session = Depends(get_db)):
    """
    Returns application status including the Job Title using a SQL Join.
    """
    results = db.query(Candidate, JobPost.title).join(
        JobPost, Candidate.job_id == JobPost.id
    ).filter(Candidate.email == email).all()
    
    # We manually map the job title into our response schema
    response_data = []
    for candidate, title in results:
        # Use Pydantic's from_orm and manually add the title
        c_dict = CandidateResponse.from_orm(candidate)
        c_dict.job_title = title
        response_data.append(c_dict)
        
    return response_data