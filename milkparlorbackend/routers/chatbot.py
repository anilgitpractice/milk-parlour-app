from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()


class ChatRequest(BaseModel):
    customer_id: Optional[int] = Field(default=None)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str


@router.post("/query", response_model=ChatResponse)
async def chat_with_ai(payload: ChatRequest):
    # In the future, call a real LLM with the customer's query.
    reply_text = (
        "Thanks for your question about milk subscriptions. "
        "This is a mock AI response; the real assistant will be connected soon."
    )
    return ChatResponse(reply=reply_text)

