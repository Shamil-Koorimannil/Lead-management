from decimal import Decimal
from rest_framework import serializers
from leads.models import Lead, LeadSource
from .models import IntegrationEvent

class IntegrationLeadCreateSerializer(serializers.Serializer):
    external_event_id = serializers.CharField(max_length=255, required=True, help_text="Unique external event identifier for idempotency")
    name = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(required=True)
    city = serializers.CharField(max_length=100, required=True)
    preferred_location = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    investment_capacity = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True, default=Decimal('0.00'))
    property_available = serializers.BooleanField(required=False, default=False)
    business_experience = serializers.BooleanField(required=False, default=False)
    expected_start = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    lead_source = serializers.ChoiceField(choices=LeadSource.choices, required=False, default=LeadSource.TEST)

    def validate_investment_capacity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Investment capacity cannot be negative.")
        return value
