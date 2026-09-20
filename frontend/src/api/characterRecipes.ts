import type { CharacterRecipeCreate } from "../dto/CharacterRecipeCreate";
import type { CharacterRecipeRead } from "../dto/CharacterRecipeRead";
import { request } from "./request";

export async function getCharacterRecipes(characterId: number): Promise<CharacterRecipeRead[]> {
    const assignments = await request<CharacterRecipeRead[]>(`/characters/${characterId}/recipes`);

    if (assignments === undefined) {
        throw new Error("The server returned no character recipes.");
    }

    return assignments;
}

export async function assignCharacterRecipe(
    characterId: number,
    assignment: CharacterRecipeCreate,
): Promise<CharacterRecipeRead> {
    const created = await request<CharacterRecipeRead>(`/characters/${characterId}/recipes`, {
        method: "POST",
        body: JSON.stringify(assignment),
    });

    if (created === undefined) {
        throw new Error("The server returned no character recipe.");
    }

    return created;
}

export async function updateCharacterRecipe(
    characterId: number,
    recipeId: number,
    concentrationCost: number,
): Promise<CharacterRecipeRead> {
    const updated = await request<CharacterRecipeRead>(`/characters/${characterId}/recipes/${recipeId}`, {
        method: "PATCH",
        body: JSON.stringify({ concentration_cost: concentrationCost }),
    });

    if (updated === undefined) {
        throw new Error("The server returned no updated character recipe.");
    }

    return updated;
}

export async function removeCharacterRecipe(characterId: number, recipeId: number): Promise<void> {
    await request<void>(`/characters/${characterId}/recipes/${recipeId}`, {
        method: "DELETE",
    });
}
