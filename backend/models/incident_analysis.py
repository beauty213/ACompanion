from typing import List, Optional
from pydantic import BaseModel, Field

class IncidentAnalysisReport(BaseModel):
    module_id: str
    module_name: str
    relationship: Optional[str] = None
    incident_count: int = 0
    timeline_summary: str
    escalation_analysis: str
    documented_contradictions: List[str] = Field(default_factory=list)
    reciprocity_assessment: str
    active_boundaries: List[str] = Field(default_factory=list)
    clarifying_questions: List[str] = Field(default_factory=list)
    key_takeaway: str
    generated_at: str
