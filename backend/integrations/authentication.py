from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import IntegrationToken

class IntegrationUser:
    """
    Lightweight proxy user object representing an authenticated machine-to-machine integration.
    Carries the authoritative Brand and token instance without impersonating human users.
    """
    def __init__(self, brand, token_obj):
        self.brand = brand
        self.token = token_obj
        self.is_authenticated = True
        self.is_integration = True
        self.role = 'INTEGRATION'
        self.is_superuser = False
        self.is_staff = False
        self.pk = None
        self.id = None
        self.email = f"integration-{token_obj.id}@{brand.slug}.local"

    def get_full_name(self):
        return f"n8n Integration ({self.token.name})"

    def __str__(self):
        return self.get_full_name()

class IntegrationTokenAuthentication(authentication.BaseAuthentication):
    """
    Machine-to-Machine DRF Authentication for external automation tools (n8n).
    Inspects X-Integration-Api-Key or Authorization: Api-Key <token> request headers.
    """
    def authenticate(self, request):
        api_key = request.headers.get('X-Integration-Api-Key')
        if not api_key:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Api-Key '):
                api_key = auth_header.split(' ', 1)[1].strip()

        if not api_key:
            return None  # Pass to next authentication handler or permission check

        try:
            token_obj = IntegrationToken.objects.select_related('brand').get(key=api_key, is_active=True)
        except IntegrationToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or inactive Integration API Key.')

        token_obj.last_used_at = timezone.now()
        token_obj.save(update_fields=['last_used_at'])

        integration_user = IntegrationUser(token_obj.brand, token_obj)
        return (integration_user, token_obj)
