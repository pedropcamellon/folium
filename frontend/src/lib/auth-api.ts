/**
 * Authentication API client
 * Handles all auth-related API calls to FastAPI backend
 */

import { AuthTokens, LoginCredentials, RegisterData, User } from "@/types/user";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

const AUTH_ENDPOINTS = {
  register: `${FASTAPI_BASE_URL}/auth/register`,
  login: `${FASTAPI_BASE_URL}/auth/jwt/login`,
  logout: `${FASTAPI_BASE_URL}/auth/jwt/logout`,
  me: `${FASTAPI_BASE_URL}/users/me`,
} as const;

// Token storage keys
const TOKEN_KEY = "auth_token";

/**
 * Store authentication token in localStorage
 */
export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Retrieve authentication token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Remove authentication token from localStorage
 */
export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

/**
 * Register new user
 */
export async function register(data: RegisterData): Promise<User> {
  const response = await fetch(AUTH_ENDPOINTS.register, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Registration failed");
  }

  return response.json();
}

/**
 * Login user and store token
 */
export async function login(credentials: LoginCredentials): Promise<AuthTokens> {
  // fastapi-users expects form data for login
  const formData = new URLSearchParams();
  formData.append("username", credentials.username);
  formData.append("password", credentials.password);

  const response = await fetch(AUTH_ENDPOINTS.login, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

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
      await fetch(AUTH_ENDPOINTS.logout, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
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

  const response = await fetch(AUTH_ENDPOINTS.me, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken();
      throw new Error("Authentication expired");
    }
    throw new Error("Failed to fetch user");
  }

  return response.json();
}
