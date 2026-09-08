from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Expansion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    recipes: List["Recipe"] = Relationship(back_populates="expansion")

class AppSettings(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    current_expansion_id: int = Field(foreign_key="expansion.id")

    current_expansion: Optional[Expansion] = Relationship()

class Profession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    recipes: List["Recipe"] = Relationship(back_populates="profession")

class CharacterRecipe(SQLModel, table=True):
    character_id: int = Field(foreign_key="character.id", primary_key=True, ondelete="CASCADE")
    recipe_id: int = Field(foreign_key="recipe.id", primary_key=True, ondelete="CASCADE")

    concentration_cost: int

    character: Optional["Character"] = Relationship(back_populates="recipes")
    recipe: Optional["Recipe"] = Relationship(back_populates="characters")

class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    profession1_id: int = Field(foreign_key="profession.id")
    profession2_id: int = Field(foreign_key="profession.id")

    concentration: int = 1000

    recipes: List[CharacterRecipe] = Relationship(
        back_populates="character",
        sa_relationship_kwargs={"passive_deletes": "all"},
    )

class RecipeIngredient(SQLModel, table=True):
    recipe_id: int = Field(foreign_key="recipe.id", primary_key=True, ondelete="CASCADE")
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)

    amount_required: int

    recipe: Optional["Recipe"] = Relationship(back_populates="ingredients")
    ingredient: Optional["Ingredient"] = Relationship(back_populates="recipes")

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    profit_per_craft: int = 0

    profession_id: int = Field(foreign_key="profession.id")
    expansion_id: int = Field(foreign_key="expansion.id")

    expansion: Optional[Expansion] = Relationship(back_populates="recipes")
    profession: Optional[Profession] = Relationship(back_populates="recipes")

    ingredients: List[RecipeIngredient] = Relationship(
        back_populates="recipe",
        sa_relationship_kwargs={"passive_deletes": "all"},
    )
    characters: List[CharacterRecipe] = Relationship(
        back_populates="recipe",
        sa_relationship_kwargs={"passive_deletes": "all"},
    )

class Ingredient(SQLModel, table=True):
    id: Optional[int]  = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    recipes: List[RecipeIngredient] = Relationship(back_populates="ingredient")