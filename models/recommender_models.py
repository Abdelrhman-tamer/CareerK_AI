from pydantic import BaseModel
from typing import List, Optional

class DeveloperInput(BaseModel):
    id: str
    brief_bio: Optional[str] = None
    skills: Optional[List[str]] = []
    years_of_experience: Optional[int] = None
    previous_job: Optional[str] = None
    track_level: Optional[str] = None
    cv_text: Optional[str] = None  # ✅ unified field only

class JobPostInput(BaseModel):
    id: str
    title: str
    job_description: str
    skills: Optional[List[str]] = []

class ServicePostInput(BaseModel):
    id: str
    title: str
    description: str
    required_skills: Optional[List[str]] = []

class RecommendationRequest(BaseModel):
    developer: DeveloperInput
    job_posts: List[JobPostInput]
    service_posts: List[ServicePostInput]

class ScoredItem(BaseModel):
    id: str
    score: float

class RecommendationResponse(BaseModel):
    job_recommendations: List[ScoredItem]
    service_recommendations: List[ScoredItem]



# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from typing import List, Optional
# import traceback
# import logging

# # Logger setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("CareerK-Recommender")


# class DeveloperInput(BaseModel):
#     id: str
#     brief_bio: Optional[str] = None
#     skills: Optional[List[str]] = []
#     years_of_experience: Optional[int] = None
#     previous_job: Optional[str] = None
#     track_level: Optional[str] = None
#     uploaded_cv_text: Optional[str] = None
#     generated_cv_text: Optional[str] = None

# class JobPostInput(BaseModel):
#     id: str
#     title: str
#     job_description: str
#     skills: Optional[List[str]] = []

# class ServicePostInput(BaseModel):
#     id: str
#     title: str
#     description: str
#     skills: Optional[List[str]] = []

# class RecommendationRequest(BaseModel):
#     developer: DeveloperInput
#     job_posts: List[JobPostInput]
#     service_posts: List[ServicePostInput]

# class ScoredItem(BaseModel):
#     id: str
#     score: float

# class RecommendationResponse(BaseModel):
#     job_recommendations: List[ScoredItem]
#     service_recommendations: List[ScoredItem]
