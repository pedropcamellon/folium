"use client";

import { useState } from "react";

import { getRoleLabel, hasAnyPermission } from "@/lib/permissions";
import { getDefaultRouteForRole } from "@/lib/role-routing";

import { useAuth } from "@/hooks/useAuth";

import SidebarFooter from "./sidebar/SidebarFooter";
import SidebarHeader from "./sidebar/SidebarHeader";
import SidebarNav from "./sidebar/SidebarNav";
import { navItems } from "./sidebar/navConfig";

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const { user } = useAuth();

    const filteredItems = navItems
        .map((item) => {
            if (item.id !== "home" || !user) {
                return item;
            }

            return {
                ...item,
                href: getDefaultRouteForRole(user.role),
            };
        })
        .filter((item) => {
            if (
                !item.requiredPermissions ||
                item.requiredPermissions.length === 0
            ) {
                return true;
            }

            return hasAnyPermission(user, item.requiredPermissions);
        });

    const currentUser = {
        name: user?.email.split("@")[0] ?? "Guest",
        role: user ? getRoleLabel(user.role) : "Signed out",
    };

    return (
        <aside
            className={`bg-white border-r flex flex-col justify-between transition-all duration-300 ${collapsed ? "w-16" : "w-64"}`}
        >
            <div>
                <SidebarHeader
                    collapsed={collapsed}
                    onToggleCollapse={() => setCollapsed(!collapsed)}
                />
                <SidebarNav items={filteredItems} collapsed={collapsed} />
            </div>
            <SidebarFooter user={currentUser} collapsed={collapsed} />
        </aside>
    );
}
