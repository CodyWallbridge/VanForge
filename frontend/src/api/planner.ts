import type { CharacterPlanItem } from "../dto/CharacterPlanItem";
import type { OptimizationRead } from "../dto/OptimizationRead";
import type { PlannerOption } from "../dto/PlannerOption";
import type { OptimizationRequest } from "../dto/OptimizationRequest";
import { request } from "./request";

export async function optimizePlan(selection: OptimizationRequest): Promise<OptimizationRead> {
    const result = await request<OptimizationRead>("/planner/optimize", {
        method: "POST",
        body: JSON.stringify(selection),
    });

    if (result === undefined) {
        throw new Error("The server returned no optimization result.");
    }

    return result;
}


export async function getPlannerOptions(characterId: number): Promise<PlannerOption[]> {
    const options = await request<PlannerOption[]>(`/planner/options/${characterId}`);

    if (options === undefined) {
        throw new Error("The server returned no planner options.");
    }

    return options;
}

export async function calculateMaterials(plan: CharacterPlanItem[]): Promise<Record<string, number>> {
    const materials = await request<Record<string, number>>("/planner/", {
        method: "POST",
        body: JSON.stringify(plan),
    });

    if (materials === undefined) {
        throw new Error("The server returned no materials.");
    }

    return materials;
}
