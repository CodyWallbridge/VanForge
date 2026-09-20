import type { AppSettingsRead } from "../dto/AppSettingsRead";
import { request } from "./request";

export async function getSettings(): Promise<AppSettingsRead> {
    const settings = await request<AppSettingsRead>("/settings/");

    if (settings === undefined) {
        throw new Error("The server returned no settings.");
    }

    return settings;
}


export async function setCurrentExpansion(expansionId: number): Promise<AppSettingsRead> {
    const updated = await request<AppSettingsRead>("/settings/", {
        method: "PATCH",
        body: JSON.stringify({ current_expansion_id: expansionId }),
    });

    if (updated === undefined) {
        throw new Error("The server returned no updated settings.");
    }

    return updated;
}
