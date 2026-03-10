import {
    FaTachometerAlt,
    FaUserInjured,
    FaCalendarAlt,
    FaPhoneAlt,
    FaXRay,
    FaFileAlt,
    FaCog,
} from "react-icons/fa";
import { NavItem } from "./types";

export const navItems: NavItem[] = [
    {
        id: "home",
        label: "Home",
        href: "/",
        icon: FaTachometerAlt,
    },
    {
        id: "patients",
        label: "Patients",
        href: "/patients",
        icon: FaUserInjured,
    },
    {
        id: "appointments",
        label: "Appointments",
        href: "#",
        icon: FaCalendarAlt,
        // comingSoon: true, # TODO Add comming soon badge when we have more features to show
    },
    {
        id: "medical-calls",
        label: "Medical Calls",
        href: "#",
        icon: FaPhoneAlt,
    },
    {
        id: "imaging-ai",
        label: "Imaging AI",
        href: "#",
        icon: FaXRay,
    },
    {
        id: "reports",
        label: "Reports",
        href: "#",
        icon: FaFileAlt,
    },
    {
        id: "settings",
        label: "Settings",
        href: "#",
        icon: FaCog,
    },
];
