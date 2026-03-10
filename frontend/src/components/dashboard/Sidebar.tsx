"use client";

import { useState } from "react";

import SidebarFooter from "./sidebar/SidebarFooter";
import SidebarHeader from "./sidebar/SidebarHeader";
import SidebarNav from "./sidebar/SidebarNav";
import { navItems } from "./sidebar/navConfig";

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);

    // TODO: Replace with actual user data from auth context
    const currentUser = {
        name: "Dr. Admin",
        role: "Administrator",
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
                <SidebarNav items={navItems} collapsed={collapsed} />
            </div>
            <SidebarFooter user={currentUser} collapsed={collapsed} />
        </aside>
    );
}
