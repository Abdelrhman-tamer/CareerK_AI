from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import cv_routes, recommender_routes, course_recommender_routes, amr_recommender

app = FastAPI(title="CareerK AI Backend")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routers
app.include_router(cv_routes.router, prefix="", tags=["CV Generation"])
# app.include_router(recommender_routes.router, prefix="/recommend", tags=["Recommendation"])
app.include_router(course_recommender_routes.router, prefix="/courses", tags=["ML Course Recommender"])  # ✅ NEW
app.include_router(amr_recommender.router, prefix="/recommend", tags=["Structured Recommender"])



# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from typing import List, Optional
# from recommender import recommend_for_developer
# import traceback
# import logging

# # Logger setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("CareerK-Recommender")

# app = FastAPI(title="CareerK AI Job & Service Recommender")

# # ======================
# # ✅ Pydantic Models
# # ======================

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

# # ======================
# # ✅ Endpoint
# # ======================

# @app.post("/recommend", response_model=RecommendationResponse)
# def recommend(data: RecommendationRequest):
#     try:
#         logger.info(f"Received request for developer ID: {data.developer.id}")
#         logger.info(f"{len(data.job_posts)} job posts | {len(data.service_posts)} service posts")

#         result = recommend_for_developer(
#             developer=data.developer.dict(),
#             job_posts=[job.dict(by_alias=True) for job in data.job_posts],
#             service_posts=[srv.dict() for srv in data.service_posts]
#         )
#         return result

#     except Exception as e:
#         logger.error("🔥 Recommendation failed!")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
