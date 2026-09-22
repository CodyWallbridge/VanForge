from sqlmodel import Session
from ..backend_models.recipe_profit import recipe_profits
from ..models import RecipeProfit
from .base import BaseService

class RecipeProfitService(BaseService):
    model_class = RecipeProfit
    data_accessor = recipe_profits

    def get_value(
        self,
        session: Session,
        account_id: int,
        recipe_id: int,
    ) -> int:
        profit = self.data_accessor.get_by_account_recipe(
            session,
            account_id,
            recipe_id,
        )

        return profit.profit_per_craft if profit else 0

    def get_values(
        self,
        session: Session,
        account_id: int,
        recipe_ids: list[int],
    ) -> dict[int, int]:
        profits = self.data_accessor.get_for_recipes(
            session,
            account_id,
            recipe_ids,
        )

        return {profit.recipe_id: profit.profit_per_craft for profit in profits}

    def set_value(
        self,
        session: Session,
        account_id: int,
        recipe_id: int,
        profit_per_craft: int,
    ):
        profit = self.data_accessor.get_by_account_recipe(
            session,
            account_id,
            recipe_id,
        )

        if profit is None:
            profit = RecipeProfit(
                account_id=account_id,
                recipe_id=recipe_id,
                profit_per_craft=profit_per_craft,
            )

            return self.create(entity=profit, session=session)

        profit.profit_per_craft = profit_per_craft

        return self.update(entity=profit, session=session)
