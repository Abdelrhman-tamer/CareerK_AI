from fastapi import APIRouter, HTTPException
from services.course_recommender import get_course_recommendations

router = APIRouter()

@router.get("/recommendations/{developer_id}")
async def recommend_courses(developer_id: str):
    try:
        recommendations = await get_course_recommendations(developer_id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
