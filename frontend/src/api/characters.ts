import type { CharacterRead } from "../dto/CharacterRead";
import type { CharacterCreate } from "../dto/CharacterCreate";
import type { CharacterUpdate } from "../dto/CharacterUpdate";
import { request } from "./request";

export async function getCharacters(): Promise<CharacterRead[]> {
    const characters = await request<CharacterRead[]>("/characters/");

    if (characters === undefined) {
        throw new Error("The server returned no character list.");
    }

    return characters;
}

export async function getCharacter(characterId: number): Promise<CharacterRead> {
    const character = await request<CharacterRead>(`/characters/${characterId}`);

    if (character === undefined) {
        throw new Error("The server returned no character.");
    }

    return character;
}

export async function createCharacter(
    character: CharacterCreate,
): Promise<CharacterRead> {
    const created = await request<CharacterRead>("/characters/", {
        method: "POST",
        body: JSON.stringify(character),
    });

    if (created === undefined) {
        throw new Error("The server returned no character.");
    }

    return created;
}

export async function deleteCharacter(characterId: number): Promise<void> {
    await request<void>(`/characters/${characterId}`, {
        method: "DELETE",
    });
}

export async function updateCharacter(
    characterId: number,
    changes: CharacterUpdate,
): Promise<CharacterRead> {
    const updated = await request<CharacterRead>(`/characters/${characterId}`, {
        method: "PATCH",
        body: JSON.stringify(changes),
    });

    if (updated === undefined) {
        throw new Error("The server returned no updated character.");
    }

    return updated;
}
