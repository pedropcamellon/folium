"use client";

import Link from "next/link";

import { FaChevronLeft, FaChevronRight } from "react-icons/fa";

interface SidebarHeaderProps {
    collapsed: boolean;
    onToggleCollapse: () => void;
}

export default function SidebarHeader({
    collapsed,
    onToggleCollapse,
}: SidebarHeaderProps) {
    return (
        <div className="flex items-center h-16 px-4 border-b justify-between">
            <Link
                href="/"
                className={`font-bold text-xl text-blue-700 transition-opacity duration-200 hover:text-blue-800 ${collapsed ? "opacity-0 w-0" : "opacity-100 w-auto"}`}
            >
                SouthDrift
            </Link>
            <button
                className="p-2 rounded hover:bg-slate-100 ml-2"
                onClick={onToggleCollapse}
                aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                tabIndex={0}
            >
                {collapsed ? (
                    <FaChevronRight size={20} />
                ) : (
                    <FaChevronLeft size={20} />
                )}
            </button>
        </div>
    );
}
