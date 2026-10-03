import json
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from users.models import Organization, Brand
from conversations.services import InstagramQualificationService

class Command(BaseCommand):
    help = "Simulates an inbound Instagram DM for local testing of qualification state machine, idempotency, and temperature classification."

    def add_arguments(self, parser):
        parser.add_argument('--message', type=str, required=True, help="Text content of the simulated Instagram DM.")
        parser.add_argument('--user-id', type=str, default="sim_ig_user_1001", help="Simulated Meta Instagram User ID.")
        parser.add_argument('--account-id', type=str, default="sim_ig_acc_coolcane", help="Simulated Instagram Account ID.")
        parser.add_argument('--brand-slug', type=str, default="coolcane-india", help="Target Brand slug.")
        parser.add_argument('--username', type=str, default="simulated_user", help="Simulated Instagram username.")
        parser.add_argument('--event-id', type=str, default=None, help="External event ID for idempotency test.")
        parser.add_argument('--message-id', type=str, default=None, help="External message ID for idempotency test.")

    def handle(self, *args, **options):
        brand_slug = options['brand_slug']
        brand = Brand.objects.filter(slug=brand_slug).first()
        if not brand:
            # Auto-create test brand if running in blank local dev DB
            org, _ = Organization.objects.get_or_create(name="CoolCane Corp", defaults={'slug': 'coolcane-corp'})
            brand = Brand.objects.create(
                organization=org,
                name="CoolCane India",
                slug="coolcane-india",
                min_investment_threshold=Decimal('1000000.00')
            )

        event_id = options['event_id'] or f"sim_evt_{uuid.uuid4().hex[:12]}"
        message_id = options['message_id'] or f"sim_msg_{uuid.uuid4().hex[:12]}"

        result = InstagramQualificationService.process_inbound_message(
            brand=brand,
            instagram_account_id=options['account_id'],
            instagram_user_id=options['user_id'],
            username=options['username'],
            display_name=options['username'].title(),
            message_text=options['message'],
            external_message_id=message_id,
            external_event_id=event_id
        )

        lead = result['lead']
        conv = result['conversation']

        output = {
            "reply_text": result['reply_text'],
            "conversation_id": conv.id if conv else None,
            "lead_id": lead.id if lead else None,
            "lead_number": lead.lead_number if lead else None,
            "phone": lead.phone if lead else "",
            "state": conv.state if conv else None,
            "lead_temperature": lead.lead_temperature if lead else None,
            "qualification_status": lead.qualification_status if lead else None,
            "is_duplicate": result.get('is_duplicate', False)
        }

        self.stdout.write(self.style.SUCCESS(json.dumps(output, indent=2)))
