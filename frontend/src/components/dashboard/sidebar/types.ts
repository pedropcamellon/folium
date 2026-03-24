import { IconType } from "react-icons";

import { Permission } from "@/lib/permissions";

export interface NavItem {
    id: string;
    label: string;
    href: string;
    icon: IconType;
    badge?: number;
    comingSoon?: boolean;
    requiredPermissions?: Permission[];
}

export interface UserProfile {
    name: string;
    role: string;
    avatarUrl?: string;
}
