from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, LeadNoteViewSet

router = DefaultRouter()
router.register(r'notes', LeadNoteViewSet, basename='lead-notes')
router.register(r'', ConversationViewSet, basename='conversations')

urlpatterns = [
    path('', include(router.urls)),
]
