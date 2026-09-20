import type { ExpansionCreate } from "../dto/ExpansionCreate";
import type { ExpansionRead } from "../dto/ExpansionRead";
import type { ExpansionUpdate } from "../dto/ExpansionUpdate";
import { request } from "./request";

export async function getExpansions(): Promise<ExpansionRead[]> {
    const expansions = await request<ExpansionRead[]>("/expansions/");

    if (expansions === undefined) {
        throw new Error("The server returned no expansion list.");
    }

    return expansions;
}


export async function createExpansion(expansion: ExpansionCreate): Promise<ExpansionRead> {
    const created = await request<ExpansionRead>("/expansions/", {
        method: "POST",
        body: JSON.stringify(expansion),
    });

    if (created === undefined) {
        throw new Error("The server returned no expansion.");
    }

    return created;
}

export async function updateExpansion(
    expansionId: number,
    changes: ExpansionUpdate,
): Promise<ExpansionRead> {
    const updated = await request<ExpansionRead>(`/expansions/${expansionId}`, {
        method: "PATCH",
        body: JSON.stringify(changes),
    });

    if (updated === undefined) {
        throw new Error("The server returned no updated expansion.");
    }

    return updated;
}

export async function deleteExpansion(expansionId: number): Promise<void> {
    await request<void>(`/expansions/${expansionId}`, {
        method: "DELETE",
    });
}
