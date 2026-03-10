"use client";

import { UserProfile } from "./types";

interface SidebarFooterProps {
    user: UserProfile;
    collapsed: boolean;
}

export default function SidebarFooter({ user, collapsed }: SidebarFooterProps) {
    return (
        <div className="p-4 border-t">
            <div className="flex items-center space-x-3">
                {user.avatarUrl ? (
                    <img
                        src={user.avatarUrl}
                        alt={user.name}
                        className="w-10 h-10 rounded-full"
                    />
                ) : (
                    <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-semibold">
                        {user.name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .toUpperCase()}
                    </div>
                )}
                <div className={`${collapsed ? "hidden" : "block"}`}>
                    <div className="font-semibold">{user.name}</div>
                    <div className="text-xs text-slate-500">{user.role}</div>
                </div>
            </div>
        </div>
    );
}
