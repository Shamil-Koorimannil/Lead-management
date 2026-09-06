from rest_framework import permissions
from users.models import UserRole

class IsBrandOwner(permissions.BasePermission):
    """Allows access only to Brand Owner users or Superusers."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == UserRole.BRAND_OWNER or request.user.is_superuser)
        )

class IsSalesManagerOrOwner(permissions.BasePermission):
    """Allows access to Sales Managers and Brand Owners."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.BRAND_OWNER, UserRole.SALES_MANAGER] or request.user.is_superuser
        )

class IsAuthenticatedUser(permissions.BasePermission):
    """Allows access to any authenticated user."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class CanManageUsers(permissions.BasePermission):
    """Only Brand Owners can manage team users."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == UserRole.BRAND_OWNER or request.user.is_superuser)
        )

class CanManageQualificationRules(permissions.BasePermission):
    """Only Brand Owners can manage qualification rules (or Sales Managers for read-only)."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == UserRole.BRAND_OWNER or request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS and request.user.role == UserRole.SALES_MANAGER:
            return True
        return False
