from models.todos import Todo
# from schema.schemas import list_serial
from fastapi import APIRouter
from models.resume import Resume
from config.database import collection_resume
from schema.schemas import list_resume_serial, individual_resume_serial
from bson import ObjectId

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("/")
async def get_resumes():
    resumes = list_resume_serial(collection_resume.find())
    return resumes


@router.post("/")
async def post_resume(resume: Resume):
    new_resume = resume.dict() #dict(resume) does not work because, the resume has several nested pydantic models.  Before calling insert_one, convert the entire Pydantic object to a plain dictionary, with nested models unwrapped.  .dict() properly serializes nested Pydantic models into native dicts that MongoDB can handle.
    result = collection_resume.insert_one(new_resume)
    inserted_resume = collection_resume.find_one({"_id": result.inserted_id})
    return individual_resume_serial(inserted_resume)

from fastapi import HTTPException

@router.get("/{id}")
async def get_resume_by_id(id: str):
    resume = collection_resume.find_one({"_id": ObjectId(id)})
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return individual_resume_serial(resume)
