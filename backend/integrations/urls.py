from django.urls import path
from .views import IntegrationsPlaceholderView

urlpatterns = [
    path('', IntegrationsPlaceholderView.as_view(), name='integrations-placeholder'),
]
