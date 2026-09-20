import type { ExpansionRead } from "../dto/ExpansionRead";
import { request } from "./request";

export async function getExpansions(): Promise<ExpansionRead[]> {
    const expansions = await request<ExpansionRead[]>("/expansions/");

    if (expansions === undefined) {
        throw new Error("The server returned no expansion list.");
    }

    return expansions;
}
