from typing import Optional
from pydantic import BaseModel
from backend.models.memory import ImportanceLevel

class FutureSelfBase(BaseModel):
    message: str
    related_person: Optional[str] = None
    related_topic: Optional[str] = None
    importance: ImportanceLevel = ImportanceLevel.MED
    trigger_context: str
    expires_at: Optional[str] = None

class FutureSelfCreate(FutureSelfBase):
    id: Optional[str] = None
    created_at: Optional[str] = None

class FutureSelfResponse(FutureSelfBase):
    id: str
    created_at: str
    triggered_at: Optional[str] = None
    dismissed: bool = False
