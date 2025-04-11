from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    summary: str
    ai_tags: dict = Field(..., description="Counts of OASMNR and SASBA submissions")
