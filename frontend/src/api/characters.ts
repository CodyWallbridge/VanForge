import type { CharacterRead } from "../dto/CharacterRead";
import { request } from "./request";

export async function getCharacters(): Promise<CharacterRead[]> {
    const characters = await request<CharacterRead[]>("/characters/");

    if (characters === undefined) {
        throw new Error("The server returned no character list.");
    }

    return characters;
}