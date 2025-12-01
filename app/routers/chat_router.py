from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import generate_reply

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/reply")
async def chat_reply(payload: ChatRequest):
    response = generate_reply(
        user_id=payload.user_id,
        message=payload.message
    )
    return response
