"""Central permission registry for API and UI access control."""

from app.models.user import UserRole


class Permission:
    """Named permissions used across backend access checks."""

    PATIENTS_READ = "patients:read"
    PATIENTS_CREATE = "patients:create"
    PATIENTS_UPDATE = "patients:update"
    PATIENTS_DELETE = "patients:delete"
    INTERACTIONS_READ = "interactions:read"
    INTERACTIONS_CREATE = "interactions:create"
    INTERACTIONS_UPDATE = "interactions:update"
    INTERACTIONS_DELETE = "interactions:delete"
    INTERACTIONS_SUMMARIZE = "interactions:summarize"
    DOCUMENTS_READ = "documents:read"
    DOCUMENTS_CREATE = "documents:create"
    DOCUMENTS_UPDATE = "documents:update"
    DOCUMENTS_DELETE = "documents:delete"
    VOICE_RECORD = "voice:record"
    VOICE_REVIEW = "voice:review"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    ADMIN_HEALTH_READ = "admin:health:read"


ALL_PERMISSIONS = {
    Permission.PATIENTS_READ,
    Permission.PATIENTS_CREATE,
    Permission.PATIENTS_UPDATE,
    Permission.PATIENTS_DELETE,
    Permission.INTERACTIONS_READ,
    Permission.INTERACTIONS_CREATE,
    Permission.INTERACTIONS_UPDATE,
    Permission.INTERACTIONS_DELETE,
    Permission.INTERACTIONS_SUMMARIZE,
    Permission.DOCUMENTS_READ,
    Permission.DOCUMENTS_CREATE,
    Permission.DOCUMENTS_UPDATE,
    Permission.DOCUMENTS_DELETE,
    Permission.VOICE_RECORD,
    Permission.VOICE_REVIEW,
    Permission.USERS_READ,
    Permission.USERS_UPDATE,
    Permission.ADMIN_HEALTH_READ,
}


ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN: set(ALL_PERMISSIONS),
    UserRole.PROVIDER: {
        Permission.PATIENTS_READ,
        Permission.PATIENTS_CREATE,
        Permission.PATIENTS_UPDATE,
        Permission.PATIENTS_DELETE,
        Permission.INTERACTIONS_READ,
        Permission.INTERACTIONS_CREATE,
        Permission.INTERACTIONS_UPDATE,
        Permission.INTERACTIONS_DELETE,
        Permission.INTERACTIONS_SUMMARIZE,
        Permission.DOCUMENTS_READ,
        Permission.DOCUMENTS_CREATE,
        Permission.DOCUMENTS_UPDATE,
        Permission.DOCUMENTS_DELETE,
        Permission.VOICE_RECORD,
        Permission.VOICE_REVIEW,
    },
    UserRole.STAFF: {
        Permission.PATIENTS_READ,
        Permission.PATIENTS_CREATE,
        Permission.PATIENTS_UPDATE,
        Permission.INTERACTIONS_READ,
        Permission.INTERACTIONS_CREATE,
        Permission.INTERACTIONS_UPDATE,
        Permission.VOICE_RECORD,
        Permission.VOICE_REVIEW,
    },
    UserRole.PATIENT: set(),
}


def role_has_permission(role: UserRole, permission: str) -> bool:
    """Return whether the given role grants the requested permission."""

    return permission in ROLE_PERMISSIONS.get(role, set())
