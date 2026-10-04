from typing import List, Optional
from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    sender: str  # "user" | "assistant"
    content: str
    citations: List[str] = Field(default_factory=list)

class MessageCreate(BaseModel):
    content: str
    conversation_id: Optional[str] = None

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: str

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: str
    updated_at: str
    messages: List[MessageResponse] = Field(default_factory=list)
