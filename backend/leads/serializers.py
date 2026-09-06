from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Lead, ActivityLog, LeadSource, SalesStatus, QualificationStatus, FollowUpType

class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'lead', 'actor', 'actor_name', 'action', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class LeadListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'lead_number', 'name', 'phone', 'email', 'city', 'preferred_location',
            'investment_capacity', 'qualification_score', 'qualification_status',
            'sales_status', 'lead_source', 'assigned_to', 'assigned_to_name',
            'follow_up_required', 'next_follow_up_at', 'follow_up_type',
            'created_at', 'updated_at'
        ]

class LeadDetailSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    activities = ActivityLogSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'brand', 'lead_number', 'name', 'phone', 'email', 'city',
            'preferred_location', 'investment_capacity', 'property_available',
            'business_experience', 'expected_start', 'lead_source',
            'qualification_score', 'qualification_status', 'qualification_reason',
            'follow_up_required', 'next_follow_up_at', 'follow_up_type', 'follow_up_note',
            'sales_status', 'assigned_to', 'assigned_to_detail', 'assigned_at',
            'activities', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'lead_number', 'qualification_score', 'qualification_status',
            'qualification_reason', 'assigned_at', 'created_at', 'updated_at'
        ]

    def validate_investment_capacity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Investment capacity cannot be negative.")
        return value

class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'id', 'brand', 'name', 'phone', 'email', 'city', 'preferred_location',
            'investment_capacity', 'property_available', 'business_experience',
            'expected_start', 'lead_source', 'sales_status', 'assigned_to',
            'follow_up_required', 'next_follow_up_at', 'follow_up_type', 'follow_up_note'
        ]
        read_only_fields = ['id', 'brand']

    def validate_investment_capacity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Investment capacity cannot be negative.")
        return value

class FollowUpScheduleSerializer(serializers.Serializer):
    next_follow_up_at = serializers.DateTimeField(required=True)
    follow_up_type = serializers.ChoiceField(choices=FollowUpType.choices, required=True)
    follow_up_note = serializers.CharField(required=False, allow_blank=True, default='')

class AssignLeadSerializer(serializers.Serializer):
    assigned_to_id = serializers.IntegerField(required=True)
