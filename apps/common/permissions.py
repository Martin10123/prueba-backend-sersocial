from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAgent(BasePermission):
    """Allow authenticated users with agent/supervisor/admin role."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "rol", None) in {"agente", "supervisor", "admin"}
        )


class IsSupervisorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "rol", None) in {"supervisor", "admin"}
        )


class ReadOnlyOrAuthenticatedAgent(BasePermission):
    """Public read for allowlisted views; write requires agent+."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsAuthenticatedAgent().has_permission(request, view)
