# def individual_serial(todo) -> dict:
#     return {
#       "id": str(todo["_id"]),
#       "name": todo["name"],
#       "description": todo["description"],
#       "complete": todo["complete"]
#     }


# def list_serial(todos) -> list:
#     return[individual_serial(todo) for todo in todos]

def individual_resume_serial(resume: dict) -> dict:
    return {
        "id": str(resume["_id"]),
        "file_name": resume["file_name"],
        "personal_information": resume["personal_information"],
        "education": resume.get("education", []),
        "skills": resume.get("skills", {}),
        "languages": resume.get("languages", []),
        "tools": resume.get("tools", []),
        "concepts": resume.get("concepts", []),
        "others": resume.get("others", []),
        "metadata": resume.get("metadata", {})
    }

def list_resume_serial(resumes: list) -> list:
    return [individual_resume_serial(resume) for resume in resumes]

def individual_personal_info_serial(info: dict) -> dict:
    return {
        "name": info.get("name"),
        "email": info.get("email"),
        "phone": info.get("phone"),
        "location": info.get("location")
    }

def list_personal_info_serial(info_list: list) -> list:
    return [individual_personal_info_serial(info) for info in info_list]


def individual_education_serial(edu: dict) -> dict:
    return {
        "institution": edu.get("institution"),
        "location": edu.get("location"),
        "date": edu.get("date")
    }

def list_education_serial(education_list: list) -> list:
    return [individual_education_serial(edu) for edu in education_list]

def individual_language_serial(lang: dict) -> dict:
    return {
        "name": lang.get("name"),
        "proficiency": lang.get("proficiency")
    }

def list_language_serial(language_list: list) -> list:
    return [individual_language_serial(lang) for lang in language_list]
