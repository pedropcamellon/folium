import { UserRole } from "@/types/user";

export function getDefaultRouteForRole(role: UserRole): string {
    switch (role) {
        case UserRole.ADMIN:
            return "/admin";
        case UserRole.PROVIDER:
            return "/provider";
        case UserRole.STAFF:
            return "/receptionist";
        case UserRole.PATIENT:
            return "/portal";
        default:
            return "/login";
    }
}
