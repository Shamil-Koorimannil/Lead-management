from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.models import Organization, Brand, User, UserRole
from leads.models import (
    Lead, LeadSource, QualificationStatus, LeadTemperature, CurrentProfession, OpeningTimeline, ActivityLog
)
from conversations.models import Conversation, ConversationState, InstagramContact, Message
from integrations.models import IntegrationToken, IntegrationEvent

class InstagramAutomationTestCase(TestCase):

    def setUp(self):
        self.org = Organization.objects.create(name="CoolCane Corp", slug="coolcane-corp")
        self.brand = Brand.objects.create(
            organization=self.org,
            name="CoolCane India",
            slug="coolcane-india",
            min_investment_threshold=Decimal('1000000.00')
        )
        self.token = IntegrationToken.objects.create(
            brand=self.brand,
            name="n8n Test Client",
            key="n8n_sec_test_token_1234567890"
        )
        self.client = APIClient()
        self.client.credentials(HTTP_X_INTEGRATION_API_KEY=self.token.key)

    def test_01_investment_below_10_lakh_disqualifies_lead_immediately(self):
        """TEST 1: Investment ₹8 lakh -> DISQUALIFIED immediately, no further questions asked."""
        payload = {
            "external_event_id": "evt_test_01",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": "ig_user_111",
            "username": "rahul_investor",
            "display_name": "Rahul Sharma",
            "message_text": "8 lakh",
            "external_message_id": "msg_001"
        }
        res = self.client.post('/api/integrations/v1/instagram/process-message/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()

        self.assertIn("minimum investment of ₹10 lakh", data['reply_text'])
        self.assertEqual(data['lead_temperature'], LeadTemperature.DISQUALIFIED)
        self.assertEqual(data['qualification_status'], QualificationStatus.NOT_QUALIFIED)
        self.assertEqual(data['state'], ConversationState.DISQUALIFIED)

        lead = Lead.objects.get(id=data['lead_id'])
        self.assertEqual(lead.lead_temperature, LeadTemperature.DISQUALIFIED)
        self.assertEqual(lead.qualification_status, QualificationStatus.NOT_QUALIFIED)

        # Ensure no further qualification questions are sent if user sends another DM
        payload_2 = {
            "external_event_id": "evt_test_01_b",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": "ig_user_111",
            "username": "rahul_investor",
            "message_text": "What is the next step?",
            "external_message_id": "msg_002"
        }
        res_2 = self.client.post('/api/integrations/v1/instagram/process-message/', payload_2, format='json')
        self.assertEqual(res_2.json()['reply_text'], '')

    def test_02_hot_classification_scenario(self):
        """TEST 2: Investment ₹10 lakh, Business, 3 yrs, Kochi, < 2 mos -> Temperature: HOT."""
        user_id = "ig_user_222"
        acc_id = "ig_acc_coolcane_01"

        # Step 1: Inbound DM with exact ₹10 lakh
        p1 = {
            "external_event_id": "evt_02_1", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "username": "kochi_biz",
            "message_text": "₹10 lakh", "external_message_id": "m1"
        }
        r1 = self.client.post('/api/integrations/v1/instagram/process-message/', p1, format='json').json()
        self.assertEqual(r1['state'], ConversationState.WAITING_PROFESSION)

        # Step 2: Profession -> Business owner
        p2 = {
            "external_event_id": "evt_02_2", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Business owner", "external_message_id": "m2"
        }
        r2 = self.client.post('/api/integrations/v1/instagram/process-message/', p2, format='json').json()
        self.assertEqual(r2['state'], ConversationState.WAITING_BUSINESS_DURATION)

        # Step 3: Business duration -> 3 years
        p3 = {
            "external_event_id": "evt_02_3", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "3 years", "external_message_id": "m3"
        }
        r3 = self.client.post('/api/integrations/v1/instagram/process-message/', p3, format='json').json()
        self.assertEqual(r3['state'], ConversationState.WAITING_LOCATION)

        # Step 4: Location -> Kochi
        p4 = {
            "external_event_id": "evt_02_4", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Kochi", "external_message_id": "m4"
        }
        r4 = self.client.post('/api/integrations/v1/instagram/process-message/', p4, format='json').json()
        self.assertEqual(r4['state'], ConversationState.WAITING_OPENING_TIMELINE)

        # Step 5: Opening timeline -> Within 2 months
        p5 = {
            "external_event_id": "evt_02_5", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Within 2 months", "external_message_id": "m5"
        }
        r5 = self.client.post('/api/integrations/v1/instagram/process-message/', p5, format='json').json()
        self.assertEqual(r5['state'], ConversationState.QUALIFIED)
        self.assertEqual(r5['lead_temperature'], LeadTemperature.HOT)

        lead = Lead.objects.get(id=r5['lead_id'])
        self.assertEqual(lead.lead_temperature, LeadTemperature.HOT)
        self.assertTrue(lead.follow_up_required)
        self.assertEqual(lead.preferred_location, "Kochi")

    def test_03_warm_classification_scenario(self):
        """TEST 3: Investment ₹15L, Salaried, Prev business: Yes, Blr, < 6 mos -> Temperature: WARM."""
        user_id = "ig_user_333"
        acc_id = "ig_acc_coolcane_01"

        # 1. Investment 15L
        r1 = self.client.post('/api/integrations/v1/instagram/process-message/', {
            "external_event_id": "evt_03_1", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "15 lakh", "external_message_id": "m1"
        }, format='json').json()

        # 2. Profession Salaried
        r2 = self.client.post('/api/integrations/v1/instagram/process-message/', {
            "external_event_id": "evt_03_2", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Salaried job", "external_message_id": "m2"
        }, format='json').json()
        self.assertEqual(r2['state'], ConversationState.WAITING_PREVIOUS_EXPERIENCE)

        # 3. Previous business exp -> Yes
        r3 = self.client.post('/api/integrations/v1/instagram/process-message/', {
            "external_event_id": "evt_03_3", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Yes I previously ran a store", "external_message_id": "m3"
        }, format='json').json()

        # 4. Location -> Bangalore
        r4 = self.client.post('/api/integrations/v1/instagram/process-message/', {
            "external_event_id": "evt_03_4", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Bangalore", "external_message_id": "m4"
        }, format='json').json()

        # 5. Timeline -> Within 6 months
        r5 = self.client.post('/api/integrations/v1/instagram/process-message/', {
            "external_event_id": "evt_03_5", "instagram_account_id": acc_id,
            "instagram_user_id": user_id, "message_text": "Within 6 months", "external_message_id": "m5"
        }, format='json').json()

        self.assertEqual(r5['lead_temperature'], LeadTemperature.WARM)
        lead = Lead.objects.get(id=r5['lead_id'])
        self.assertEqual(lead.lead_temperature, LeadTemperature.WARM)
        self.assertTrue(lead.previous_business_experience)

    def test_04_cold_classification_scenario(self):
        """TEST 4: Investment ₹20L, Business, 5 yrs, Hyd, < 1 yr -> Temperature: COLD."""
        user_id = "ig_user_444"
        acc_id = "ig_acc_coolcane_01"

        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e4_1", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "20 lakh", "external_message_id": "m1"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e4_2", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Business", "external_message_id": "m2"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e4_3", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "5 years", "external_message_id": "m3"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e4_4", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Hyderabad", "external_message_id": "m4"}, format='json')
        r5 = self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e4_5", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Within 1 year", "external_message_id": "m5"}, format='json').json()

        self.assertEqual(r5['lead_temperature'], LeadTemperature.COLD)

    def test_05_long_term_classification_scenario(self):
        """TEST 5: Investment ₹30L, Business, 10 yrs, Mumbai, > 1 yr -> Temperature: LONG_TERM."""
        user_id = "ig_user_555"
        acc_id = "ig_acc_coolcane_01"

        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e5_1", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "30 lakh", "external_message_id": "m1"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e5_2", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Business", "external_message_id": "m2"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e5_3", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "10 years", "external_message_id": "m3"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e5_4", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Mumbai", "external_message_id": "m4"}, format='json')
        r5 = self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e5_5", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "More than 1 year", "external_message_id": "m5"}, format='json').json()

        self.assertEqual(r5['lead_temperature'], LeadTemperature.LONG_TERM)

    def test_06_idempotent_duplicate_event_handling(self):
        """TEST 6: Same event sent twice -> Idempotent replay, only 1 message created."""
        payload = {
            "external_event_id": "evt_dup_999",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": "ig_user_dup",
            "message_text": "15 lakh",
            "external_message_id": "msg_dup_111"
        }
        res1 = self.client.post('/api/integrations/v1/instagram/process-message/', payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Retry exact same webhook payload
        res2 = self.client.post('/api/integrations/v1/instagram/process-message/', payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertTrue(res2.json()['is_duplicate'])

        # Verify only 1 IntegrationEvent and 1 inbound message was created
        events_count = IntegrationEvent.objects.filter(brand=self.brand, external_event_id="evt_dup_999").count()
        self.assertEqual(events_count, 1)

    def test_07_multiple_messages_in_same_conversation(self):
        """TEST 7: Same Instagram user sends multiple messages -> Single conversation maintained."""
        user_id = "ig_user_777"
        acc_id = "ig_acc_coolcane_01"

        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e7_1", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Hi", "external_message_id": "m1"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e7_2", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "10 lakh", "external_message_id": "m2"}, format='json')

        contact = InstagramContact.objects.get(brand=self.brand, instagram_user_id=user_id)
        conv_count = Conversation.objects.filter(instagram_contact=contact).count()
        self.assertEqual(conv_count, 1)

    def test_08_existing_instagram_lead_updates_without_creating_duplicate(self):
        """TEST 8: Existing Instagram lead sending another DM -> Lead updated, no duplicate created."""
        user_id = "ig_user_888"
        acc_id = "ig_acc_coolcane_01"

        r1 = self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e8_1", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "12 lakh", "external_message_id": "m1"}, format='json').json()
        lead_id = r1['lead_id']

        r2 = self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e8_2", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Salaried", "external_message_id": "m2"}, format='json').json()

        self.assertEqual(r2['lead_id'], lead_id)
        leads_count = Lead.objects.filter(brand=self.brand, phone=f"IG:{user_id}").count()
        self.assertEqual(leads_count, 1)
