from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction

from users.models import UserRole, User
from users.permissions import IsBrandOwner
from qualification.services import calculate_lead_qualification
from .models import Lead, LeadSequence, ActivityLog, ActivityAction, SalesStatus
from .serializers import (
    LeadListSerializer, LeadDetailSerializer, LeadCreateSerializer,
    FollowUpScheduleSerializer, AssignLeadSerializer, ActivityLogSerializer
)

class LeadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['qualification_status', 'sales_status', 'lead_source', 'assigned_to', 'city', 'follow_up_required']
    search_fields = ['lead_number', 'name', 'phone', 'email', 'city', 'preferred_location']
    ordering_fields = ['created_at', 'investment_capacity', 'qualification_score', 'next_follow_up_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Lead.objects.select_related('brand', 'assigned_to').prefetch_related('activities')

        if user.is_superuser:
            return queryset

        # Strict Brand Scoping
        if user.brand:
            queryset = queryset.filter(brand=user.brand)
        else:
            return Lead.objects.none()

        # Strict Role-Based Data Visibility Scoping
        if user.role == UserRole.SALES_AGENT:
            queryset = queryset.filter(assigned_to=user)
        elif user.role == UserRole.SALES_MANAGER:
            queryset = queryset.filter(brand=user.brand)
        elif user.role == UserRole.BRAND_OWNER:
            queryset = queryset.filter(brand=user.brand)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        elif self.action == 'create':
            return LeadCreateSerializer
        return LeadDetailSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        brand = user.brand
        if not brand and not user.is_superuser:
            return Response({'detail': 'User is not associated with any Brand.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get('phone', '').strip()
        email = serializer.validated_data.get('email', '').strip()

        # Basic Duplicate Detection Foundation within Brand scope
        if phone:
            existing_phone = Lead.objects.filter(brand=brand, phone=phone).first()
            if existing_phone:
                return Response(
                    {'detail': f'A lead with phone number {phone} already exists ({existing_phone.lead_number}).'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            lead_num = LeadSequence.get_next_lead_number(brand)
            lead = serializer.save(brand=brand, lead_number=lead_num)

            # Auto-calculate server-side authoritative qualification
            calculate_lead_qualification(lead, save=True)

            # Log lead creation activity
            ActivityLog.objects.create(
                brand=brand,
                lead=lead,
                actor=user,
                action=ActivityAction.LEAD_CREATED,
                description=f"Lead {lead.lead_number} created by {user.get_full_name()}."
            )

        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        user = self.request.user
        old_instance = self.get_object()
        old_qualification_status = old_instance.qualification_status
        old_sales_status = old_instance.sales_status

        instance = serializer.save()

        # Recalculate qualification server-side if relevant fields updated
        calculate_lead_qualification(instance, save=True)

        # Detect and emit specific granular activity log events
        if old_qualification_status != instance.qualification_status:
            ActivityLog.objects.create(
                brand=instance.brand,
                lead=instance,
                actor=user,
                action=ActivityAction.QUALIFICATION_CHANGED,
                description=f"Qualification status changed from {old_qualification_status} to {instance.qualification_status}."
            )

        if old_sales_status != instance.sales_status:
            action_type = ActivityAction.STATUS_CHANGED
            if instance.sales_status == SalesStatus.CONVERTED:
                action_type = ActivityAction.LEAD_CONVERTED
            elif instance.sales_status == SalesStatus.LOST:
                action_type = ActivityAction.LEAD_LOST

            ActivityLog.objects.create(
                brand=instance.brand,
                lead=instance,
                actor=user,
                action=action_type,
                description=f"Sales status changed from {old_sales_status} to {instance.sales_status}."
            )

        ActivityLog.objects.create(
            brand=instance.brand,
            lead=instance,
            actor=user,
            action=ActivityAction.LEAD_UPDATED,
            description=f"Lead {instance.lead_number} details updated by {user.get_full_name()}."
        )

    def destroy(self, request, *args, **kwargs):
        # Destructive action restricted to Brand Owner
        if not (request.user.role == UserRole.BRAND_OWNER or request.user.is_superuser):
            return Response({'detail': 'Only Brand Owners can delete leads.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='schedule-follow-up')
    def schedule_follow_up(self, request, pk=None):
        lead = self.get_object()
        serializer = FollowUpScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lead.follow_up_required = True
        lead.next_follow_up_at = serializer.validated_data['next_follow_up_at']
        lead.follow_up_type = serializer.validated_data['follow_up_type']
        lead.follow_up_note = serializer.validated_data.get('follow_up_note', '')
        lead.sales_status = SalesStatus.FOLLOW_UP
        lead.save()

        ActivityLog.objects.create(
            brand=lead.brand,
            lead=lead,
            actor=request.user,
            action=ActivityAction.FOLLOW_UP_SCHEDULED,
            description=f"Follow-up ({lead.follow_up_type}) scheduled for {lead.next_follow_up_at.strftime('%Y-%m-%d %H:%M')}."
        )

        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='complete-follow-up')
    def complete_follow_up(self, request, pk=None):
        lead = self.get_object()
        lead.follow_up_required = False
        lead.save(update_fields=['follow_up_required', 'updated_at'])

        ActivityLog.objects.create(
            brand=lead.brand,
            lead=lead,
            actor=request.user,
            action=ActivityAction.FOLLOW_UP_COMPLETED,
            description=f"Follow-up completed by {request.user.get_full_name()}."
        )

        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign_lead(self, request, pk=None):
        lead = self.get_object()
        serializer = AssignLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent_id = serializer.validated_data['assigned_to_id']
        agent = User.objects.filter(id=agent_id, brand=lead.brand).first()
        if not agent:
            return Response({'detail': 'Target user not found in this brand.'}, status=status.HTTP_400_BAD_REQUEST)

        lead.assigned_to = agent
        lead.assigned_at = timezone.now()
        lead.save(update_fields=['assigned_to', 'assigned_at', 'updated_at'])

        ActivityLog.objects.create(
            brand=lead.brand,
            lead=lead,
            actor=request.user,
            action=ActivityAction.LEAD_ASSIGNED,
            description=f"Lead assigned to {agent.get_full_name()} by {request.user.get_full_name()}."
        )

        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_200_OK)
