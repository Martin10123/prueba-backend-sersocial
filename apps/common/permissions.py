from rest_framework.permissions import BasePermission


class IsAuthenticatedAgent(BasePermission):
    """Allow authenticated users with agent/supervisor/admin role."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "rol", None) in {"agente", "supervisor", "admin"}
        )
