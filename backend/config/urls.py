from django.contrib import admin
from django.urls import path, include
from users.views import SettingsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/conversations/', include('conversations.urls')),
    path('api/qualification/', include('qualification.urls')),
    path('api/dashboard/', include('leads.dashboard_urls')),
    path('api/users/', include('users.management_urls')),
    path('api/settings/', SettingsView.as_view(), name='settings'),
]
