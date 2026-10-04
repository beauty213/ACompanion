from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    EXPERIENCE = "Experience"
    REFLECTION = "Reflection"
    BOUNDARY = "Boundary"
    GOAL = "Goal"
    COMMITMENT = "Commitment"
    EVENT = "Event"
    VALUE = "Value"
    PATTERN = "Pattern"
    PERSON = "Person"
    FUTURE_SELF_MESSAGE = "FutureSelfMessage"

class MemoryStatus(str, Enum):
    AI_SUGGESTED = "ai_suggested"
    USER_CONFIRMED = "user_confirmed"
    USER_EDITED = "user_edited"

class ImportanceLevel(str, Enum):
    LOW = "low"
    MED = "med"
    HIGH = "high"

class MemoryBase(BaseModel):
    type: MemoryType
    title: Optional[str] = None
    content: str
    summary: Optional[str] = None
    related_people: List[str] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    emotion: Optional[str] = None
    importance: ImportanceLevel = ImportanceLevel.MED
    confidence: float = 1.0
    status: MemoryStatus = MemoryStatus.USER_CONFIRMED
    source_journal_id: Optional[str] = None
    source_conversation_id: Optional[str] = None
    module_id: Optional[str] = None

class MemoryCreate(MemoryBase):
    id: Optional[str] = None

class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    type: Optional[MemoryType] = None
    related_people: Optional[List[str]] = None
    related_topics: Optional[List[str]] = None
    emotion: Optional[str] = None
    importance: Optional[ImportanceLevel] = None
    status: Optional[MemoryStatus] = None
    module_id: Optional[str] = None

class MemorySource(BaseModel):
    id: str
    memory_id: str
    source_type: str  # "journal", "chat"
    source_id: str
    excerpt: Optional[str] = None
    created_at: str

class MemoryResponse(MemoryBase):
    id: str
    created_at: str
    updated_at: str
    confirmed_at: Optional[str] = None
    sources: List[MemorySource] = Field(default_factory=list)

class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.3
    include_suggested: bool = False
    filter_type: Optional[MemoryType] = None
