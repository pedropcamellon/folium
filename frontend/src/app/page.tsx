"use client";

import Image from "next/image";
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
        <div className="flex min-h-screen flex-col items-center justify-center gap-8 bg-slate-50 px-6 text-slate-500">
            <Image
                src="/banner.png"
                alt="Folium EHR"
                width={473}
                height={149}
                priority
                className="h-auto w-full max-w-[473px]"
            />
            <p>Loading dashboard...</p>
        </div>
    );
}
