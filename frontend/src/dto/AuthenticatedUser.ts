export interface AuthenticatedUser {
    id: number;
    auth_user_id: string;
    email: string | null;
    role: "user" | "admin";
}
