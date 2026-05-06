from .BaseModelClean import BaseModelClean as BaseModel
from .Validators import Between10, Percentage

from enum import StrEnum
from pydantic import ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

# ! Note that the below class has been extended when compared to the original schema
class ActorType(StrEnum):
    country = "country"
    government = "government"
    political_party = "political party"

    company = "company"
    news_outlet = "news outlet"

    politician = "politician"
    celebrity = "celebrity"
    ceo = "ceo"
    other = "other"

class Actor(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    name: str = Field(frozen=True)
    actor_type: ActorType = Field(frozen=True)

    # TODO The below fields and method should likely be deleted, as they are not being used
    # Fields to be filled in later
    #impact: Between10 | None = None
    #public_opinion: Between10 | None = None
    #controversy: Between10 | None = None
    #mentions_weight: Percentage | None = None
    # TODO should be restricted to only themes found
    #linked_themes: str | None = None

    '''
    # TODO may need breaking up into different methods for filling in at different times
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
    '''