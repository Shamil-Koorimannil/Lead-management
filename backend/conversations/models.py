from django.db import models
from django.utils.translation import gettext_lazy as _
from leads.models import Lead, LeadSource
from users.models import Brand, User

class ConversationStatus(models.TextChoices):
    OPEN = 'OPEN', _('Open')
    CLOSED = 'CLOSED', _('Closed')

class ConversationState(models.TextChoices):
    NEW = 'NEW', _('New')
    QUALIFYING = 'QUALIFYING', _('Qualifying')
    WAITING_INVESTMENT = 'WAITING_INVESTMENT', _('Waiting Investment')
    CONFIRMING_INVESTMENT = 'CONFIRMING_INVESTMENT', _('Confirming Investment')
    WAITING_PROFESSION = 'WAITING_PROFESSION', _('Waiting Profession')
    WAITING_BUSINESS_DURATION = 'WAITING_BUSINESS_DURATION', _('Waiting Business Duration')
    WAITING_PREVIOUS_EXPERIENCE = 'WAITING_PREVIOUS_EXPERIENCE', _('Waiting Previous Experience')
    WAITING_LOCATION = 'WAITING_LOCATION', _('Waiting Location')
    WAITING_OPENING_TIMELINE = 'WAITING_OPENING_TIMELINE', _('Waiting Opening Timeline')
    QUALIFIED = 'QUALIFIED', _('Qualified')
    DISQUALIFIED = 'DISQUALIFIED', _('Disqualified')
    HUMAN_HANDOFF = 'HUMAN_HANDOFF', _('Human Handoff')

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

class InstagramContact(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='instagram_contacts')
    instagram_account_id = models.CharField(max_length=255, db_index=True, help_text=_('ID of connected Instagram Professional account'))
    instagram_user_id = models.CharField(max_length=255, db_index=True, help_text=_('Stable external Meta IG User ID'))
    username = models.CharField(max_length=255, blank=True, default='')
    display_name = models.CharField(max_length=255, blank=True, default='')
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='instagram_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('brand', 'instagram_account_id', 'instagram_user_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"IG @{self.username or self.instagram_user_id} ({self.brand.name})"

class Conversation(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='conversations')
    instagram_contact = models.ForeignKey(
        InstagramContact, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations'
    )
    channel = models.CharField(max_length=30, choices=LeadSource.choices, default=LeadSource.MANUAL)
    status = models.CharField(max_length=20, choices=ConversationStatus.choices, default=ConversationStatus.OPEN)
    state = models.CharField(
        max_length=40, choices=ConversationState.choices, default=ConversationState.NEW, db_index=True
    )
    is_automation_enabled = models.BooleanField(
        default=True, help_text=_('Disables automated qualification when human salesperson takes over')
    )
    pending_investment_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        help_text=_('Transient storage during investment confirmation step')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Conversation #{self.id} for {self.lead.lead_number} ({self.channel} - {self.state})"

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
