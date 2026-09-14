from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import Brand, User

class LeadSource(models.TextChoices):
    MANUAL = 'MANUAL', _('Manual')
    TEST = 'TEST', _('Test')
    WHATSAPP = 'WHATSAPP', _('WhatsApp')
    WEBSITE = 'WEBSITE', _('Website')
    INSTAGRAM = 'INSTAGRAM', _('Instagram')
    FACEBOOK = 'FACEBOOK', _('Facebook')
    GOOGLE_ADS = 'GOOGLE_ADS', _('Google Ads')
    OTHER = 'OTHER', _('Other')

class SalesStatus(models.TextChoices):
    NEW = 'NEW', _('New')
    CONTACTED = 'CONTACTED', _('Contacted')
    FOLLOW_UP = 'FOLLOW_UP', _('Follow Up')
    MEETING = 'MEETING', _('Meeting')
    NEGOTIATION = 'NEGOTIATION', _('Negotiation')
    CONVERTED = 'CONVERTED', _('Converted')
    LOST = 'LOST', _('Lost')

class QualificationStatus(models.TextChoices):
    QUALIFIED = 'QUALIFIED', _('Qualified')
    REVIEW = 'REVIEW', _('Review')
    NOT_QUALIFIED = 'NOT_QUALIFIED', _('Not Qualified')

class LeadTemperature(models.TextChoices):
    HOT = 'HOT', _('Hot')
    WARM = 'WARM', _('Warm')
    COLD = 'COLD', _('Cold')
    LONG_TERM = 'LONG_TERM', _('Long Term')
    DISQUALIFIED = 'DISQUALIFIED', _('Disqualified')

class CurrentProfession(models.TextChoices):
    BUSINESS = 'BUSINESS', _('Business')
    SALARIED = 'SALARIED', _('Salaried')
    SELF_EMPLOYED = 'SELF_EMPLOYED', _('Self Employed')
    STUDENT = 'STUDENT', _('Student')
    OTHER = 'OTHER', _('Other')

class OpeningTimeline(models.TextChoices):
    WITHIN_2_MONTHS = 'WITHIN_2_MONTHS', _('Within 2 months')
    WITHIN_6_MONTHS = 'WITHIN_6_MONTHS', _('Within 6 months')
    WITHIN_1_YEAR = 'WITHIN_1_YEAR', _('Within 1 year')
    MORE_THAN_1_YEAR = 'MORE_THAN_1_YEAR', _('More than 1 year')
    NOT_DECIDED = 'NOT_DECIDED', _('Not decided yet')

class FollowUpType(models.TextChoices):
    CALL = 'CALL', _('Call')
    WHATSAPP = 'WHATSAPP', _('WhatsApp')
    MEETING = 'MEETING', _('Meeting')
    EMAIL = 'EMAIL', _('Email')
    OTHER = 'OTHER', _('Other')

class LeadSequence(models.Model):
    brand = models.OneToOneField(Brand, on_delete=models.CASCADE, related_name='lead_sequence')
    next_number = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _('Lead Sequence Counter')

    @classmethod
    def get_next_lead_number(cls, brand):
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(brand=brand)
            number = seq.next_number
            seq.next_number += 1
            seq.save(update_fields=['next_number'])
            return f"LEAD-{number:06d}"

class Lead(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='leads')
    lead_number = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=50, db_index=True)
    email = models.EmailField(db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    preferred_location = models.CharField(max_length=100, blank=True, default='')

    investment_capacity = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    property_available = models.BooleanField(default=False)
    business_experience = models.BooleanField(default=False)
    expected_start = models.CharField(max_length=100, blank=True, default='')

    # Franchise Qualification Fields
    current_profession = models.CharField(
        max_length=30, choices=CurrentProfession.choices, null=True, blank=True
    )
    business_duration = models.CharField(max_length=100, blank=True, default='')
    previous_business_experience = models.BooleanField(null=True, blank=True)
    opening_timeline = models.CharField(
        max_length=30, choices=OpeningTimeline.choices, null=True, blank=True
    )
    lead_temperature = models.CharField(
        max_length=30, choices=LeadTemperature.choices, null=True, blank=True, default=None, db_index=True
    )

    lead_source = models.CharField(
        max_length=30, choices=LeadSource.choices, default=LeadSource.MANUAL, db_index=True
    )

    qualification_score = models.IntegerField(default=0)
    qualification_status = models.CharField(
        max_length=30, choices=QualificationStatus.choices, default=QualificationStatus.REVIEW, db_index=True
    )
    qualification_reason = models.TextField(blank=True, default='')

    follow_up_required = models.BooleanField(default=False)
    next_follow_up_at = models.DateTimeField(null=True, blank=True, db_index=True)
    follow_up_type = models.CharField(
        max_length=30, choices=FollowUpType.choices, null=True, blank=True
    )
    follow_up_note = models.TextField(blank=True, default='')

    sales_status = models.CharField(
        max_length=30, choices=SalesStatus.choices, default=SalesStatus.NEW, db_index=True
    )

    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads', db_index=True
    )
    assigned_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lead_number} - {self.name} ({self.qualification_status})"

class ActivityAction(models.TextChoices):
    LEAD_CREATED = 'LEAD_CREATED', _('Lead Created')
    LEAD_UPDATED = 'LEAD_UPDATED', _('Lead Updated')
    LEAD_ASSIGNED = 'LEAD_ASSIGNED', _('Lead Assigned')
    QUALIFICATION_CHANGED = 'QUALIFICATION_CHANGED', _('Qualification Changed')
    LEAD_TEMPERATURE_CHANGED = 'LEAD_TEMPERATURE_CHANGED', _('Lead Temperature Changed')
    LEAD_DISQUALIFIED = 'LEAD_DISQUALIFIED', _('Lead Disqualified')
    QUALIFICATION_COMPLETED = 'QUALIFICATION_COMPLETED', _('Qualification Completed')
    STATUS_CHANGED = 'STATUS_CHANGED', _('Sales Status Changed')
    NOTE_ADDED = 'NOTE_ADDED', _('Note Added')
    FOLLOW_UP_SCHEDULED = 'FOLLOW_UP_SCHEDULED', _('Follow Up Scheduled')
    FOLLOW_UP_COMPLETED = 'FOLLOW_UP_COMPLETED', _('Follow Up Completed')
    LEAD_CONVERTED = 'LEAD_CONVERTED', _('Lead Converted')
    LEAD_LOST = 'LEAD_LOST', _('Lead Lost')
    INSTAGRAM_MESSAGE_RECEIVED = 'INSTAGRAM_MESSAGE_RECEIVED', _('Instagram Message Received')
    INSTAGRAM_MESSAGE_SENT = 'INSTAGRAM_MESSAGE_SENT', _('Instagram Message Sent')

class ActivityLog(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='activities')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=40, choices=ActivityAction.choices)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lead.lead_number} - {self.action} at {self.created_at}"
