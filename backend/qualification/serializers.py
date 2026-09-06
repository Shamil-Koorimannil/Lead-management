from rest_framework import serializers
from .models import QualificationRule, OperatorChoices

class QualificationRuleSerializer(serializers.ModelSerializer):
    operator_display = serializers.CharField(source='get_operator_display', read_only=True)

    class Meta:
        model = QualificationRule
        fields = [
            'id', 'brand', 'name', 'field', 'operator', 'operator_display',
            'value', 'score', 'active', 'priority', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
