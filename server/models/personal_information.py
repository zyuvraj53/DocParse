from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class PersonalInformation(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    location: Optional[str]