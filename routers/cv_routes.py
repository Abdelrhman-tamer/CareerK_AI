# routers/cv_routes.py
from fastapi import APIRouter, HTTPException, Response
from models.cv_models import CVData, ChatToCVRequest
from services.pdf_generator import generate_pdf
from services.chat_to_cv import process_message
from services.ai_summary import generate_professional_summary

router = APIRouter()


@router.post("/generate")
def generate_cv(data: CVData):
    try:
        # Convert to dict
        cv_dict = data.dict()

        # 🔹 Inject AI-generated summary
        summary = generate_professional_summary(cv_dict)
        cv_dict["personal_info"]["summary"] = summary

        # 🔹 Generate PDF
        pdf_content = generate_pdf(cv_dict)

        return Response(content=pdf_content, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-to-cv")
def chat_to_cv(request: ChatToCVRequest):
    try:
        return process_message(session_id=request.session_id, message=request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))









# from fastapi import APIRouter, HTTPException, Response
# from models.cv_models import CVData, ChatToCVRequest
# from services.pdf_generator import generate_pdf
# from services.chat_to_cv import process_message

# router = APIRouter()

# @router.post("/generate")
# def generate_cv(data: CVData):
#     try:
#         pdf_content = generate_pdf(data.dict())
#         return Response(content=pdf_content, media_type="application/pdf")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/chat-to-cv")
# def chat_to_cv(request: ChatToCVRequest):
#     try:
#         return process_message(session_id=request.session_id, message=request.message)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
