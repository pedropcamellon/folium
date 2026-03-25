import {
    FaCalendarAlt,
    FaCog,
    FaFileAlt,
    FaPhoneAlt,
    FaTachometerAlt,
    FaUserInjured,
    FaXRay,
} from "react-icons/fa";

import { permissions } from "@/lib/permissions";

import { NavItem } from "./types";

export const navItems: NavItem[] = [
    {
        id: "home",
        label: "Dashboard",
        href: "/",
        icon: FaTachometerAlt,
    },
    {
        id: "patients",
        label: "Patients",
        href: "/patients",
        icon: FaUserInjured,
        requiredPermissions: [permissions.patientsRead],
    },
    {
        id: "appointments",
        label: "Appointments",
        href: "#",
        icon: FaCalendarAlt,
        comingSoon: true,
        requiredPermissions: [permissions.patientsRead],
    },
    {
        id: "medical-calls",
        label: "Medical Calls",
        href: "#",
        icon: FaPhoneAlt,
        comingSoon: true,
        requiredPermissions: [permissions.voiceRecord],
    },
    {
        id: "imaging-ai",
        label: "Imaging AI",
        href: "#",
        icon: FaXRay,
        comingSoon: true,
        requiredPermissions: [permissions.documentsRead],
    },
    {
        id: "reports",
        label: "Reports",
        href: "#",
        icon: FaFileAlt,
        comingSoon: true,
        requiredPermissions: [permissions.adminHealthRead],
    },
    {
        id: "settings",
        label: "Settings",
        href: "#",
        icon: FaCog,
        comingSoon: true,
    },
];
