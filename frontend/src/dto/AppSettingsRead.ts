import type { ExpansionRead } from "./ExpansionRead";

export interface AppSettingsRead {
    id: number;
    current_expansion_id: number;
    current_expansion: ExpansionRead;
}
