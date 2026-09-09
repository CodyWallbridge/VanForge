from pydantic import BaseModel, model_validator

class UpdateRequest(BaseModel):
    @model_validator(mode="after")
    def reject_explicit_nulls(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null; omit it to leave it unchanged")
            
        return self
