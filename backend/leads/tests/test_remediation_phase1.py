from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User, UserRole, Brand, Organization
from leads.models import Lead, LeadSequence, QualificationStatus, SalesStatus
from qualification.services import calculate_lead_qualification

class RemediationPhase1TestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Organization
        self.org = Organization.objects.create(name='Remediation Org', slug='remediation-org')

        # Create Brand A and Brand B
        self.brand_a = Brand.objects.create(
            organization=self.org, name='Brand Alpha', slug='brand-alpha', min_investment_threshold=Decimal('1500000.00')
        )
        self.brand_b = Brand.objects.create(
            organization=self.org, name='Brand Beta', slug='brand-beta', min_investment_threshold=Decimal('2000000.00')
        )

        # Create Users
        self.owner_a = User.objects.create_user(
            email='owner.a@alpha.com', password='Password123!', role=UserRole.BRAND_OWNER, brand=self.brand_a
        )
        self.agent_a = User.objects.create_user(
            email='agent.a@alpha.com', password='Password123!', role=UserRole.SALES_AGENT, brand=self.brand_a
        )
        self.owner_b = User.objects.create_user(
            email='owner.b@beta.com', password='Password123!', role=UserRole.BRAND_OWNER, brand=self.brand_b
        )
        self.agent_b = User.objects.create_user(
            email='agent.b@beta.com', password='Password123!', role=UserRole.SALES_AGENT, brand=self.brand_b
        )

    # ------------------------------------------------------------------
    # 1. USER CREATION IDOR SECURITY TESTS
    # ------------------------------------------------------------------
    def test_user_creation_idor_prevention(self):
        """Verify Brand Owner A cannot create a user in Brand B even if supplying Brand B's ID."""
        self.client.force_authenticate(user=self.owner_a)

        payload = {
            'email': 'injected.agent@beta.com',
            'first_name': 'Injected',
            'last_name': 'Agent',
            'password': 'Password123!',
            'role': UserRole.SALES_AGENT,
            'brand': self.brand_b.id  # Malicious payload trying to inject into Brand B
        }

        response = self.client.post('/api/users/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_user = User.objects.get(email='injected.agent@beta.com')
        # Crucial Security Assertion: Must belong to Brand A, NOT Brand B
        self.assertEqual(created_user.brand, self.brand_a)
        self.assertNotEqual(created_user.brand, self.brand_b)

    def test_user_update_cross_brand_prevention(self):
        """Verify Brand Owner A cannot modify Brand B users."""
        self.client.force_authenticate(user=self.owner_a)
        response = self.client.patch(f'/api/users/{self.agent_b.id}/', {'first_name': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.agent_b.refresh_from_db()
        self.assertNotEqual(self.agent_b.first_name, 'Hacked')

    # ------------------------------------------------------------------
    # 2. CONFIGURABLE QUALIFICATION THRESHOLD TESTS
    # ------------------------------------------------------------------
    def test_configurable_brand_qualification_threshold(self):
        """Verify qualification engine respects brand.min_investment_threshold."""
        LeadSequence.objects.create(brand=self.brand_a, next_number=1)

        lead = Lead.objects.create(
            brand=self.brand_a,
            lead_number='LEAD-000100',
            name='Threshold Lead',
            phone='+919876543210',
            email='threshold@example.com',
            city='Kochi',
            preferred_location='Kochi',
            investment_capacity=Decimal('3000000.00'),  # 30 Lakhs
            property_available=True,
            business_experience=True,
            expected_start='3 months',
        )

        # 1. Default threshold (15 Lakhs): 30L >= 15L -> QUALIFIED (Score 100)
        calculate_lead_qualification(lead, save=True)
        self.assertEqual(lead.qualification_status, QualificationStatus.QUALIFIED)

        # 2. Increase threshold to 40 Lakhs (4000000.00): 30L < 40L -> Should be hard disqualified
        self.brand_a.min_investment_threshold = Decimal('4000000.00')
        self.brand_a.save()

        calculate_lead_qualification(lead, save=True)
        self.assertEqual(lead.qualification_status, QualificationStatus.NOT_QUALIFIED)
        self.assertIn('below the minimum threshold', lead.qualification_reason)

        # 3. Lower threshold to 10 Lakhs (1000000.00): 30L >= 10L -> QUALIFIED
        self.brand_a.min_investment_threshold = Decimal('1000000.00')
        self.brand_a.save()

        calculate_lead_qualification(lead, save=True)
        self.assertEqual(lead.qualification_status, QualificationStatus.QUALIFIED)

    # ------------------------------------------------------------------
    # 3. SETTINGS API TESTS
    # ------------------------------------------------------------------
    def test_settings_api_get_and_patch(self):
        """Verify GET and PATCH /api/settings/."""
        # Brand Owner A GET settings
        self.client.force_authenticate(user=self.owner_a)
        res_get = self.client.get('/api/settings/')
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data['name'], 'Brand Alpha')
        self.assertEqual(Decimal(str(res_get.data['min_investment_threshold'])), Decimal('1500000.00'))

        # Brand Owner A PATCH settings
        res_patch = self.client.patch('/api/settings/', {'min_investment_threshold': '2500000.00', 'name': 'Brand Alpha Plus'})
        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(res_patch.data['min_investment_threshold'])), Decimal('2500000.00'))

        self.brand_a.refresh_from_db()
        self.assertEqual(self.brand_a.name, 'Brand Alpha Plus')
        self.assertEqual(self.brand_a.min_investment_threshold, Decimal('2500000.00'))

    def test_settings_api_authorization_and_isolation(self):
        """Verify Sales Agents cannot modify settings and cross-brand isolation holds."""
        # Sales Agent A attempts to PATCH settings -> 403 Forbidden
        self.client.force_authenticate(user=self.agent_a)
        res_agent = self.client.patch('/api/settings/', {'min_investment_threshold': '500000.00'})
        self.assertEqual(res_agent.status_code, status.HTTP_403_FORBIDDEN)

        # Brand Owner B GET settings -> sees Brand B settings (not Brand A)
        self.client.force_authenticate(user=self.owner_b)
        res_b = self.client.get('/api/settings/')
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)
        self.assertEqual(res_b.data['name'], 'Brand Beta')

    # ------------------------------------------------------------------
    # 4. DASHBOARD AGGREGATION TESTS
    # ------------------------------------------------------------------
    def test_owner_dashboard_team_aggregation(self):
        """Verify owner dashboard team performance annotations."""
        self.client.force_authenticate(user=self.owner_a)

        # Create a lead assigned to Agent A
        Lead.objects.create(
            brand=self.brand_a,
            lead_number='LEAD-000200',
            name='Agent Lead',
            phone='+919000000200',
            email='agentlead@example.com',
            city='Kochi',
            investment_capacity=Decimal('3000000.00'),
            sales_status=SalesStatus.CONVERTED,
            qualification_status=QualificationStatus.QUALIFIED,
            assigned_to=self.agent_a
        )

        res = self.client.get('/api/dashboard/owner/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('team_performance', res.data)

        # Find agent_a in team_performance
        agent_perf = next((item for item in res.data['team_performance'] if item['id'] == self.agent_a.id), None)
        self.assertIsNotNone(agent_perf)
        self.assertEqual(agent_perf['assigned_leads'], 1)
        self.assertEqual(agent_perf['qualified_leads'], 1)
        self.assertEqual(agent_perf['converted_leads'], 1)

    # ------------------------------------------------------------------
    # 5. INVESTMENT CAPACITY VALIDATION TESTS
    # ------------------------------------------------------------------
    def test_negative_investment_capacity_rejected(self):
        """Verify negative investment capacity amounts are rejected with HTTP 400 Bad Request."""
        self.client.force_authenticate(user=self.owner_a)

        payload = {
            'name': 'Negative Investment Lead',
            'phone': '+919999000111',
            'email': 'negative@example.com',
            'city': 'Kochi',
            'investment_capacity': '-500000.00',  # Invalid negative capacity
        }

        response = self.client.post('/api/leads/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('investment_capacity', response.data)

    # ------------------------------------------------------------------
    # 6. GRANULAR ACTIVITY LOG EVENT TESTS
    # ------------------------------------------------------------------
    def test_granular_activity_log_events(self):
        """Verify updating lead sales status emits STATUS_CHANGED and LEAD_CONVERTED activity logs."""
        self.client.force_authenticate(user=self.owner_a)

        lead = Lead.objects.create(
            brand=self.brand_a,
            lead_number='LEAD-000300',
            name='Activity Log Lead',
            phone='+919999000222',
            email='activitylog@example.com',
            city='Kochi',
            investment_capacity=Decimal('2500000.00'),
            sales_status=SalesStatus.NEW
        )

        # Update sales status to CONVERTED
        res = self.client.patch(f'/api/leads/{lead.id}/', {'sales_status': SalesStatus.CONVERTED})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        activities = list(lead.activities.values_list('action', flat=True))
        self.assertIn('LEAD_CONVERTED', activities)

