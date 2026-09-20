import type { RecipeIngredientInput } from "./RecipeCreate";

export interface RecipeUpdate {
    name?: string;
    profit_per_craft?: number;
    profession_id?: number;
    expansion_id?: number;
    ingredients?: RecipeIngredientInput[];
}
