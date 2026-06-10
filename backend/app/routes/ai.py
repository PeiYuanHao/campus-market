from fastapi import APIRouter

from app.schemas.common import AIGenerateRequest, AIGenerateResponse
from app.services.ai_helper import build_description


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/generate-description", response_model=AIGenerateResponse)
def generate_description(payload: AIGenerateRequest):
    return build_description(payload)
