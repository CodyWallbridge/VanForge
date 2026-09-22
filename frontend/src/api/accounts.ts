import type { AuthenticatedUser } from "../dto/AuthenticatedUser";
import { request } from "./request";

export async function getAccounts(): Promise<AuthenticatedUser[]> {
    return await request<AuthenticatedUser[]>("/accounts/") ?? [];
}

export async function updateAccountRole(accountId: number, role: "user" | "admin"): Promise<AuthenticatedUser> {
    const account = await request<AuthenticatedUser>(`/accounts/${accountId}/role`, {
        method: "PATCH",
        body: JSON.stringify({ role }),
    });

    if (!account) {
        throw new Error("The backend did not return the updated account.");
    }

    return account;
}

export async function deleteAccount(accountId: number): Promise<void> {
    await request<void>(`/accounts/${accountId}`, { method: "DELETE" });
}
