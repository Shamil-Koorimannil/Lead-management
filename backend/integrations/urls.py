from django.urls import path
from .views import IntegrationLeadCreateView, InstagramProcessMessageView

urlpatterns = [
    path('v1/leads/', IntegrationLeadCreateView.as_view(), name='integration-lead-create'),
    path('v1/instagram/process-message/', InstagramProcessMessageView.as_view(), name='integration-instagram-process-message'),
]


