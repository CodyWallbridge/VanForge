from sqlmodel import Session, select
from ..models import RecipeProfit
from .base import CRUDBase

class RecipeProfitCRUD(CRUDBase[RecipeProfit]):
    def get_by_account_recipe(
        self,
        session: Session,
        account_id: int,
        recipe_id: int,
    ):
        return session.exec(
            select(RecipeProfit).where(
                RecipeProfit.account_id == account_id,
                RecipeProfit.recipe_id == recipe_id,
            ),
        ).first()

    def get_for_recipes(
        self,
        session: Session,
        account_id: int,
        recipe_ids: list[int],
    ):
        if not recipe_ids:
            return []

        return session.exec(
            select(RecipeProfit).where(
                RecipeProfit.account_id == account_id,
                RecipeProfit.recipe_id.in_(recipe_ids),
            ),
        ).all()

recipe_profits = RecipeProfitCRUD(RecipeProfit)
