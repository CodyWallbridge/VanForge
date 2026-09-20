export interface RecipeIngredientInput {
    name: string;
    amount_required: number;
}

export interface RecipeCreate {
    name: string;
    profit_per_craft: number;
    profession_id: number;
    expansion_id: number;
    ingredients: RecipeIngredientInput[];
}
