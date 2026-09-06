from django.urls import path
from .dashboard_views import OwnerDashboardView, SalesDashboardView

urlpatterns = [
    path('owner/', OwnerDashboardView.as_view(), name='dashboard-owner'),
    path('sales/', SalesDashboardView.as_view(), name='dashboard-sales'),
]
