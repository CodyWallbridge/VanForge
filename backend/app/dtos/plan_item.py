from sqlmodel import SQLModel

class PlanItem(SQLModel):
    recipe_id: int
    crafts: int
