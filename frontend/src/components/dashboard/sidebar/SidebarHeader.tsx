"use client";

import Image from "next/image";
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
                aria-label="Folium home"
                className="flex min-w-0 items-center"
            >
                {collapsed ? (
                    <Image
                        src="/logo-icon.png"
                        alt="Folium"
                        width={28}
                        height={34}
                        className="h-9 w-auto object-contain"
                    />
                ) : (
                    <Image
                        src="/banner.png"
                        alt="Folium EHR"
                        width={473}
                        height={149}
                        priority
                        className="h-auto max-h-10 w-auto max-w-[160px] object-contain"
                    />
                )}
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
