import type { OptimizationRead } from "../dto/OptimizationRead";
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
