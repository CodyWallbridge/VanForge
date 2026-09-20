import type { CharacterOptimizationRead } from "./CharacterOptimizationRead";
import type { CharacterPlanItem } from "./CharacterPlanItem";

export interface OptimizationRead {
    expansion_id: number;
    total_profit: number;
    crafts: CharacterPlanItem[];
    characters: CharacterOptimizationRead[];
}
