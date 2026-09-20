import type { ProfessionOptimizationRead } from "./ProfessionOptimizationRead";

export interface CharacterOptimizationRead {
    character_id: number;
    character_name: string;
    profit: number;
    professions: ProfessionOptimizationRead[];
}
