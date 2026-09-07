from django.urls import path
from .views import IntegrationLeadCreateView

urlpatterns = [
    path('v1/leads/', IntegrationLeadCreateView.as_view(), name='integration-lead-create'),
]

