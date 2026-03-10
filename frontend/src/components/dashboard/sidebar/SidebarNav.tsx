"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NavItem } from "./types";

interface SidebarNavProps {
    items: NavItem[];
    collapsed: boolean;
}

export default function SidebarNav({ items, collapsed }: SidebarNavProps) {
    const pathname = usePathname();

    const isActive = (href: string) => {
        if (href === "/") {
            return pathname === "/";
        }
        return pathname.startsWith(href);
    };

    return (
        <nav className="mt-4 flex-1">
            <ul className="space-y-2 px-2">
                {items.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);

                    // Use Link for real hrefs, <a> for placeholders
                    const Component = item.comingSoon ? "a" : Link;

                    return (
                        <li key={item.id}>
                            <Component
                                className={`flex items-center px-3 py-2 rounded font-medium transition-colors ${
                                    active
                                        ? "bg-blue-50 text-blue-700"
                                        : "hover:bg-slate-100 text-gray-700"
                                }`}
                                href={item.href}
                            >
                                <Icon size={20} />
                                <span
                                    className={`ml-3 ${collapsed ? "hidden" : "inline"}`}
                                >
                                    {item.label}
                                </span>
                                {!collapsed && item.badge !== undefined && (
                                    <span className="ml-auto bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                                        {item.badge}
                                    </span>
                                )}
                            </Component>
                        </li>
                    );
                })}
            </ul>
        </nav>
    );
}
