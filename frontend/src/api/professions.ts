import type { ProfessionRead } from "../dto/ProfessionRead";
import { request } from "./request";

export async function getProfessions(): Promise<ProfessionRead[]> {
    const professions = await request<ProfessionRead[]>("/professions/");

    if (professions === undefined) {
        throw new Error("The server returned no profession list.");
    }

    return professions;
}