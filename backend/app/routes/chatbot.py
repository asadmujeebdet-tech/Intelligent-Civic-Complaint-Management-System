from fastapi import APIRouter, HTTPException

from backend.app.models.complaint import ChatRequest, ChatResponse
from backend.app.services.chatbot_service import ChatbotService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """AI analytics chatbot for managers."""
    try:
        answer = ChatbotService.chat_with_complaints(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
