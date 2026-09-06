from django.db import models
from django.utils.translation import gettext_lazy as _
from leads.models import Lead, LeadSource
from users.models import User

class ConversationStatus(models.TextChoices):
    OPEN = 'OPEN', _('Open')
    CLOSED = 'CLOSED', _('Closed')

class MessageDirection(models.TextChoices):
    INBOUND = 'INBOUND', _('Inbound')
    OUTBOUND = 'OUTBOUND', _('Outbound')

class MessageType(models.TextChoices):
    TEXT = 'TEXT', _('Text')
    IMAGE = 'IMAGE', _('Image')
    DOCUMENT = 'DOCUMENT', _('Document')
    SYSTEM = 'SYSTEM', _('System')
    AI = 'AI', _('AI')
    NOTE = 'NOTE', _('Note')

class Conversation(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='conversations')
    channel = models.CharField(max_length=30, choices=LeadSource.choices, default=LeadSource.MANUAL)
    status = models.CharField(max_length=20, choices=ConversationStatus.choices, default=ConversationStatus.OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Conversation #{self.id} for {self.lead.lead_number} ({self.channel})"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    direction = models.CharField(max_length=20, choices=MessageDirection.choices, default=MessageDirection.INBOUND)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    external_message_id = models.CharField(max_length=255, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg #{self.id} ({self.direction}) - {self.message[:30]}"

class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_notes')
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.author.get_full_name()} on {self.lead.lead_number}"
