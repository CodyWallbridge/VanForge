import type { IngredientRead } from "./IngredientRead";

export interface RecipeRead {
    id: number;
    name: string;
    profit_per_craft: number;
    profession_id: number;
    expansion_id: number;
    ingredients: RecipeIngredientRead[];
}

export interface RecipeIngredientRead {
    amount_required: number;
    ingredient: IngredientRead;
}
