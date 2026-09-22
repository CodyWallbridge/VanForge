import { API_URL } from "../config";
import { neonAuth } from "../auth";

interface ValidationError {
    loc: Array<string | number>;
    msg: string;
}

interface ErrorResponse {
    detail?: string | ValidationError[];
}

export async function request<T>(
    path: string,
    options: RequestInit = {},
): Promise<T | undefined> {
    const headers = new Headers(options.headers);

    const token = await neonAuth.getJWTToken();

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    if (typeof options.body === "string" && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    let response: Response;

    try {
        response = await fetch(`${API_URL}${path}`, {
            ...options,
            headers,
        });
    } catch {
        throw new Error("Cannot connect to the backend. Make sure it is running and try again.");
    }

    if (!response.ok) {
        let message = `Request failed (${response.status})`;

        if ([502, 503, 504].includes(response.status)) {
            message = "The backend is unavailable. Make sure it is running and try again.";
        }
        
        let errorBody: ErrorResponse | undefined;

        try {
            errorBody = await response.json();
        } catch {
            // The server may return an error without a JSON body.
        }

        if (typeof errorBody?.detail === "string") {
            message = errorBody.detail;
        } else if (Array.isArray(errorBody?.detail)) {
            message = errorBody.detail
                .map((error) => {
                    const field = error.loc.join(".");
                    return `${field}: ${error.msg}`;
                })
                .join("; ");
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return undefined;
    }

    return response.json();
}