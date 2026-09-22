from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, UniqueConstraint

class Expansion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    recipes: List["Recipe"] = Relationship(back_populates="expansion")

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    auth_user_id: str = Field(unique=True, index=True)
    email: Optional[str] = None
    role: str = Field(default="user")

    characters: List["Character"] = Relationship(back_populates="account", sa_relationship_kwargs={"passive_deletes": "all"})
    settings: Optional["AppSettings"] = Relationship(back_populates="account", sa_relationship_kwargs={"passive_deletes": "all"})
    recipe_profits: List["RecipeProfit"] = Relationship(back_populates="account", sa_relationship_kwargs={"passive_deletes": "all"})

class DeletedAuthUser(SQLModel, table=True):
    auth_user_id: str = Field(primary_key=True)
    deleted_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

class AppSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id", unique=True, ondelete="CASCADE")
    current_expansion_id: int = Field(foreign_key="expansion.id")

    account: Optional[Account] = Relationship(back_populates="settings")
    current_expansion: Optional[Expansion] = Relationship()

class Profession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    recipes: List["Recipe"] = Relationship(back_populates="profession")

class CharacterRecipe(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("character_id", "recipe_id", name="uq_characterrecipe_character_recipe"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    character_id: int = Field(foreign_key="character.id", ondelete="CASCADE")
    recipe_id: int = Field(foreign_key="recipe.id", ondelete="CASCADE")

    concentration_cost: int

    character: Optional["Character"] = Relationship(back_populates="recipes")
    recipe: Optional["Recipe"] = Relationship(back_populates="characters")

class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id", ondelete="CASCADE")
    name: str

    profession1_id: int = Field(foreign_key="profession.id")
    profession2_id: int = Field(foreign_key="profession.id")

    concentration: int = 1000

    account: Optional[Account] = Relationship(back_populates="characters")
    recipes: List[CharacterRecipe] = Relationship(back_populates="character", sa_relationship_kwargs={"passive_deletes": "all"})

class RecipeProfit(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("account_id", "recipe_id", name="uq_recipeprofit_account_recipe"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id", ondelete="CASCADE")
    recipe_id: int = Field(foreign_key="recipe.id", ondelete="CASCADE")
    profit_per_craft: int = 0

    account: Optional[Account] = Relationship(back_populates="recipe_profits")
    recipe: Optional["Recipe"] = Relationship(back_populates="profits")

class RecipeIngredient(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipeingredient_recipe_ingredient"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", ondelete="CASCADE")
    ingredient_id: int = Field(foreign_key="ingredient.id")

    amount_required: int

    recipe: Optional["Recipe"] = Relationship(back_populates="ingredients")
    ingredient: Optional["Ingredient"] = Relationship(back_populates="recipes")

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    profession_id: int = Field(foreign_key="profession.id")
    expansion_id: int = Field(foreign_key="expansion.id")

    expansion: Optional[Expansion] = Relationship(back_populates="recipes")
    profession: Optional[Profession] = Relationship(back_populates="recipes")

    ingredients: List[RecipeIngredient] = Relationship(back_populates="recipe", sa_relationship_kwargs={"passive_deletes": "all"})
    characters: List[CharacterRecipe] = Relationship(back_populates="recipe", sa_relationship_kwargs={"passive_deletes": "all"})
    profits: List[RecipeProfit] = Relationship(back_populates="recipe", sa_relationship_kwargs={"passive_deletes": "all"})

class Ingredient(SQLModel, table=True):
    id: Optional[int]  = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    recipes: List[RecipeIngredient] = Relationship(back_populates="ingredient")
