from typing import List, Optional
from pydantic import BaseModel, Field
from backend.models.memory import MemoryResponse

class MemeCritique(BaseModel):
    meme_url: str
    verdict: str
    critique: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    source_platform: Optional[str] = None
    query_used: Optional[str] = None
    situation: Optional[str] = None
    meme_file: Optional[str] = None

class JournalEntryBase(BaseModel):
    title: Optional[str] = None
    content: str
    module_id: Optional[str] = None

class JournalEntryCreate(JournalEntryBase):
    id: Optional[str] = None
    created_at: Optional[str] = None

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    module_id: Optional[str] = None

class JournalEntryResponse(JournalEntryBase):
    id: str
    created_at: str
    updated_at: str
    suggested_memories: List[MemoryResponse] = Field(default_factory=list)
    related_memories: List[MemoryResponse] = Field(default_factory=list)
    critique: Optional[MemeCritique] = None
