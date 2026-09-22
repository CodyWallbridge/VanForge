import type { AuthenticatedUser } from "../dto/AuthenticatedUser";
import { request } from "./request";

export async function getAuthenticatedUser(): Promise<AuthenticatedUser> {
    const user = await request<AuthenticatedUser>("/accounts/me");

    if (!user) {
        throw new Error("The backend did not return the authenticated user.");
    }

    return user;
}