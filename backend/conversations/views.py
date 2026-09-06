from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import UserRole
from leads.models import ActivityLog, ActivityAction
from .models import Conversation, Message, LeadNote
from .serializers import ConversationSerializer, MessageSerializer, LeadNoteSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Conversation.objects.select_related('lead').prefetch_related('messages')

        if user.is_superuser:
            return queryset

        # Scope by brand
        if user.brand:
            queryset = queryset.filter(lead__brand=user.brand)

        # Scope by user role
        if user.role == UserRole.SALES_AGENT:
            queryset = queryset.filter(lead__assigned_to=user)
        elif user.role == UserRole.SALES_MANAGER:
            # Manager sees team leads or unassigned leads
            queryset = queryset.filter(lead__brand=user.brand)

        return queryset

    @action(detail=True, methods=['post'], url_path='messages')
    def add_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(conversation=conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LeadNoteViewSet(viewsets.ModelViewSet):
    serializer_class = LeadNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = LeadNote.objects.select_related('lead', 'author')

        if user.is_superuser:
            return queryset

        if user.brand:
            queryset = queryset.filter(lead__brand=user.brand)

        if user.role == UserRole.SALES_AGENT:
            queryset = queryset.filter(lead__assigned_to=user)

        lead_id = self.request.query_params.get('lead')
        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)

        return queryset

    def perform_create(self, serializer):
        note = serializer.save(author=self.request.user)
        # Log note creation activity
        ActivityLog.objects.create(
            brand=note.lead.brand,
            lead=note.lead,
            actor=self.request.user,
            action=ActivityAction.NOTE_ADDED,
            description=f"Internal note added by {self.request.user.get_full_name()}: {note.content[:50]}"
        )
