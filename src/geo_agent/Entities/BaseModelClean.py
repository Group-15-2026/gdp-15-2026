from pydantic import BaseModel

# This class aims to reduce unnecessary content in the JSON serialisation of incomplete objects, in order to avoid confusing the orchestrator LLM
class BaseModelClean(BaseModel):
    def model_dump(self, **kwargs):
        return super().model_dump(exclude_none=True, **kwargs)
    
    def model_dump_json(self, **kwargs):
        return super().model_dump_json(exclude_none=True, **kwargs)