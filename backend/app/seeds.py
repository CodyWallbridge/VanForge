from sqlmodel import Session, select
from .database import engine
from .models import AppSettings, Character, Expansion, Ingredient, Profession, Recipe, RecipeIngredient

PROFESSIONS = [
    "Alchemy",
    "Blacksmithing",
    "Enchanting",
    "Engineering",
    "Inscription",
    "Jewelcrafting",
    "Leatherworking",
    "Tailoring",
]

CHARACTERS = [
    ("Vandredor", "Alchemy", "Enchanting"),
    ("Vanakin", "Alchemy", "Tailoring"),
    ("Vandeador", "Alchemy", "Tailoring"),
    ("Vanjinx", "Alchemy", "Tailoring"),
    ("Vanchii", "Leatherworking", "Tailoring"),
    ("Vanrage", "Blacksmithing", "Inscription"),
    ("Vantommenace", "Blacksmithing", "Jewelcrafting"),
    ("Vanethos", "Alchemy", "Tailoring"),
    ("Vandroid", "Alchemy", "Tailoring"),
    ("Vanhellsing", "Alchemy", "Tailoring"),
    ("Vango", "Alchemy", "Tailoring"),
    ("Vanhailen", "Alchemy", "Tailoring"),
    ("Miniivan", "Alchemy", "Tailoring"),
    ("Vanishing", "Alchemy", "Tailoring"),
    ("Windowlesvan", "Alchemy", "Tailoring"),
    ("Vancleavee", "Alchemy", "Inscription"),
    ("Vansurge", "Alchemy", "Inscription"),
    ("Vantastic", "Alchemy", "Inscription"),
    ("Vanlock", "Alchemy", "Enchanting"),
    ("Vanomaly", "Alchemy", "Enchanting"),
    ("Vandreador", "Alchemy", "Enchanting"),
    ("Vanwick", "Alchemy", "Enchanting"),
    ("Vantidote", "Alchemy", "Enchanting"),
    ("Vannoying", "Alchemy", "Enchanting"),
    ("Vandemonium", "Alchemy", "Blacksmithing"),
    ("Vandalorian", "Alchemy", "Blacksmithing"),
    ("Vangobrr", "Alchemy", "Blacksmithing"),
    ("Venlemix", "Alchemy", "Blacksmithing"),
]

MIDNIGHT_RECIPES = [
    ("Flask of Blood Knights", "Alchemy", {
        "Nocturnal Lotus": 1,
        "Mote of Wild Magic": 2,
        "Argentleaf": 8,
        "Sanguithorn": 6,
    }),
    ("Flask of the Magisters", "Alchemy", {
        "Nocturnal Lotus": 1,
        "Mote of Pure Void": 2,
        "Sanguithorn": 8,
        "Mana Lily": 6,
    }),
    ("Flask of the Shattered Sun", "Alchemy", {
        "Nocturnal Lotus": 1,
        "Mote of Primal Energy": 2,
        "Azeroot": 8,
        "Argentleaf": 6,
    }),
    ("Sterling Alloy", "Blacksmithing", {
        "Brilliant Silver Ore": 6,
        "Refulgent Copper Ingot": 3,
    }),
    ("Gloaming Alloy", "Blacksmithing", {
        "Umbral Tin Ore": 6,
        "Refulgent Copper Ingot": 3,
    }),
    ("Potion of Recklessness", "Alchemy", {
        "Mote of Primal Energy": 2,
        "Tranquility Bloom": 8,
        "Azeroot": 4,
    }),
    ("Potion of Light's Potential", "Alchemy", {
        "Mote of Light": 1,
        "Tranquility Bloom": 8,
        "Argentleaf": 3,
        "Azeroot": 3,
    }),
    ("Sunglass Vials", "Jewelcrafting", {
        "Crystalline Glass": 5,
        "Duskshrouded Stone": 1,
    }),
]

def seed_professions():
    print("Seeding professions...")  
    with Session(engine) as session:

        for name in PROFESSIONS:
            statement = select(Profession).where(Profession.name == name)
            existing = session.exec(statement).first()

            if not existing:
                session.add(
                    Profession(name=name),
                )

        session.commit()
    print("Seeding complete")

def seed_characters():
    with Session(engine) as session:
        professions = session.exec(
            select(Profession),
        ).all()
        profession_ids = {profession.name: profession.id for profession in professions}

        characters = session.exec(
            select(Character),
        ).all()
        existing_names = {character.name.casefold() for character in characters}

        for name, profession1, profession2 in CHARACTERS:
            if name.casefold() in existing_names:
                continue

            character = Character(
                name=name,
                profession1_id=profession_ids[profession1],
                profession2_id=profession_ids[profession2],
                concentration=1000,
            )
            session.add(character)
            existing_names.add(
                name.casefold(),
            )

        session.commit()

def seed_recipes():
    with Session(engine) as session:
        expansion = session.exec(
            select(Expansion).where(Expansion.name == "Midnight"),
        ).one()

        professions = session.exec(
            select(Profession),
        ).all()
        profession_ids = {profession.name: profession.id for profession in professions}

        ingredients = session.exec(
            select(Ingredient),
        ).all()
        ingredients_by_name = {ingredient.name.casefold(): ingredient for ingredient in ingredients}

        for name, profession_name, materials in MIDNIGHT_RECIPES:
            profession_id = profession_ids[profession_name]
            recipe = session.exec(
                select(Recipe).where(
                    Recipe.name == name,
                    Recipe.expansion_id == expansion.id,
                    Recipe.profession_id == profession_id,
                ),
            ).first()

            if recipe is None:
                recipe = Recipe(
                    name=name,
                    profession_id=profession_id,
                    expansion_id=expansion.id,
                    profit_per_craft=0,
                )
                session.add(recipe)
                session.flush()

            for ingredient_name, amount in materials.items():
                ingredient = ingredients_by_name.get(
                    ingredient_name.casefold(),
                )

                if ingredient is None:
                    ingredient = Ingredient(name=ingredient_name)
                    session.add(ingredient)
                    session.flush()
                    ingredients_by_name[ingredient_name.casefold()] = ingredient

                recipe_ingredient = session.exec(
                    select(RecipeIngredient).where(
                        RecipeIngredient.recipe_id == recipe.id,
                        RecipeIngredient.ingredient_id == ingredient.id,
                    ),
                ).first()

                if recipe_ingredient is None:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        amount_required=amount,
                    )
                    session.add(recipe_ingredient)

        session.commit()
        
def seed_initial_data():
    """Explicitly load starter data; never called during normal application startup."""
    seed_professions()
    with Session(engine) as session:
        expansion = session.exec(
            select(Expansion).where(Expansion.name == "Midnight"),
        ).first()
        if expansion is None:
            expansion = Expansion(name="Midnight")
            session.add(expansion)
            session.flush()
        if session.get(AppSettings, 1) is None:
            settings = AppSettings(id=1, current_expansion_id=expansion.id)
            session.add(settings)
        session.commit()
    seed_characters()
    seed_recipes()

if __name__ == "__main__":
    seed_initial_data()
