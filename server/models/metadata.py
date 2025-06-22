from pydantic import BaseModel, Field
from datetime import datetime

class Metadata(BaseModel):
    extracted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    anonymized: bool = True
