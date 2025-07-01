from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from models import models
from schema import schemas
from config import database

from uuid import UUID
import shutil
import os
from typing import List
from pdf_extractor.extractor import EnhancedPDFExtractor
from payslip_parser.parser import process_payslip  # Import the payslip parser
from contextlib import redirect_stdout
import io
import traceback

router_resumes = APIRouter(prefix="/resumes", tags=["Resumes"])

@router_resumes.get("/", response_model=list[schemas.ResumeResponse])
async def get_resumes(db: Session = Depends(database.get_db)):
    resumes = db.query(models.Resume).all()
    return resumes

@router_resumes.post("/", response_model=schemas.ResumeResponse)
async def post_resume(resume: schemas.ResumeCreate, db: Session = Depends(database.get_db)):
    # Create resume
    db_resume = models.Resume(
        file_name=resume.file_name,
        skills=resume.skills,
        tools=resume.tools,
        concepts=resume.concepts,
        others=resume.others,
        resume_metadata=resume.resume_metadata.dict()
    )
    db.add(db_resume)
    db.flush()  # Get resume.id before committing

    # Create personal information
    db_personal_info = models.PersonalInformation(
        resume_id=db_resume.id,
        **resume.personal_information.dict()
    )
    db.add(db_personal_info)

    # Create education entries
    for edu in resume.education:
        db_education = models.Education(resume_id=db_resume.id, **edu.dict())
        db.add(db_education)

    # Create language entries
    for lang in resume.languages:
        db_language = models.Language(resume_id=db_resume.id, **lang.dict())
        db.add(db_language)

    db.commit()
    db.refresh(db_resume)
    return db_resume

@router_resumes.get("/{id}", response_model=schemas.ResumeResponse)
async def get_resume_by_id(id: UUID, db: Session = Depends(database.get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

router_uploads = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR_RESUMES = "uploads_resume"
UPLOAD_DIR_PAYSLIPS = "uploads_payslips"

if not os.path.exists(UPLOAD_DIR_RESUMES):
    os.makedirs(UPLOAD_DIR_RESUMES)

if not os.path.exists(UPLOAD_DIR_PAYSLIPS):
    os.makedirs(UPLOAD_DIR_PAYSLIPS)

@router_uploads.post("/upload-resumes")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDF files for resumes
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR_RESUMES, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file.size,
                "path": file_path
            })
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    }

@router_uploads.post("/process-resumes")
async def process_resumes(file: UploadFile = File(...)):
    try:
        uploads_dir = UPLOAD_DIR_RESUMES
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        extractor = EnhancedPDFExtractor()
        sample_jd = "Software Engineer with Python and JavaScript experience"
        result = extractor.process_pdf(file_path, sample_jd, anonymize=True)
        return {
            "message": "Successfully processed resume",
            "status": "completed",
            "resumes": [result]
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )

@router_uploads.get("/")
async def root():
    return {"message": "Resume and Payslip Parser API"}

router_payslips = APIRouter(prefix="/payslips", tags=["Payslips"])

@router_payslips.get("/", response_model=list[schemas.PayslipResponse])
async def get_payslips(db: Session = Depends(database.get_db)):
    payslips = db.query(models.Payslip).all()
    return payslips

@router_payslips.post("/", response_model=schemas.PayslipResponse)
async def post_payslip(payslip: schemas.PayslipCreate, db: Session = Depends(database.get_db)):
    # Validate file_processed path
    if not payslip.file_processed.startswith(UPLOAD_DIR_PAYSLIPS):
        payslip.file_processed = os.path.join(UPLOAD_DIR_PAYSLIPS, os.path.basename(payslip.file_processed))

    # Create payslip
    db_payslip = models.Payslip(
        file_processed=payslip.file_processed,
        components=payslip.components.dict() if payslip.components else None
    )
    db.add(db_payslip)
    db.flush()  # Get payslip.id before committing

    # Create employment proof
    db_employment_proof = models.EmploymentProof(
        payslip_id=db_payslip.id,
        employee_name=payslip.employment_proof.employee_name,
        designation=payslip.employment_proof.designation,
        valid=str(payslip.employment_proof.valid).lower() if payslip.employment_proof.valid is not None else None
    )
    db.add(db_employment_proof)

    db.commit()
    db.refresh(db_payslip)
    return db_payslip

@router_payslips.get("/{id}", response_model=schemas.PayslipResponse)
async def get_payslip_by_id(id: UUID, db: Session = Depends(database.get_db)):
    payslip = db.query(models.Payslip).filter(models.Payslip.id == id).first()
    if payslip is None:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return payslip

@router_uploads.post("/upload-payslips")
async def upload_payslips(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDF files for payslips
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR_PAYSLIPS, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file.size,
                "path": file_path
            })
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    }

@router_uploads.post("/process-payslips")
async def process_payslips(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        # Save the file
        uploads_dir = UPLOAD_DIR_PAYSLIPS
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Process payslip
        result = process_payslip(file_path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Create database objects
        payslip_data = schemas.PayslipCreate(**result)
        
        db_payslip = models.Payslip(
            file_processed=payslip_data.file_processed,
            components=payslip_data.components.dict() if payslip_data.components else None
        )
        db.add(db_payslip)
        db.flush()

        db_employment_proof = models.EmploymentProof(
            payslip_id=db_payslip.id,
            employee_name=payslip_data.employment_proof.employee_name,
            designation=payslip_data.employment_proof.designation,
            valid=payslip_data.employment_proof.valid
        )
        db.add(db_employment_proof)

        db.commit()
        db.refresh(db_payslip)

        # Build response
        response = schemas.PayslipResponse.from_orm(db_payslip)
        
        return {
            "message": "Successfully processed and saved payslip",
            "status": "completed",
            "payslip": response
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Add to your existing imports
from experience_letter_parser.parser import process_letter  # Import the experience letter parser

# Add a new router for experience letters
router_experience_letters = APIRouter(
    prefix="/experience-letters", 
    tags=["Experience Letters"]
)

# Add a new upload directory
UPLOAD_DIR_EXPERIENCE_LETTERS = "uploads_experience_letters"
if not os.path.exists(UPLOAD_DIR_EXPERIENCE_LETTERS):
    os.makedirs(UPLOAD_DIR_EXPERIENCE_LETTERS)

# Experience Letter Routes
@router_experience_letters.get("/", response_model=list[schemas.ExperienceLetterResponse])
async def get_experience_letters(db: Session = Depends(database.get_db)):
    experience_letters = db.query(models.ExperienceLetter).all()
    return experience_letters

@router_experience_letters.post("/", response_model=schemas.ExperienceLetterResponse)
async def post_experience_letter(
    experience_letter: schemas.ExperienceLetterCreate, 
    db: Session = Depends(database.get_db)
):
    # Validate file_processed path
    if not experience_letter.file_processed.startswith(UPLOAD_DIR_EXPERIENCE_LETTERS):
        experience_letter.file_processed = os.path.join(
            UPLOAD_DIR_EXPERIENCE_LETTERS, 
            os.path.basename(experience_letter.file_processed)
        )

    # Create experience letter
    db_experience_letter = models.ExperienceLetter(
        file_processed=experience_letter.file_processed,
        raw_text_length=experience_letter.raw_text_length,
        confidence_score=experience_letter.confidence_score
    )
    db.add(db_experience_letter)
    db.flush()

    # Create extracted data
    db_extracted_data = models.ExperienceLetterData(
        experience_letter_id=db_experience_letter.id,
        **experience_letter.extracted_data.dict()
    )
    db.add(db_extracted_data)

    # Create formatting consistency
    db_formatting = models.ExperienceLetterFormatting(
        experience_letter_id=db_experience_letter.id,
        **experience_letter.formatting_consistency.dict()
    )
    db.add(db_formatting)

    # Create anomalies
    for anomaly in experience_letter.anomalies:
        db_anomaly = models.ExperienceLetterAnomaly(
            experience_letter_id=db_experience_letter.id,
            **anomaly.dict()
        )
        db.add(db_anomaly)

    db.commit()
    db.refresh(db_experience_letter)
    return db_experience_letter

@router_experience_letters.get("/{id}", response_model=schemas.ExperienceLetterResponse)
async def get_experience_letter_by_id(id: UUID, db: Session = Depends(database.get_db)):
    experience_letter = db.query(models.ExperienceLetter).filter(
        models.ExperienceLetter.id == id
    ).first()
    if experience_letter is None:
        raise HTTPException(status_code=404, detail="Experience letter not found")
    return experience_letter

# Add to your existing uploads router
@router_uploads.post("/upload-experience-letters")
async def upload_experience_letters(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDF files for experience letters
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR_EXPERIENCE_LETTERS, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file.size,
                "path": file_path
            })
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    }

@router_uploads.post("/process-experience-letters")
async def process_experience_letters(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db)
):
    try:
        # Save the file
        uploads_dir = UPLOAD_DIR_EXPERIENCE_LETTERS
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Process experience letter
        result = process_letter(file_path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Create database objects
        experience_letter_data = schemas.ExperienceLetterCreate(**result)
        
        db_experience_letter = models.ExperienceLetter(
            file_processed=experience_letter_data.file_processed,
            raw_text_length=experience_letter_data.raw_text_length,
            confidence_score=experience_letter_data.confidence_score
        )
        db.add(db_experience_letter)
        db.flush()

        # Create extracted data
        db_extracted_data = models.ExperienceLetterData(
            experience_letter_id=db_experience_letter.id,
            **experience_letter_data.extracted_data.dict()
        )
        db.add(db_extracted_data)

        # Create formatting consistency
        db_formatting = models.ExperienceLetterFormatting(
            experience_letter_id=db_experience_letter.id,
            **experience_letter_data.formatting_consistency.dict()
        )
        db.add(db_formatting)

        # Create anomalies
        for anomaly in experience_letter_data.anomalies:
            db_anomaly = models.ExperienceLetterAnomaly(
                experience_letter_id=db_experience_letter.id,
                **anomaly.dict()
            )
            db.add(db_anomaly)

        db.commit()
        db.refresh(db_experience_letter)

        # Convert SQLAlchemy objects to dictionaries
        response_data = {
            "id": db_experience_letter.id,
            "file_processed": db_experience_letter.file_processed,
            "raw_text_length": db_experience_letter.raw_text_length,
            "confidence_score": db_experience_letter.confidence_score,
            "created_at": db_experience_letter.created_at,
            "extracted_data": {
                "org_name": db_extracted_data.org_name,
                "job_title": db_extracted_data.job_title,
                "employee_name": db_extracted_data.employee_name,
                "start_date": db_extracted_data.start_date,
                "end_date": db_extracted_data.end_date,
                "duration_years": db_extracted_data.duration_years
            },
            "formatting_consistency": {
                "all_required_fields_present": db_formatting.all_required_fields_present,
                "dates_valid": db_formatting.dates_valid,
                "dates_logical": db_formatting.dates_logical,
                "organization_name_valid": db_formatting.organization_name_valid,
                "job_title_valid": db_formatting.job_title_valid,
                "employee_name_valid": db_formatting.employee_name_valid,
                "manager_info_present": db_formatting.manager_info_present
            },
            "anomalies": [
                {
                    "anomaly_type": a.anomaly_type,
                    "description": a.description
                } for a in db_experience_letter.anomalies
            ]
        }
        
        # Validate with response model
        response = schemas.ExperienceLetterResponse(**response_data)
        
        return {
            "message": "Successfully processed and saved experience letter",
            "status": "completed",
            "experience_letter": response
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))