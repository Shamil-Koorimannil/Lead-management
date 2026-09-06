from rest_framework import viewsets
from users.permissions import CanManageQualificationRules
from .models import QualificationRule
from .serializers import QualificationRuleSerializer

class QualificationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = QualificationRuleSerializer
    permission_classes = [CanManageQualificationRules]

    def get_queryset(self):
        user = self.request.user
        queryset = QualificationRule.objects.all()
        if user.brand and not user.is_superuser:
            queryset = queryset.filter(brand=user.brand)
        return queryset.order_by('priority', 'id')

    def perform_create(self, serializer):
        user = self.request.user
        brand = serializer.validated_data.get('brand') or user.brand
        serializer.save(brand=brand)
