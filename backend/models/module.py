from typing import Optional
from pydantic import BaseModel

class ModuleBase(BaseModel):
    name: str
    alias: Optional[str] = None
    relationship: Optional[str] = None
    description: Optional[str] = None

class ModuleCreate(ModuleBase):
    id: Optional[str] = None

class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    relationship: Optional[str] = None
    description: Optional[str] = None

class Module(ModuleBase):
    id: str
    created_at: str
    updated_at: str

class ModuleWithStats(Module):
    incident_count: int = 0
    latest_incident_date: Optional[str] = None
    active_boundaries_count: int = 0
