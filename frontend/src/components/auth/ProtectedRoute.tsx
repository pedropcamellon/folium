"use client";

/**
 * Protected Route component
 * Wraps content that requires authentication and optional role-based access
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";

// Types
import { UserRole } from "@/types/user";

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: UserRole[];
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
    const { isAuthenticated, loading, user, hasRole } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push("/login");
            return;
        }

        if (!loading && isAuthenticated && allowedRoles && !hasRole(allowedRoles)) {
            // Redirect to home if user lacks required role
            // TODO: Consider redirecting to a dedicated "Access Denied" page instead
            router.push("/");
        }
    }, [isAuthenticated, loading, user, allowedRoles, hasRole, router]);

    // Show loading state with pulse animation
    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
                <div className="text-center space-y-4">
                    <div className="relative">
                        <div className="h-16 w-16 rounded-full border-4 border-primary/20 animate-pulse mx-auto" />
                        <div className="absolute inset-0 h-16 w-16 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto" />
                    </div>
                    <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-600 animate-pulse">
                            Authenticating...
                        </p>
                        <div className="flex gap-1 justify-center">
                            <div className="h-1.5 w-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                            <div className="h-1.5 w-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                            <div className="h-1.5 w-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Show redirecting message if not authenticated
    if (!isAuthenticated) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
                <div className="text-center space-y-4 animate-in fade-in duration-300">
                    <div className="mx-auto w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center">
                        <svg
                            className="w-8 h-8 text-amber-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                            />
                        </svg>
                    </div>
                    <div className="space-y-1">
                        <p className="text-lg font-semibold text-slate-800">
                            Authentication Required
                        </p>
                        <p className="text-sm text-slate-600">
                            Redirecting to login...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // Show access denied message if role not allowed
    if (allowedRoles && !hasRole(allowedRoles)) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
                <div className="text-center space-y-4 animate-in fade-in duration-300">
                    <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                        <svg
                            className="w-8 h-8 text-red-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
                            />
                        </svg>
                    </div>
                    <div className="space-y-1">
                        <p className="text-lg font-semibold text-slate-800">
                            Access Denied
                        </p>
                        <p className="text-sm text-slate-600">
                            You don&apos;t have permission to view this page
                        </p>
                        <p className="text-xs text-slate-500 mt-2">
                            Redirecting...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}
