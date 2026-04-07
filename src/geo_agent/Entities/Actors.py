from .Validators import Between10, Percentage

from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

class ActorType(StrEnum):
    country = "country"
    company = "company"
    politician = "politician"
    celebrity = "celebrity"
    other = "other"

class Actor(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    name: str = Field(frozen=True)
    actor_type: ActorType = Field(frozen=True)

    # Fields to be filled in later
    impact: Between10 | None = None
    public_opinion: Between10 | None = None
    controversy: Between10 | None = None
    mentions_weight: Percentage | None = None
    # XX should be restricted to only themes found
    linked_themes: str | None = None

    # XX may need breaking up into different methods for filling in at different times
    def set_processed_values(self, 
                            impact: float, 
                            public_opinion: float,
                            controversy: float,
                            mentions_weight: float,
                            linked_themes: str) -> None:
        self.impact = impact
        self.public_opinion = public_opinion
        self.controversy = controversy
        self.mentions_weight = mentions_weight
        self.linked_themes = linked_themes