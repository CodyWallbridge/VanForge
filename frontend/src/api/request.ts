import { API_URL } from "../config";

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

    if (typeof options.body === "string" && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        let message = `Request failed (${response.status})`;
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