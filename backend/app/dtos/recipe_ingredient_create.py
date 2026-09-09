from pydantic import BaseModel, Field, model_validator

class RecipeIngredientCreate(BaseModel):
    ingredient_id: int | None = None
    name: str | None = Field(default=None, min_length=1)
    amount_required: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_ingredient_reference(self):
        if (self.ingredient_id is None) == (self.name is None):
            raise ValueError("Provide either ingredient_id or name, but not both")
        
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Ingredient name cannot be blank")
            
        return self
