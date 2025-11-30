from fastapi import APIRouter
from pydantic import BaseModel
from app.services.emotion_service import analyze_emotion

router = APIRouter(prefix="/emotion", tags=["Emotion Analysis"])

class EmotionRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze_emotion_route(payload: EmotionRequest):
    result = analyze_emotion(payload.text)
    return result
