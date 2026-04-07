from .Validators import Between10p

from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

class _Severity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"

class _Impact(BaseModel):
    severity: _Severity
    justification: str

class Event(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    event: str = Field(frozen=True)

    # Fields to be filled in later
    controversy: Between10p | None = None
    economic_impact: _Impact | None = None
    financial_market_impact: _Impact | None = None
    security_impact: _Impact | None = None
    diplomatic_impact: _Impact | None = None

    def set_processed_values(self,
                             controversy: float,
                             e_sev: str, e_just: str,
                             f_sev: str, f_just: str,
                             s_sev: str, s_just: str,
                             d_sev: str, d_just: str) -> None:
        self.controversy = controversy
        self.economic_impact = _Impact(severity=_Severity(e_sev), justification=e_just)
        self.financial_market_impact = _Impact(severity=_Severity(f_sev), justification=f_just)
        self.security_impact = _Impact(severity=_Severity(s_sev), justification=s_just)
        self.diplomatic_impact = _Impact(severity=_Severity(d_sev), justification=d_just)