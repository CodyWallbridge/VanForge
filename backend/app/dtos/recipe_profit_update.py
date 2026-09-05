from sqlmodel import SQLModel

class RecipeProfitUpdate(SQLModel):
    profit_per_craft: int