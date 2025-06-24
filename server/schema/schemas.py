from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

class PersonalInformationBase(BaseModel):
    """Base model for personal information."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class EducationBase(BaseModel):
    """Base model for education details."""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None  # Expected format: e.g., "YYYY-MM-DD" or free-form

class LanguageBase(BaseModel):
    """Base model for language proficiency."""
    name: str

class MetadataBase(BaseModel):
    """Base model for resume metadata."""
    extracted_at: str  # ISO 8601 datetime string, e.g., "2025-06-22T15:50:45Z"
    anonymized: bool

    @validator("extracted_at")
    def validate_extracted_at(cls, v):
        """Validate that extracted_at is a valid ISO 8601 datetime string."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("extracted_at must be a valid ISO 8601 datetime string")
        return v

class ResumeCreate(BaseModel):
    """Model for creating a new resume."""
    file_name: str
    personal_information: PersonalInformationBase
    education: List[EducationBase]
    skills: Optional[Dict[str, List[str]]] = {}  # Allow empty skills dictionary
    languages: List[LanguageBase]
    tools: List[str]
    concepts: List[str]
    others: List[str]
    resume_metadata: MetadataBase

class ResumeResponse(BaseModel):
    """Model for resume response."""
    id: UUID
    file_name: str
    personal_information: PersonalInformationBase
    education: List[EducationBase]
    skills: Dict[str, List[str]]
    languages: List[LanguageBase]
    tools: List[str]
    concepts: List[str]
    others: List[str]
    resume_metadata: MetadataBase
    created_at: datetime

    class Config:
        from_attributes = True