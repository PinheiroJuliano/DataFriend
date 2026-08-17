from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    raise HTTPException(status_code=501, detail="Chat endpoint not implemented yet. Will be implemented in Phase 6.")
