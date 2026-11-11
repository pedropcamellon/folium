import { IS_MOCK_API } from "./api-mode";

const TOKEN_KEY = "auth_token";

export function setAuthToken(token: string): void {
    if (typeof window !== "undefined") {
        localStorage.setItem(TOKEN_KEY, token);
    }
}

export function getAuthToken(): string | null {
    if (typeof window === "undefined") return null;

    return (
        localStorage.getItem(TOKEN_KEY) ?? (IS_MOCK_API ? "demo-token" : null)
    );
}

export function clearAuthToken(): void {
    if (typeof window !== "undefined") {
        localStorage.removeItem(TOKEN_KEY);
    }
}
