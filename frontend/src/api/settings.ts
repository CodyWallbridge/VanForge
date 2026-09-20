import type { AppSettingsRead } from "../dto/AppSettingsRead";
import { request } from "./request";

export async function getSettings(): Promise<AppSettingsRead> {
    const settings = await request<AppSettingsRead>("/settings/");

    if (settings === undefined) {
        throw new Error("The server returned no settings.");
    }

    return settings;
}
