from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class Language(BaseModel):
    name: str
    proficiency: str