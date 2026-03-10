import { IconType } from "react-icons";

export interface NavItem {
    id: string;
    label: string;
    href: string;
    icon: IconType;
    badge?: number;
    comingSoon?: boolean;
}

export interface UserProfile {
    name: string;
    role: string;
    avatarUrl?: string;
}
