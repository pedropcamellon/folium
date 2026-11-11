/**
 * Authentication API client
 * Handles all auth-related API calls to FastAPI backend
 */
import type {
    AuthTokens,
    LoginCredentials,
    RegisterData,
    User,
} from "@/types/user";
import { API_ENDPOINTS, apiRequest } from "./api";
import {
    clearAuthToken,
    getAuthToken,
    setAuthToken,
} from "./auth-token";

export { clearAuthToken, getAuthToken, setAuthToken } from "./auth-token";

/**
 * Register new user
 */
export async function register(data: RegisterData): Promise<User> {
    const response = await apiRequest(
        API_ENDPOINTS.authRegister,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        },
        { authenticated: false }
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Registration failed");
    }

    return response.json();
}

/**
 * Login user and store token
 */
export async function login(
    credentials: LoginCredentials
): Promise<AuthTokens> {
    // fastapi-users expects form data for login
    const formData = new URLSearchParams();
    formData.append("username", credentials.username);
    formData.append("password", credentials.password);

    const response = await apiRequest(
        API_ENDPOINTS.authLogin,
        {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        },
        { authenticated: false }
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
    }

    const tokens: AuthTokens = await response.json();
    setAuthToken(tokens.access_token);
    return tokens;
}

/**
 * Logout user and clear token
 */
export async function logout(): Promise<void> {
    const token = getAuthToken();

    if (token) {
        try {
            await apiRequest(API_ENDPOINTS.authLogout, { method: "POST" });
        } catch (error) {
            console.error("Logout request failed:", error);
        }
    }

    clearAuthToken();
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
    const token = getAuthToken();

    if (!token) {
        throw new Error("No authentication token found");
    }

    const response = await apiRequest(API_ENDPOINTS.usersMe);

    if (!response.ok) {
        if (response.status === 401) {
            clearAuthToken();
            throw new Error("Authentication expired");
        }
        throw new Error("Failed to fetch user");
    }

    return response.json();
}
