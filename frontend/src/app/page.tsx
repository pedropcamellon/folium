"use client";

import { useEffect } from "react";

import { useRouter } from "next/navigation";

import { getDefaultRouteForRole } from "@/lib/role-routing";

import { useAuth } from "@/hooks/useAuth";

export default function Home() {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (loading) {
            return;
        }

        if (!user) {
            router.replace("/login");
            return;
        }

        router.replace(getDefaultRouteForRole(user.role));
    }, [loading, router, user]);

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 text-slate-500">
            Loading dashboard...
        </div>
    );
}
