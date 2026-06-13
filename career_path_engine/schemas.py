from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    cv_text: str
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education_level: Optional[str] = None
    target_role: str
    target_industry: Optional[str] = None
    location: Optional[str] = None
    remote_ok: bool = True
    relocation: Optional[str] = None
    budget_eur: Optional[float] = None
    hours_per_week: Optional[int] = None
    psychometric_profile: Dict[str, float] = Field(default_factory=dict)


class CareerPathOutput(BaseModel):
    primary_role: str
    role_match_score: float = Field(ge=0.0, le=1.0)
    fit_breakdown: Dict[str, float] = Field(default_factory=dict)
    gaps: List[str] = Field(default_factory=list)
    roadmap_3m: List[str] = Field(default_factory=list)
    roadmap_6m: List[str] = Field(default_factory=list)
    roadmap_12m: List[str] = Field(default_factory=list)
    recommended_resources: List[str] = Field(default_factory=list)
    interview_prep_topics: List[str] = Field(default_factory=list)
