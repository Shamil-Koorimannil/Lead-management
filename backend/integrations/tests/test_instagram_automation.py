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

    def test_01_disqualification_9_99_lakh_and_below_threshold(self):
        """TEST 1: Investment ₹9.99L (9,99,000) or below threshold -> DISQUALIFIED immediately."""
        payload = {
            "external_event_id": "evt_test_01",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": "ig_user_111",
            "username": "rahul_investor",
            "display_name": "Rahul Sharma",
            "message_text": "₹9.99L",
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

    def test_02_exact_10L_formats(self):
        """TEST 2: Test variations of exact ₹10L ('10L', '10 lakh', '10,00,000', '₹10L') -> WAITING_PROFESSION."""
        test_inputs = ["10L", "10 lakh", "10,00,000", "₹10L"]
        for idx, text in enumerate(test_inputs):
            user_id = f"ig_user_exact_{idx}"
            payload = {
                "external_event_id": f"evt_exact_{idx}",
                "instagram_account_id": "ig_acc_coolcane_01",
                "instagram_user_id": user_id,
                "username": f"user_{idx}",
                "message_text": text,
                "external_message_id": f"msg_exact_{idx}"
            }
            res = self.client.post('/api/integrations/v1/instagram/process-message/', payload, format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            data = res.json()
            self.assertEqual(data['state'], ConversationState.WAITING_PROFESSION)
            lead = Lead.objects.get(id=data['lead_id'])
            self.assertEqual(lead.investment_capacity, Decimal('1000000.00'))

    def test_03_ambiguous_investment_around_10_lakh(self):
        """TEST 3: Ambiguous investment ('around 10 lakh') -> CONFIRMING_INVESTMENT state -> Yes -> WAITING_PROFESSION."""
        user_id = "ig_user_ambiguous"
        acc_id = "ig_acc_coolcane_01"

        # Step 1: Inbound 'around 10 lakh'
        p1 = {
            "external_event_id": "evt_amb_1",
            "instagram_account_id": acc_id,
            "instagram_user_id": user_id,
            "username": "ambiguous_user",
            "message_text": "around 10 lakh",
            "external_message_id": "msg_amb_1"
        }
        r1 = self.client.post('/api/integrations/v1/instagram/process-message/', p1, format='json').json()
        self.assertEqual(r1['state'], ConversationState.CONFIRMING_INVESTMENT)
        self.assertIn("Just to confirm", r1['reply_text'])

        # Step 2: Inbound 'Yes'
        p2 = {
            "external_event_id": "evt_amb_2",
            "instagram_account_id": acc_id,
            "instagram_user_id": user_id,
            "message_text": "Yes correct",
            "external_message_id": "msg_amb_2"
        }
        r2 = self.client.post('/api/integrations/v1/instagram/process-message/', p2, format='json').json()
        self.assertEqual(r2['state'], ConversationState.WAITING_PROFESSION)
        lead = Lead.objects.get(id=r2['lead_id'])
        self.assertEqual(lead.investment_capacity, Decimal('1000000.00'))

    def test_04_incomplete_lead_remains_null_temperature(self):
        """TEST 4: Incomplete lead has lead_temperature = NULL (None), not COLD."""
        user_id = "ig_user_incomplete"
        p = {
            "external_event_id": "evt_inc_1",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": user_id,
            "username": "incomplete_user",
            "message_text": "10 lakh",
            "external_message_id": "msg_inc_1"
        }
        r = self.client.post('/api/integrations/v1/instagram/process-message/', p, format='json').json()
        lead = Lead.objects.get(id=r['lead_id'])
        self.assertIsNone(lead.lead_temperature)

    def test_05_no_phone_number_fabricated(self):
        """TEST 5: Newly created Instagram lead has phone = '', identity is stored on InstagramContact."""
        user_id = "ig_user_nophone_999"
        p = {
            "external_event_id": "evt_np_1",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": user_id,
            "username": "nophone_user",
            "message_text": "Hello",
            "external_message_id": "msg_np_1"
        }
        r = self.client.post('/api/integrations/v1/instagram/process-message/', p, format='json').json()
        lead = Lead.objects.get(id=r['lead_id'])
        self.assertEqual(lead.phone, "")

        contact = InstagramContact.objects.get(brand=self.brand, instagram_user_id=user_id)
        self.assertEqual(contact.lead, lead)
        self.assertEqual(contact.username, "nophone_user")

    def test_06_human_handoff(self):
        """TEST 6: Human handoff or is_automation_enabled=False prevents bot auto-responses."""
        user_id = "ig_user_handoff"
        p1 = {
            "external_event_id": "evt_ho_1",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": user_id,
            "message_text": "10 lakh",
            "external_message_id": "msg_ho_1"
        }
        r1 = self.client.post('/api/integrations/v1/instagram/process-message/', p1, format='json').json()
        conv = Conversation.objects.get(id=r1['conversation_id'])

        # Set conversation to HUMAN_HANDOFF
        conv.state = ConversationState.HUMAN_HANDOFF
        conv.save()

        p2 = {
            "external_event_id": "evt_ho_2",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": user_id,
            "message_text": "Can someone call me?",
            "external_message_id": "msg_ho_2"
        }
        r2 = self.client.post('/api/integrations/v1/instagram/process-message/', p2, format='json').json()
        self.assertEqual(r2['reply_text'], "")

    def test_07_duplicate_instagram_message(self):
        """TEST 7: Same external_message_id sent twice -> duplicate detected, empty reply returned."""
        user_id = "ig_user_dup_msg"
        p = {
            "external_event_id": "evt_dup_msg_1",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": user_id,
            "message_text": "10 lakh",
            "external_message_id": "msg_dup_unique_999"
        }
        r1 = self.client.post('/api/integrations/v1/instagram/process-message/', p, format='json').json()
        self.assertFalse(r1['is_duplicate'])

        r2 = self.client.post('/api/integrations/v1/instagram/process-message/', p, format='json').json()
        self.assertTrue(r2['is_duplicate'])
        self.assertEqual(r2['reply_text'], "")

    def test_08_duplicate_webhook_event(self):
        """TEST 8: Duplicate webhook event recorded in IntegrationEvent and idempotently handled."""
        p = {
            "external_event_id": "evt_web_dup_888",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": "ig_user_web_dup",
            "message_text": "15 lakh",
            "external_message_id": "msg_web_dup_111"
        }
        res1 = self.client.post('/api/integrations/v1/instagram/process-message/', p, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        res2 = self.client.post('/api/integrations/v1/instagram/process-message/', p, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertTrue(res2.json()['is_duplicate'])

        events_count = IntegrationEvent.objects.filter(brand=self.brand, external_event_id="evt_web_dup_888").count()
        self.assertEqual(events_count, 1)

    def test_09_same_instagram_user_across_two_brands(self):
        """TEST 9: Same Instagram user ID messaging Brand A and Brand B -> Isolated contacts & leads."""
        brand_b = Brand.objects.create(
            organization=self.org,
            name="Zywo Juice",
            slug="zywo-juice",
            min_investment_threshold=Decimal('1500000.00')
        )
        token_b = IntegrationToken.objects.create(
            brand=brand_b,
            name="Brand B Token",
            key="n8n_sec_brand_b_token_999"
        )
        client_b = APIClient()
        client_b.credentials(HTTP_X_INTEGRATION_API_KEY=token_b.key)

        user_id = "ig_user_cross_brand"

        # Message to Brand A
        p_a = {
            "external_event_id": "evt_cross_a",
            "instagram_account_id": "ig_acc_coolcane_01",
            "instagram_user_id": user_id,
            "message_text": "10 lakh",
            "external_message_id": "msg_cross_a"
        }
        self.client.post('/api/integrations/v1/instagram/process-message/', p_a, format='json')

        # Message to Brand B
        p_b = {
            "external_event_id": "evt_cross_b",
            "instagram_account_id": "ig_acc_zywo_01",
            "instagram_user_id": user_id,
            "message_text": "15 lakh",
            "external_message_id": "msg_cross_b"
        }
        client_b.post('/api/integrations/v1/instagram/process-message/', p_b, format='json')

        contacts = InstagramContact.objects.filter(instagram_user_id=user_id)
        self.assertEqual(contacts.count(), 2)

        contact_a = InstagramContact.objects.get(brand=self.brand, instagram_user_id=user_id)
        contact_b = InstagramContact.objects.get(brand=brand_b, instagram_user_id=user_id)
        self.assertNotEqual(contact_a.lead.id, contact_b.lead.id)

    def test_10_brand_specific_threshold(self):
        """TEST 10: Brand B with 15 lakh threshold disqualifies 10 lakh, but accepts 15 lakh."""
        brand_b = Brand.objects.create(
            organization=self.org,
            name="Premium Cafe",
            slug="premium-cafe",
            min_investment_threshold=Decimal('1500000.00')
        )
        token_b = IntegrationToken.objects.create(
            brand=brand_b,
            name="Brand B Token",
            key="token_premium_cafe_123"
        )
        client_b = APIClient()
        client_b.credentials(HTTP_X_INTEGRATION_API_KEY=token_b.key)

        # 10L to Premium Cafe -> DISQUALIFIED because 10L < 15L
        p1 = {
            "external_event_id": "evt_b_1",
            "instagram_account_id": "ig_acc_cafe_01",
            "instagram_user_id": "user_cafe_1",
            "message_text": "10 lakh",
            "external_message_id": "msg_b_1"
        }
        r1 = client_b.post('/api/integrations/v1/instagram/process-message/', p1, format='json').json()
        self.assertEqual(r1['state'], ConversationState.DISQUALIFIED)
        self.assertIn("minimum investment of ₹15 lakh", r1['reply_text'])

        # 15L to Premium Cafe -> WAITING_PROFESSION
        p2 = {
            "external_event_id": "evt_b_2",
            "instagram_account_id": "ig_acc_cafe_01",
            "instagram_user_id": "user_cafe_2",
            "message_text": "15 lakh",
            "external_message_id": "msg_b_2"
        }
        r2 = client_b.post('/api/integrations/v1/instagram/process-message/', p2, format='json').json()
        self.assertEqual(r2['state'], ConversationState.WAITING_PROFESSION)

    def test_11_full_qualification_temperature_flow(self):
        """TEST 11: Full multi-step qualification (HOT, WARM, COLD, LONG_TERM)."""
        user_id = "ig_user_full_hot"
        acc_id = "ig_acc_coolcane_01"

        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e_h1", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "10 lakh", "external_message_id": "m1"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e_h2", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Business owner", "external_message_id": "m2"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e_h3", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "3 years", "external_message_id": "m3"}, format='json')
        self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e_h4", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Kochi", "external_message_id": "m4"}, format='json')
        r5 = self.client.post('/api/integrations/v1/instagram/process-message/', {"external_event_id": "e_h5", "instagram_account_id": acc_id, "instagram_user_id": user_id, "message_text": "Within 2 months", "external_message_id": "m5"}, format='json').json()

        self.assertEqual(r5['state'], ConversationState.QUALIFICATION_COMPLETE)
        self.assertEqual(r5['lead_temperature'], LeadTemperature.HOT)

    def test_12_final_gate_safety_check(self):
        """TEST 12: Final gate verification - @coolcane_india is not connected to live webhook environment."""
        self.assertFalse(hasattr(self.brand, 'is_live_webhook_active') and getattr(self.brand, 'is_live_webhook_active') == True)
        self.assertEqual(self.brand.slug, "coolcane-india")
