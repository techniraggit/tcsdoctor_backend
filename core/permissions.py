from rest_framework.permissions import BasePermission
import pretty_errors


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser and request.user.is_active:
            return True
        return False


class IsDoctorOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff and request.user.is_active:
            return True
        return False
