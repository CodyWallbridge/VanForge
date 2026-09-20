import type { RecipeCreate } from "../dto/RecipeCreate";
import type { RecipeRead } from "../dto/RecipeRead";
import type { RecipeUpdate } from "../dto/RecipeUpdate";
import { request } from "./request";

export async function getRecipes(): Promise<RecipeRead[]> {
    const recipes = await request<RecipeRead[]>("/recipes/");

    if (recipes === undefined) {
        throw new Error("The server returned no recipe list.");
    }

    return recipes;
}

export async function createRecipe(recipe: RecipeCreate): Promise<RecipeRead> {
    const created = await request<RecipeRead>("/recipes/", {
        method: "POST",
        body: JSON.stringify(recipe),
    });

    if (created === undefined) {
        throw new Error("The server returned no recipe.");
    }

    return created;
}

export async function updateRecipe(
    recipeId: number,
    changes: RecipeUpdate,
): Promise<RecipeRead> {
    const updated = await request<RecipeRead>(`/recipes/${recipeId}`, {
        method: "PATCH",
        body: JSON.stringify(changes),
    });

    if (updated === undefined) {
        throw new Error("The server returned no updated recipe.");
    }

    return updated;
}

export async function deleteRecipe(recipeId: number): Promise<void> {
    await request<void>(`/recipes/${recipeId}`, {
        method: "DELETE",
    });
}
