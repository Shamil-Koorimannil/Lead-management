from rest_framework import permissions

class HasValidIntegrationToken(permissions.BasePermission):
    """
    Permission class allowing access strictly to machine-to-machine integrations
    authenticated via a valid IntegrationToken.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            getattr(request.user, 'is_authenticated', False) and
            getattr(request.user, 'is_integration', False) and
            getattr(request.user, 'brand', None) is not None
        )
