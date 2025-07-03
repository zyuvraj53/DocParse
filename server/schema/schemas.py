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

from pydantic import BaseModel, field_validator
from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID

# Certificate Schemas
class CertificateBase(BaseModel):
    university: Optional[str] = None
    degree: Optional[str] = None
    gpa: Optional[float] = None
    graduation_date: Optional[str] = None
    source_file: Optional[str] = None
    processed_at: Optional[datetime] = None
    text_length: Optional[int] = None

class CertificateCreate(CertificateBase):
    pass

class CertificateResponse(CertificateBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CertificateUpdate(BaseModel):
    university: Optional[str] = None
    degree: Optional[str] = None
    gpa: Optional[float] = None
    graduation_date: Optional[str] = None
    source_file: Optional[str] = None
    processed_at: Optional[datetime] = None
    text_length: Optional[int] = None

# Confidence Scores Schemas
class ConfidenceScoreBase(BaseModel):
    university: Optional[float] = None
    degree: Optional[float] = None
    gpa: Optional[float] = None
    graduation_date: Optional[float] = None
    overall: Optional[float] = None

class ConfidenceScoreCreate(ConfidenceScoreBase):
    certificate_id: UUID

class ConfidenceScoreResponse(ConfidenceScoreBase):
    id: UUID
    certificate_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Extraction Methods Schemas
class ExtractionMethodBase(BaseModel):
    university: Optional[str] = None
    degree: Optional[str] = None
    gpa: Optional[str] = None
    graduation_date: Optional[str] = None

class ExtractionMethodCreate(ExtractionMethodBase):
    certificate_id: UUID

class ExtractionMethodResponse(ExtractionMethodBase):
    id: UUID
    certificate_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Raw Matches Schemas (all follow same pattern)
class RawMatchBase(BaseModel):
    match: Optional[str] = None

class RawMatchCreate(RawMatchBase):
    certificate_id: UUID

class RawMatchResponse(RawMatchBase):
    id: UUID
    certificate_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Extracted Entities Schemas (all follow same pattern)
class ExtractedEntityBase(BaseModel):
    university: Optional[str] = None  # For universities
    organization: Optional[str] = None  # For organizations
    person: Optional[str] = None  # For persons

class ExtractedEntityCreate(ExtractedEntityBase):
    certificate_id: UUID

class ExtractedEntityResponse(ExtractedEntityBase):
    id: UUID
    certificate_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Authenticity Schemas
class AuthenticityBase(BaseModel):
    overall_score: Optional[float] = None
    document_hash: Optional[str] = None

class AuthenticityCreate(AuthenticityBase):
    certificate_id: UUID

class AuthenticityResponse(AuthenticityBase):
    id: UUID
    certificate_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Digital Signatures Schemas
class DigitalSignatureBase(BaseModel):
    has_digital_signature: Optional[bool] = None
    signature_count: Optional[int] = None
    encrypted: Optional[bool] = None
    error: Optional[str] = None

class DigitalSignatureCreate(DigitalSignatureBase):
    authenticity_id: UUID

class DigitalSignatureResponse(DigitalSignatureBase):
    id: UUID
    authenticity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Security Features Schemas
class SecurityFeatureBase(BaseModel):
    feature: Optional[str] = None

class SecurityFeatureCreate(SecurityFeatureBase):
    digital_signature_id: UUID

class SecurityFeatureResponse(SecurityFeatureBase):
    id: UUID
    digital_signature_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Certificate Metadata Schemas
class CertificateMetadataBase(BaseModel):
    creator: Optional[str] = None
    producer: Optional[str] = None
    subject: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None

class CertificateMetadataCreate(CertificateMetadataBase):
    digital_signature_id: UUID

class CertificateMetadataResponse(CertificateMetadataBase):
    id: UUID
    digital_signature_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# QR Code Schemas
class QRCodeBase(BaseModel):
    qr_code: Optional[str] = None

class QRCodeCreate(QRCodeBase):
    authenticity_id: UUID

class QRCodeResponse(QRCodeBase):
    id: UUID
    authenticity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# QR Verification Schemas
class QRVerificationBase(BaseModel):
    verification: Optional[str] = None

class QRVerificationCreate(QRVerificationBase):
    authenticity_id: UUID

class QRVerificationResponse(QRVerificationBase):
    id: UUID
    authenticity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Authenticity Indicators Schemas
class AuthenticityIndicatorBase(BaseModel):
    indicator: Optional[str] = None

class AuthenticityIndicatorCreate(AuthenticityIndicatorBase):
    authenticity_id: UUID

class AuthenticityIndicatorResponse(AuthenticityIndicatorBase):
    id: UUID
    authenticity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Risk Factors Schemas
class RiskFactorBase(BaseModel):
    risk_factor: Optional[str] = None

class RiskFactorCreate(RiskFactorBase):
    authenticity_id: UUID

class RiskFactorResponse(RiskFactorBase):
    id: UUID
    authenticity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Recommendations Schemas
class RecommendationBase(BaseModel):
    recommendation: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    authenticity_id: UUID

class RecommendationResponse(RecommendationBase):
    id: UUID
    authenticity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True