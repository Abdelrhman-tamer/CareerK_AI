from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import spacy
import re
import numpy as np

router = APIRouter()

# Load spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

bert_model = SentenceTransformer('all-mpnet-base-v2')

# ==== Data Models ====
class DeveloperInput(BaseModel):
    id: str
    brief_bio: Optional[str] = None
    skills: Optional[List[str]] = []
    years_of_experience: Optional[int] = None
    previous_job: Optional[str] = None
    track_level: Optional[str] = None
    cv_text: Optional[str] = None

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
    final_score: float
    similarity_score: Optional[float] = None
    experience_score: Optional[float] = None
    skill_score: Optional[float] = None

class RecommendationResponse(BaseModel):
    job_recommendations: List[ScoredItem]
    service_recommendations: List[ScoredItem]


# ==== Utility Functions ====
def advanced_preprocess(text: str) -> str:
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and len(token) > 2 and not token.is_digit
    ]
    return " ".join(tokens)

def parse_experience(text: str) -> tuple[int, int]:
    text = text.lower()
    patterns = [
        (r'(\d+)\s*\+\s*years?', 1),
        (r'at\s*least\s*(\d+)\s*years?', 1),
        (r'more\s*than\s*(\d+)\s*years?', 1),
        (r'minimum\s*of\s*(\d+)\s*years?', 1),
        (r'(\d+)\s*-\s*(\d+)\s*years?', 2),
        (r'(\d+)\s*years?', 1),
        (r'fresher|trainee|entry[- ]level', 0)
    ]
    for pattern, group_count in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if group_count == 0:
                return 0, 0
            nums = [int(n) for n in match.groups() if n.isdigit()]
            if group_count == 2 and len(nums) == 2:
                return min(nums), max(nums)
            elif nums:
                return nums[0], nums[0]
    return 0, 0

def calculate_experience_score(dev_exp: int, job_min_exp: int) -> float:
    if job_min_exp == 0:
        return 1.0  # لو الوظيفة مش طالبة خبرة
    if dev_exp >= job_min_exp:
        return 1.0
    else:
        return round(dev_exp / job_min_exp, 2)

def skill_score_calculator(dev_tokens: set, required_skills: List[str]) -> float:
    if not required_skills:
        return 0.0
    matched = 0
    for skill in required_skills:
        tokens = advanced_preprocess(skill).split()
        if all(t in dev_tokens for t in tokens):
            matched += 1
    return matched / len(required_skills)

def get_valid_cv_text(dev: DeveloperInput) -> str:
    parts = []
    if dev.cv_text:
        parts.append(dev.cv_text.strip())
    if dev.brief_bio:
        parts.append(dev.brief_bio.strip())
    if dev.previous_job:
        parts.append(dev.previous_job.strip())
    if dev.track_level:
        parts.append(dev.track_level.strip())
    if dev.years_of_experience:
        parts.append(str(dev.years_of_experience))
    if dev.skills:
        parts.append(" ".join(dev.skills))
    return " ".join([p for p in parts if p])

# ==== Main Endpoint ====
@router.post("/", response_model=RecommendationResponse)
async def recommend(payload: RecommendationRequest):
    try:
        dev = payload.developer
        cv_text = get_valid_cv_text(dev)

        if not cv_text:
            raise HTTPException(400, "cv_text and fallback fields are empty")

        processed_cv = advanced_preprocess(cv_text)
        cv_vector = np.array(bert_model.encode(processed_cv))
        cv_tokens = set(processed_cv.split())

        dev_exp = dev.years_of_experience or 0

        # ==== JOBS ====
        job_results = []
        for job in payload.job_posts:
            job_text = advanced_preprocess(f"{job.title} {' '.join(job.skills or [])} {job.job_description}")
            job_vector = np.array(bert_model.encode(job_text))
            similarity = cosine_similarity([cv_vector], [job_vector])[0][0]
            similarity = max(0.0, min(1.0, similarity))

            job_min_exp, _ = parse_experience(job.job_description or "")
            experience_score = calculate_experience_score(dev_exp, job_min_exp)

            skill_score = skill_score_calculator(cv_tokens, job.skills or [])
            final_score = (0.65 * similarity) + (0.15 * experience_score) + (0.2 * skill_score)

            job_results.append(ScoredItem(
                id=job.id,
                final_score=round(final_score, 4),
                similarity_score=round(similarity, 4),
                experience_score=round(experience_score, 4),
                skill_score=round(skill_score, 4)
            ))

        job_results = [j for j in job_results if j.final_score >= 0.4]
        job_results.sort(key=lambda x: x.final_score, reverse=True)

        # ==== SERVICES ====
        service_results = []
        for sp in payload.service_posts:
            sp_text = advanced_preprocess(f"{sp.title} {sp.description} {' '.join(sp.required_skills or [])}")
            sp_vector = np.array(bert_model.encode(sp_text))
            similarity = cosine_similarity([cv_vector], [sp_vector])[0][0]
            similarity = max(0.0, min(1.0, similarity))

            skill_score = skill_score_calculator(cv_tokens, sp.required_skills or [])
            final_score = (0.5 * similarity) + (0.5 * skill_score)

            service_results.append(ScoredItem(
                id=sp.id,
                final_score=round(final_score, 4),
                similarity_score=round(similarity, 4),
                skill_score=round(skill_score, 4)
            ))

        service_results = [s for s in service_results if s.final_score >= 0.4]
        service_results.sort(key=lambda x: x.final_score, reverse=True)

        return RecommendationResponse(
            job_recommendations=job_results,
            service_recommendations=service_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")



# from fastapi import FastAPI, APIRouter, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer
# import spacy
# import re
# import numpy as np

# router = APIRouter()

# # Load spaCy
# try:
#     nlp = spacy.load("en_core_web_sm")
# except:
#     import spacy.cli
#     spacy.cli.download("en_core_web_sm")
#     nlp = spacy.load("en_core_web_sm")

# bert_model = SentenceTransformer('all-mpnet-base-v2')

# # ==== Data Models ====
# class DeveloperInput(BaseModel):
#     id: str
#     brief_bio: Optional[str] = None
#     skills: Optional[List[str]] = []
#     years_of_experience: Optional[int] = None
#     previous_job: Optional[str] = None
#     track_level: Optional[str] = None
#     cv_text: Optional[str] = None

# class JobPostInput(BaseModel):
#     id: str
#     title: str
#     job_description: str
#     skills: Optional[List[str]] = []

# class ServicePostInput(BaseModel):
#     id: str
#     title: str
#     description: str
#     required_skills: Optional[List[str]] = []

# class RecommendationRequest(BaseModel):
#     developer: DeveloperInput
#     job_posts: List[JobPostInput]
#     service_posts: List[ServicePostInput]

# class ScoredItem(BaseModel):
#     id: str
#     final_score: float
#     similarity_score: Optional[float] = None
#     experience_score: Optional[float] = None
#     skill_score: Optional[float] = None

# class RecommendationResponse(BaseModel):
#     job_recommendations: List[ScoredItem]
#     service_recommendations: List[ScoredItem]


# # ==== Utility Functions ====
# def advanced_preprocess(text: str) -> str:
#     text = re.sub(r'[^\w\s]', ' ', text.lower())
#     doc = nlp(text)
#     tokens = [
#         token.lemma_ for token in doc
#         if not token.is_stop and len(token) > 2 and not token.is_digit
#     ]
#     return " ".join(tokens)

# def parse_experience(text: str) -> tuple[int, int]:
#     text = text.lower()
#     patterns = [
#         (r'(\d+)\s*\+\s*years?', 1),
#         (r'at\s*least\s*(\d+)\s*years?', 1),
#         (r'more\s*than\s*(\d+)\s*years?', 1),
#         (r'minimum\s*of\s*(\d+)\s*years?', 1),
#         (r'(\d+)\s*-\s*(\d+)\s*years?', 2),
#         (r'(\d+)\s*years?', 1),
#         (r'fresher|trainee|entry[- ]level', 0)
#     ]
#     for pattern, group_count in patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             if group_count == 0:
#                 return 0, 0
#             nums = [int(n) for n in match.groups() if n.isdigit()]
#             if group_count == 2 and len(nums) == 2:
#                 return min(nums), max(nums)
#             elif nums:
#                 return nums[0], nums[0]
#     return 0, 0

# def calculate_experience_score(dev_exp: int, job_min_exp: int) -> float:
#     if job_min_exp == 0:
#         return 1.0  # لو الوظيفة مش طالبة خبرة
#     if dev_exp >= job_min_exp:
#         return 1.0
#     else:
#         return round(dev_exp / job_min_exp, 2)

# def skill_score_calculator(dev_tokens: set, required_skills: List[str]) -> float:
#     if not required_skills:
#         return 0.0
#     matched = 0
#     for skill in required_skills:
#         tokens = advanced_preprocess(skill).split()
#         if all(t in dev_tokens for t in tokens):
#             matched += 1
#     return matched / len(required_skills)

# def get_valid_cv_text(dev: DeveloperInput) -> str:
#     parts = []
#     if dev.cv_text:
#         parts.append(dev.cv_text.strip())
#     if dev.brief_bio:
#         parts.append(dev.brief_bio.strip())
#     if dev.previous_job:
#         parts.append(dev.previous_job.strip())
#     if dev.track_level:
#         parts.append(dev.track_level.strip())
#     if dev.years_of_experience:
#         parts.append(str(dev.years_of_experience))
#     if dev.skills:
#         parts.append(" ".join(dev.skills))
#     return " ".join([p for p in parts if p])

# # ==== Main Endpoint ====
# @router.post("/", response_model=RecommendationResponse)
# async def recommend(payload: RecommendationRequest):
#     try:
#         dev = payload.developer
#         cv_text = get_valid_cv_text(dev)

#         if not cv_text:
#             raise HTTPException(400, "cv_text and fallback fields are empty")

#         processed_cv = advanced_preprocess(cv_text)
#         cv_vector = np.array(bert_model.encode(processed_cv))
#         cv_tokens = set(processed_cv.split())

#         dev_exp = dev.years_of_experience or 0

#         # ==== JOBS ====
#         job_results = []
#         for job in payload.job_posts:
#             job_text = advanced_preprocess(f"{job.title} {' '.join(job.skills or [])} {job.job_description}")
#             job_vector = np.array(bert_model.encode(job_text))
#             similarity = cosine_similarity([cv_vector], [job_vector])[0][0]
#             similarity = max(0.0, min(1.0, similarity))

#             job_min_exp, _ = parse_experience(job.job_description or "")
#             experience_score = calculate_experience_score(dev_exp, job_min_exp)

#             skill_score = skill_score_calculator(cv_tokens, job.skills or [])
#             final_score = (0.5 * similarity) + (0.3 * experience_score) + (0.2 * skill_score)

#             job_results.append(ScoredItem(
#                 id=job.id,
#                 final_score=round(final_score, 4),
#                 similarity_score=round(similarity, 4),
#                 experience_score=round(experience_score, 4),
#                 skill_score=round(skill_score, 4)
#             ))

#         job_results = [j for j in job_results if j.final_score >= 0.4]
#         job_results.sort(key=lambda x: x.final_score, reverse=True)

#         # ==== SERVICES ====
#         service_results = []
#         for sp in payload.service_posts:
#             sp_text = advanced_preprocess(f"{sp.title} {sp.description} {' '.join(sp.required_skills or [])}")
#             sp_vector = np.array(bert_model.encode(sp_text))
#             similarity = cosine_similarity([cv_vector], [sp_vector])[0][0]
#             similarity = max(0.0, min(1.0, similarity))

#             skill_score = skill_score_calculator(cv_tokens, sp.required_skills or [])
#             final_score = (0.5 * similarity) + (0.5 * skill_score)

#             service_results.append(ScoredItem(
#                 id=sp.id,
#                 final_score=round(final_score, 4),
#                 similarity_score=round(similarity, 4),
#                 skill_score=round(skill_score, 4)
#             ))

#         service_results = [s for s in service_results if s.final_score >= 0.4]
#         service_results.sort(key=lambda x: x.final_score, reverse=True)

#         return RecommendationResponse(
#             job_recommendations=job_results,
#             service_recommendations=service_results
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")



