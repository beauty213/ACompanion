from typing import List
from pydantic import BaseModel, Field

class PatternBase(BaseModel):
    title: str
    description: str
    memory_ids: List[str] = Field(default_factory=list)

class PatternResponse(PatternBase):
    id: str
    dismissed: bool = False
    created_at: str

class PatternDetectResponse(BaseModel):
    detected: bool
    patterns: List[PatternResponse] = Field(default_factory=list)
    message: str
