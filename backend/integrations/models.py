import secrets
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import Brand
from leads.models import Lead

class IntegrationToken(models.Model):
    """
    Machine-to-Machine Integration API Key Token.
    Binds an external integration client (e.g. n8n) strictly to an authoritative Brand.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='integration_tokens')
    name = models.CharField(max_length=255, help_text=_('Description of the integration client e.g. n8n Production'))
    key = models.CharField(max_length=128, unique=True, db_index=True, help_text=_('Machine-to-machine API Key secret token'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    @classmethod
    def generate_key(cls):
        return f"n8n_sec_{secrets.token_urlsafe(32)}"

class IntegrationEvent(models.Model):
    """
    Tracks external integration event IDs for database-level concurrency-safe idempotency.
    Enforces uniqueness per brand to prevent duplicate lead creation on workflow retries.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='integration_events')
    external_event_id = models.CharField(max_length=255, db_index=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='integration_events', null=True, blank=True)
    source = models.CharField(max_length=50, default='N8N')
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('brand', 'external_event_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"Event {self.external_event_id} ({self.brand.name})"
