"use client";

/**
 * Authentication Context Provider
 * Manages global authentication state
 */

import { createContext, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User, LoginCredentials, RegisterData, UserRole } from "@/types/user";
import * as authApi from "@/lib/auth-api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  hasRole: (roles: UserRole[]) => boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const isAuthenticated = !!user;

  /**
   * Fetch current user from API
   */
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : "Failed to fetch user");
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Check if current user has one of the specified roles
   */
  const hasRole = useCallback(
    (roles: UserRole[]): boolean => {
      if (!user) return false;
      return roles.includes(user.role);
    },
    [user]
  );

  /**
   * Login user
   */
  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setLoading(true);
        setError(null);
        await authApi.login(credentials);
        await refreshUser();
        router.push("/");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Login failed");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [refreshUser, router]
  );

  /**
   * Register new user
   */
  const register = useCallback(
    async (data: RegisterData) => {
      try {
        setLoading(true);
        setError(null);
        await authApi.register(data);
        // Auto-login after registration
        await login({ username: data.email, password: data.password });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Registration failed");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [login]
  );

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      setLoading(true);
      await authApi.logout();
      setUser(null);
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Logout failed");
    } finally {
      setLoading(false);
    }
  }, [router]);

  /**
   * Initialize auth state on mount
   */
  useEffect(() => {
    const token = authApi.getAuthToken();
    if (token) {
      refreshUser();
    } else {
      setLoading(false);
    }
  }, [refreshUser]);

  const value: AuthContextType = {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
