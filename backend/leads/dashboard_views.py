from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from users.models import UserRole, User
from users.permissions import IsBrandOwner, IsSalesManagerOrOwner
from .models import Lead, QualificationStatus, SalesStatus
from .serializers import LeadListSerializer

class OwnerDashboardView(APIView):
    permission_classes = [IsSalesManagerOrOwner]

    def get(self, request):
        user = request.user
        brand = user.brand

        if not brand and not user.is_superuser:
            return Response({'detail': 'User not associated with a Brand.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Lead.objects.all() if user.is_superuser else Lead.objects.filter(brand=brand)

        total_leads = queryset.count()
        qualified_count = queryset.filter(qualification_status=QualificationStatus.QUALIFIED).count()
        review_count = queryset.filter(qualification_status=QualificationStatus.REVIEW).count()
        not_qualified_count = queryset.filter(qualification_status=QualificationStatus.NOT_QUALIFIED).count()
        converted_count = queryset.filter(sales_status=SalesStatus.CONVERTED).count()
        lost_count = queryset.filter(sales_status=SalesStatus.LOST).count()
        active_followups = queryset.filter(follow_up_required=True).count()

        conversion_rate = round((converted_count / total_leads * 100), 1) if total_leads > 0 else 0.0
        avg_qualification_score = round(queryset.aggregate(Avg('qualification_score'))['qualification_score__avg'] or 0, 1)

        # Breakdown by Sales Status (Funnel)
        sales_funnel = list(queryset.values('sales_status').annotate(count=Count('id')).order_by('sales_status'))

        # Breakdown by Lead Source
        lead_sources = list(queryset.values('lead_source').annotate(count=Count('id')).order_by('lead_source'))

        # Breakdown by Location
        locations = list(queryset.values('city').annotate(count=Count('id')).order_by('-count')[:5])

        # Team Performance (Optimized using DB Annotations to eliminate N+1 queries)
        team_users = User.objects.filter(brand=brand) if brand else User.objects.all()
        team_users = team_users.annotate(
            assigned_leads_count=Count('assigned_leads'),
            qualified_leads_count=Count('assigned_leads', filter=Q(assigned_leads__qualification_status=QualificationStatus.QUALIFIED)),
            converted_leads_count=Count('assigned_leads', filter=Q(assigned_leads__sales_status=SalesStatus.CONVERTED))
        )
        team_performance = [
            {
                'id': agent.id,
                'name': agent.get_full_name(),
                'email': agent.email,
                'role': agent.role,
                'assigned_leads': agent.assigned_leads_count,
                'qualified_leads': agent.qualified_leads_count,
                'converted_leads': agent.converted_leads_count,
            }
            for agent in team_users
        ]

        data = {
            'total_leads': total_leads,
            'qualified': qualified_count,
            'review': review_count,
            'not_qualified': not_qualified_count,
            'conversion_rate': conversion_rate,
            'avg_qualification_score': avg_qualification_score,
            'active_followups': active_followups,
            'converted': converted_count,
            'lost': lost_count,
            'sales_funnel': sales_funnel,
            'lead_sources': lead_sources,
            'locations': locations,
            'team_performance': team_performance,
        }

        return Response(data, status=status.HTTP_200_OK)

class SalesDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # Scope based on role
        if user.is_superuser:
            queryset = Lead.objects.all()
        elif user.role == UserRole.SALES_AGENT:
            queryset = Lead.objects.filter(assigned_to=user)
        else:
            # Sales Manager or Brand Owner sees brand-wide operational leads
            queryset = Lead.objects.filter(brand=user.brand) if user.brand else Lead.objects.none()

        new_leads = queryset.filter(sales_status=SalesStatus.NEW).count()
        qualified_leads = queryset.filter(qualification_status=QualificationStatus.QUALIFIED).count()
        followups_due = queryset.filter(follow_up_required=True, next_follow_up_at__lte=now + timedelta(days=1)).count()
        meetings_today = queryset.filter(sales_status=SalesStatus.MEETING).count()
        priority_leads_count = queryset.filter(
            qualification_status=QualificationStatus.QUALIFIED
        ).exclude(sales_status__in=[SalesStatus.CONVERTED, SalesStatus.LOST]).count()

        # Specific Lead lists for action dashboard
        overdue_followups = queryset.filter(
            follow_up_required=True, next_follow_up_at__lt=now
        ).order_by('next_follow_up_at')[:10]

        upcoming_followups = queryset.filter(
            follow_up_required=True, next_follow_up_at__gte=now
        ).order_by('next_follow_up_at')[:10]

        recently_qualified = queryset.filter(
            qualification_status=QualificationStatus.QUALIFIED
        ).order_by('-created_at')[:10]

        data = {
            'metrics': {
                'new_leads': new_leads,
                'qualified_leads': qualified_leads,
                'followups_due': followups_due,
                'meetings_today': meetings_today,
                'priority_leads': priority_leads_count,
            },
            'overdue_followups': LeadListSerializer(overdue_followups, many=True).data,
            'upcoming_followups': LeadListSerializer(upcoming_followups, many=True).data,
            'recently_qualified': LeadListSerializer(recently_qualified, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)
