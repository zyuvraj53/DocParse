from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from .personal_information import PersonalInformation
from .education import Education
from .language import Language
from .metadata import Metadata

class Resume(BaseModel):
    file_name: str
    personal_information: PersonalInformation
    education: List[Education]
    skills: Dict[str, List[str]]
    languages: List[Language]
    tools: List[str]
    concepts: List[str]
    others: List[str]
    metadata: Metadata = Field(default_factory=Metadata)