from rest_framework import serializers
from .models import Conversation, Message, LeadNote

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'direction', 'message', 'message_type', 'external_message_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    lead_number = serializers.CharField(source='lead.lead_number', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'lead', 'lead_number', 'channel', 'status', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class LeadNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = LeadNote
        fields = ['id', 'lead', 'author', 'author_name', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
