from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QualificationRuleViewSet

router = DefaultRouter()
router.register(r'rules', QualificationRuleViewSet, basename='qualification-rules')

urlpatterns = [
    path('', include(router.urls)),
]
