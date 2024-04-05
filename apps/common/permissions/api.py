from rest_framework import permissions


class IsValidUser(permissions.IsAuthenticated):
    """
        有效用户
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_active


class IsAdminUser(IsValidUser):
    """
        admin用户
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'
