from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class Education(BaseModel):
    institution: Optional[str]
    location: Optional[str]
    date: Optional[str]
