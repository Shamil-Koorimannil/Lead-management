from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User, UserRole, Brand, Organization
from leads.models import Lead, LeadSequence, QualificationStatus, ActivityLog, ActivityAction, LeadSource
from qualification.models import QualificationRule, OperatorChoices
from integrations.models import IntegrationToken, IntegrationEvent

class N8nIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Organization & Brands
        self.org = Organization.objects.create(name='Zywo Network', slug='zywo-network')
        self.brand_a = Brand.objects.create(organization=self.org, name='Brand A', slug='brand-a')
        self.brand_b = Brand.objects.create(organization=self.org, name='Brand B', slug='brand-b')

        # Lead Sequences
        LeadSequence.objects.create(brand=self.brand_a, next_number=1)
        LeadSequence.objects.create(brand=self.brand_b, next_number=1)

        # Integration Tokens
        self.token_a = IntegrationToken.objects.create(
            brand=self.brand_a,
            name='n8n Token Brand A',
            key='token_key_brand_a_1234567890',
            is_active=True
        )
        self.token_b = IntegrationToken.objects.create(
            brand=self.brand_b,
            name='n8n Token Brand B',
            key='token_key_brand_b_1234567890',
            is_active=True
        )

        # Standard User
        self.user_a = User.objects.create_user(
            email='user@brand-a.com',
            password='Password123!',
            role=UserRole.SALES_AGENT,
            brand=self.brand_a
        )

        # Set up full qualification rules for Brand A
        QualificationRule.objects.create(
            brand=self.brand_a,
            name='Investment >= 25L',
            field='investment_capacity',
            operator=OperatorChoices.GTE,
            value='2500000',
            score=30,
            priority=1,
            active=True
        )
        QualificationRule.objects.create(
            brand=self.brand_a,
            name='Preferred Location Available',
            field='preferred_location',
            operator=OperatorChoices.IS_TRUE,
            value='',
            score=20,
            priority=2,
            active=True
        )
        QualificationRule.objects.create(
            brand=self.brand_a,
            name='Property Available',
            field='property_available',
            operator=OperatorChoices.IS_TRUE,
            value='',
            score=20,
            priority=3,
            active=True
        )
        QualificationRule.objects.create(
            brand=self.brand_a,
            name='Business Experience Present',
            field='business_experience',
            operator=OperatorChoices.IS_TRUE,
            value='',
            score=10,
            priority=4,
            active=True
        )
        QualificationRule.objects.create(
            brand=self.brand_a,
            name='Expected Start within 6 months',
            field='expected_start',
            operator=OperatorChoices.CONTAINS,
            value='month',
            score=20,
            priority=5,
            active=True
        )

        self.valid_payload = {
            "name": "Ahmed Test",
            "phone": "+919999999001",
            "email": "ahmed.test@example.com",
            "city": "Kochi",
            "preferred_location": "Kochi",
            "investment_capacity": 5000000,
            "property_available": True,
            "business_experience": True,
            "expected_start": "3 months",
            "lead_source": "TEST",
            "external_event_id": "evt_test_unique_001"
        }

    def test_01_valid_n8n_authentication_succeeds(self):
        """1. Valid n8n authentication succeeds."""
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Ahmed Test")

    def test_02_missing_integration_credential_fails(self):
        """2. Missing integration credential fails."""
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json'
        )
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_03_invalid_integration_credential_fails(self):
        """3. Invalid integration credential fails."""
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY='invalid_bogus_key'
        )
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_04_normal_user_jwt_cannot_access_integration_endpoint_without_key(self):
        """4. Normal user JWT cannot use the integration-only endpoint unless key provided."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json'
        )
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


    def test_05_integration_cannot_access_another_brand(self):
        """5. Integration cannot access another Brand (token_a creates under Brand A only)."""
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        lead = Lead.objects.get(id=response.data['id'])
        self.assertEqual(lead.brand, self.brand_a)
        self.assertNotEqual(lead.brand, self.brand_b)

    def test_06_arbitrary_brand_id_in_payload_cannot_bypass_brand_isolation(self):
        """6. Arbitrary brand_id cannot bypass Brand isolation."""
        tampered_payload = self.valid_payload.copy()
        tampered_payload['brand_id'] = str(self.brand_b.id)

        response = self.client.post(
            '/api/integrations/v1/leads/',
            tampered_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        lead = Lead.objects.get(id=response.data['id'])
        self.assertEqual(lead.brand, self.brand_a)

    def test_07_invalid_payload_fails_validation(self):
        """7. Invalid payload fails validation (e.g. negative investment)."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['investment_capacity'] = -50000

        response = self.client.post(
            '/api/integrations/v1/leads/',
            invalid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_08_duplicate_external_event_id_does_not_create_duplicate_lead(self):
        """8. Duplicate external event ID does not create duplicate Lead."""
        res1 = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('X-Idempotent-Replay'), 'true')
        self.assertTrue(res2.data.get('is_duplicate'))

        # DB verification: Only 1 lead created
        self.assertEqual(Lead.objects.filter(brand=self.brand_a, phone="+919999999001").count(), 1)

    def test_09_concurrent_duplicate_requests_remain_idempotent(self):
        """9. Duplicate requests with same event ID remain idempotent in DB constraint."""
        self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )

        event_count = IntegrationEvent.objects.filter(
            brand=self.brand_a,
            external_event_id="evt_test_unique_001"
        ).count()
        self.assertEqual(event_count, 1)

    def test_10_lead_is_correctly_qualified_by_django(self):
        """10. Lead is correctly qualified by Django server authority."""
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        lead = Lead.objects.get(id=response.data['id'])
        self.assertEqual(lead.qualification_status, QualificationStatus.QUALIFIED)
        self.assertGreater(lead.qualification_score, 0)

    def test_11_activity_log_is_created_correctly(self):
        """11. ActivityLog is created correctly."""
        response = self.client.post(
            '/api/integrations/v1/leads/',
            self.valid_payload,
            format='json',
            HTTP_X_INTEGRATION_API_KEY=self.token_a.key
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        lead_id = response.data['id']
        activity = ActivityLog.objects.filter(lead_id=lead_id, action=ActivityAction.LEAD_CREATED).first()
        self.assertIsNotNone(activity)
        self.assertIsNone(activity.actor)
        self.assertIn("n8n integration workflow", activity.description)
