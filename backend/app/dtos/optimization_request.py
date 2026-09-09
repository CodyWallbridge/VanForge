from pydantic import BaseModel, Field, model_validator

class OptimizationRequest(BaseModel):
    character_ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_character_ids(self):
        if len(self.character_ids) != len(set(self.character_ids)):
            raise ValueError("Select each character only once")

        return self
