# models.py
from pydantic import BaseModel
from typing import List, Optional

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    summary: Optional[str] = None
    # summary: Optional[str]

class Education(BaseModel):
    institution: str
    location: Optional[str] = None
    degree: str
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None

class Experience(BaseModel):
    position: str
    company: str
    dates: str
    achievements: Optional[List[str]] = []

class Project(BaseModel):
    title: str
    description: str
    technologies: Optional[List[str]] = []
    results: Optional[List[str]] = []

class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None

class Additional(BaseModel):
    title: str
    description: str

class CVData(BaseModel):
    personal_info: PersonalInfo
    education: Optional[List[Education]] = []
    experience: Optional[List[Experience]] = []
    skillsets: Optional[List[str]] = []
    projects: Optional[List[Project]] = []
    certifications: Optional[List[Certification]] = []
    additional: Optional[List[Additional]] = []

class ChatToCVRequest(BaseModel):
    session_id: str
    message: str









# # models.py
# from pydantic import BaseModel
# from typing import List, Optional

# class PersonalInfo(BaseModel):
#     full_name: str
#     email: str
#     phone: Optional[str]
#     address: Optional[str]
#     linkedin: Optional[str]
#     github: Optional[str]
#     summary: Optional[str]

# class Experience(BaseModel):
#     position: str
#     company: str
#     duration: str
#     description: Optional[str]

# class Education(BaseModel):
#     degree: str
#     institution: str
#     year: str
#     description: Optional[str]

# class Project(BaseModel):
#     name: str
#     description: str
#     technologies: Optional[List[str]]

# class Certification(BaseModel):
#     name: str
#     issuer: str
#     date: str

# class CVData(BaseModel):
#     personal_info: PersonalInfo
#     experience: Optional[List[Experience]] = []
#     education: Optional[List[Education]] = []
#     skills: Optional[List[str]] = []
#     projects: Optional[List[Project]] = []
#     certifications: Optional[List[Certification]] = []
#     additional: Optional[str] = ""

# # Chat request model
# class ChatToCVRequest(BaseModel):
#     session_id: str
#     message: str