from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User, UserRole, Brand, Organization
from leads.models import Lead, LeadSequence, QualificationStatus, SalesStatus, LeadSource
from qualification.services import calculate_lead_qualification

class QualificationAndPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Brand A
        self.org = Organization.objects.create(name='Org A', slug='org-a')
        self.brand_a = Brand.objects.create(organization=self.org, name='Brand A', slug='brand-a')

        # Create Brand B for cross-brand isolation testing
        self.brand_b = Brand.objects.create(organization=self.org, name='Brand B', slug='brand-b')

        # Users
        self.owner = User.objects.create_user(
            email='owner@brand-a.com', password='Pass123!', role=UserRole.BRAND_OWNER, brand=self.brand_a
        )
        self.agent1 = User.objects.create_user(
            email='agent1@brand-a.com', password='Pass123!', role=UserRole.SALES_AGENT, brand=self.brand_a
        )
        self.agent2 = User.objects.create_user(
            email='agent2@brand-a.com', password='Pass123!', role=UserRole.SALES_AGENT, brand=self.brand_a
        )
        self.brand_b_user = User.objects.create_user(
            email='user@brand-b.com', password='Pass123!', role=UserRole.BRAND_OWNER, brand=self.brand_b
        )

        # Create leads for Agent 1 and Agent 2
        LeadSequence.objects.create(brand=self.brand_a, next_number=1)

        self.lead_agent1 = Lead.objects.create(
            brand=self.brand_a,
            lead_number='LEAD-000001',
            name='Lead 1',
            phone='+919000000001',
            email='lead1@example.com',
            city='Kochi',
            preferred_location='Kochi',
            investment_capacity=Decimal('5000000'),
            property_available=True,
            business_experience=True,
            expected_start='3 months',
            assigned_to=self.agent1,
        )
        calculate_lead_qualification(self.lead_agent1, save=True)

        self.lead_agent2 = Lead.objects.create(
            brand=self.brand_a,
            lead_number='LEAD-000002',
            name='Lead 2',
            phone='+919000000002',
            email='lead2@example.com',
            city='Kochi',
            preferred_location='Kochi',
            investment_capacity=Decimal('1000000'), # Hard disqualified (< ₹15L)
            property_available=False,
            business_experience=False,
            expected_start='2 years',
            assigned_to=self.agent2,
        )
        calculate_lead_qualification(self.lead_agent2, save=True)

    def test_qualification_score_and_hard_disqualifier(self):
        # TEST-001 equivalent -> 100 Score, QUALIFIED
        self.assertEqual(self.lead_agent1.qualification_status, QualificationStatus.QUALIFIED)
        self.assertEqual(self.lead_agent1.qualification_score, 100)

        # TEST-002 equivalent -> Hard Disqualified, NOT_QUALIFIED
        self.assertEqual(self.lead_agent2.qualification_status, QualificationStatus.NOT_QUALIFIED)
        self.assertIn('below the minimum threshold', self.lead_agent2.qualification_reason)

    def test_brand_owner_access(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/leads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_sales_agent_isolation(self):
        # Agent 1 should only see lead 1
        self.client.force_authenticate(user=self.agent1)
        response = self.client.get('/api/leads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.lead_agent1.id)

        # Agent 1 attempting to access Lead 2 of Agent 2 must be rejected with 404
        response_detail = self.client.get(f'/api/leads/{self.lead_agent2.id}/')
        self.assertEqual(response_detail.status_code, status.HTTP_404_NOT_FOUND)

    def test_sales_agent_cannot_manage_users(self):
        self.client.force_authenticate(user=self.agent1)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_brand_isolation(self):
        self.client.force_authenticate(user=self.brand_b_user)
        response = self.client.get('/api/leads/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        response_detail = self.client.get(f'/api/leads/{self.lead_agent1.id}/')
        self.assertEqual(response_detail.status_code, status.HTTP_404_NOT_FOUND)
