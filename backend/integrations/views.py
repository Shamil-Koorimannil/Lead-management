from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction

from leads.models import Lead, LeadSequence, ActivityLog, ActivityAction, LeadSource
from leads.serializers import LeadDetailSerializer
from qualification.services import calculate_lead_qualification

from .models import IntegrationEvent
from .authentication import IntegrationTokenAuthentication
from .permissions import HasValidIntegrationToken
from .serializers import IntegrationLeadCreateSerializer

class IntegrationLeadCreateView(APIView):
    """
    Dedicated Machine-to-Machine Endpoint for n8n Integration Workflows.
    Creates or returns idempotent leads scoped strictly to the authenticated Brand.
    """
    authentication_classes = [IntegrationTokenAuthentication]
    permission_classes = [HasValidIntegrationToken]

    def post(self, request):
        serializer = IntegrationLeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        brand = request.user.brand
        external_event_id = serializer.validated_data['external_event_id'].strip()

        with transaction.atomic():
            # 1. Idempotency Check: Query DB for existing event ID under this brand
            existing_event = IntegrationEvent.objects.filter(brand=brand, external_event_id=external_event_id).first()
            if existing_event and existing_event.lead:
                response_data = LeadDetailSerializer(existing_event.lead).data
                response_data['is_duplicate'] = True
                return Response(response_data, status=status.HTTP_200_OK, headers={'X-Idempotent-Replay': 'true'})

            phone = serializer.validated_data['phone'].strip()
            existing_lead = Lead.objects.filter(brand=brand, phone=phone).first()

            if existing_lead:
                # Link existing lead to this integration event
                IntegrationEvent.objects.create(
                    brand=brand,
                    external_event_id=external_event_id,
                    lead=existing_lead,
                    source='N8N',
                    payload=request.data
                )
                response_data = LeadDetailSerializer(existing_lead).data
                response_data['is_duplicate'] = True
                return Response(response_data, status=status.HTTP_200_OK, headers={'X-Idempotent-Replay': 'true'})

            # 2. Atomic Lead Number Generation & Creation
            lead_num = LeadSequence.get_next_lead_number(brand)

            lead = Lead.objects.create(
                brand=brand,
                lead_number=lead_num,
                name=serializer.validated_data['name'].strip(),
                phone=phone,
                email=serializer.validated_data['email'].strip(),
                city=serializer.validated_data['city'].strip(),
                preferred_location=serializer.validated_data.get('preferred_location', '').strip(),
                investment_capacity=serializer.validated_data.get('investment_capacity'),
                property_available=serializer.validated_data.get('property_available', False),
                business_experience=serializer.validated_data.get('business_experience', False),
                expected_start=serializer.validated_data.get('expected_start', '').strip(),
                lead_source=serializer.validated_data.get('lead_source', LeadSource.TEST)
            )

            # 3. Server-Side Qualification Authority Calculation
            calculate_lead_qualification(lead, save=True)

            # 4. Create Integration Event record
            IntegrationEvent.objects.create(
                brand=brand,
                external_event_id=external_event_id,
                lead=lead,
                source='N8N',
                payload=request.data
            )

            # 5. Activity Log Creation
            ActivityLog.objects.create(
                brand=brand,
                lead=lead,
                actor=None,
                action=ActivityAction.LEAD_CREATED,
                description=f"Lead {lead.lead_number} created via n8n integration workflow (Event ID: {external_event_id})."
            )

        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_201_CREATED)
