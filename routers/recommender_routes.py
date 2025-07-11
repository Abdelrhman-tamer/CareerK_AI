from fastapi import APIRouter, HTTPException
from models.recommender_models import RecommendationRequest, RecommendationResponse
from services.recommender import recommend_for_developer
import logging
import traceback

logger = logging.getLogger("CareerK-Recommender")
router = APIRouter()

@router.post("", response_model=RecommendationResponse)
def recommend(data: RecommendationRequest):
    try:
        logger.info(f"Received request for developer ID: {data.developer.id}")
        logger.info(f"{len(data.job_posts)} job posts | {len(data.service_posts)} service posts")

        result = recommend_for_developer(
            developer=data.developer.dict(),
            job_posts=[job.dict() for job in data.job_posts],
            service_posts=[srv.dict() for srv in data.service_posts]
        )
        return result
    except Exception as e:
        logger.error("🔥 Recommendation failed!")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")




# from fastapi import APIRouter, HTTPException
# from models.recommender_models import RecommendationRequest, RecommendationResponse
# from services.recommender import recommend_for_developer
# import logging
# import traceback

# logger = logging.getLogger("CareerK-Recommender")
# router = APIRouter()

# @router.post("", response_model=RecommendationResponse)
# def recommend(data: RecommendationRequest):
#     try:
#         logger.info(f"Received request for developer ID: {data.developer.id}")
#         logger.info(f"{len(data.job_posts)} job posts | {len(data.service_posts)} service posts")

#         result = recommend_for_developer(
#             developer=data.developer.dict(),
#             job_posts=[job.dict() for job in data.job_posts],
#             service_posts=[srv.dict() for srv in data.service_posts]
#         )
#         return result
#     except Exception as e:
#         logger.error("🔥 Recommendation failed!")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
