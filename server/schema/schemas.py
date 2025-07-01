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

from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import datetime

from pydantic import field_validator
from typing import Union

class EmploymentProofBase(BaseModel):
    employee_name: Optional[str] = None
    designation: Optional[str] = None
    valid: Optional[Union[bool, str]] = None  # Accepts both bool and str

    @field_validator('valid', mode='before')
    def convert_bool_to_str(cls, v):
        if isinstance(v, bool):
            return str(v).lower()  # Converts True → "true", False → "false"
        return v

    class Config:
        from_attributes = True

class PayslipComponents(BaseModel):
    basic: Optional[float] = None
    hra: Optional[float] = None

class PayslipCreate(BaseModel):
    file_processed: str
    components: Optional[PayslipComponents] = None
    employment_proof: EmploymentProofBase

class PayslipResponse(BaseModel):
    id: UUID4
    file_processed: str
    components: Optional[Dict] = None
    employment_proof: EmploymentProofBase
    created_at: datetime

    class Config:
        from_attributes = True

class ExperienceLetterDataBase(BaseModel):
    """Base model for extracted experience letter data."""
    org_name: Optional[str] = None
    job_title: Optional[str] = None
    employee_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: Optional[Union[str, float]] = None  # Allow both string and float

    @field_validator('duration_years', mode='before')
    def convert_duration_to_str(cls, v):
        if isinstance(v, (float, int)):
            return str(v)
        return v

class ExperienceLetterFormattingBase(BaseModel):
    """Base model for formatting consistency checks."""
    all_required_fields_present: Optional[Union[bool, str]] = None
    dates_valid: Optional[Union[bool, str]] = None
    dates_logical: Optional[Union[bool, str]] = None
    organization_name_valid: Optional[Union[bool, str]] = None
    job_title_valid: Optional[Union[bool, str]] = None
    employee_name_valid: Optional[Union[bool, str]] = None
    manager_info_present: Optional[Union[bool, str]] = None

    @field_validator('*', mode='before')
    def convert_bool_to_str(cls, v):
        if isinstance(v, bool):
            return str(v).lower()
        return v

class ExperienceLetterAnomalyBase(BaseModel):
    """Base model for experience letter anomalies."""
    anomaly_type: str
    description: Optional[str] = None

class ExperienceLetterResponse(BaseModel):
    """Model for experience letter response."""
    id: UUID
    file_processed: str
    raw_text_length: Optional[str] = None
    confidence_score: Optional[str] = None
    extracted_data: Optional[ExperienceLetterDataBase] = None
    formatting_consistency: Optional[ExperienceLetterFormattingBase] = None
    anomalies: List[ExperienceLetterAnomalyBase]
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

class ExperienceLetterCreate(BaseModel):
    """Model for creating a new experience letter record."""
    file_processed: str
    raw_text_length: Optional[Union[str, int]] = None  # Allow both string and int
    confidence_score: Optional[Union[str, float]] = None  # Allow both string and float
    extracted_data: ExperienceLetterDataBase
    formatting_consistency: ExperienceLetterFormattingBase
    anomalies: List[ExperienceLetterAnomalyBase] = []

    @field_validator('raw_text_length', 'confidence_score', mode='before')
    def convert_numbers_to_str(cls, v):
        if isinstance(v, (int, float)):
            return str(v)
        return v


class ExperienceLetterUpdate(BaseModel):
    """Model for updating an experience letter record."""
    file_processed: Optional[str] = None
    raw_text_length: Optional[str] = None
    confidence_score: Optional[str] = None
    extracted_data: Optional[ExperienceLetterDataBase] = None
    formatting_consistency: Optional[ExperienceLetterFormattingBase] = None
    anomalies: Optional[List[ExperienceLetterAnomalyBase]] = None