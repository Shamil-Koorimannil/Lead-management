from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from users.models import Organization, Brand, User, UserRole
from leads.models import Lead, LeadSequence, ActivityLog, ActivityAction, LeadSource, SalesStatus, FollowUpType
from qualification.models import QualificationRule, OperatorChoices
from qualification.services import calculate_lead_qualification
from conversations.models import Conversation, Message, LeadNote, MessageDirection, MessageType, ConversationStatus

class Command(BaseCommand):
    help = 'Seeds initial Organization, Brand, Users, Qualification Rules, and Test Leads for MVP.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial MVP data...')

        # 1. Organization & Brand
        org, _ = Organization.objects.get_or_create(
            slug='zywo-network',
            defaults={'name': 'Zywo Franchise Network'}
        )
        brand, _ = Brand.objects.get_or_create(
            slug='zywo-franchise',
            defaults={'organization': org, 'name': 'Zywo Franchise'}
        )

        # 2. Users
        password = 'Password123!'

        owner, created = User.objects.get_or_create(
            email='owner@zywolabs.com',
            defaults={
                'first_name': 'Ahmed',
                'last_name': 'Owner',
                'role': UserRole.BRAND_OWNER,
                'brand': brand,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            owner.set_password(password)
            owner.save()

        manager, created = User.objects.get_or_create(
            email='manager@zywolabs.com',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Manager',
                'role': UserRole.SALES_MANAGER,
                'brand': brand,
                'is_staff': True,
            }
        )
        if created:
            manager.set_password(password)
            manager.save()

        agent1, created = User.objects.get_or_create(
            email='agent1@zywolabs.com',
            defaults={
                'first_name': 'Rohan',
                'last_name': 'Agent',
                'role': UserRole.SALES_AGENT,
                'brand': brand,
            }
        )
        if created:
            agent1.set_password(password)
            agent1.save()

        agent2, created = User.objects.get_or_create(
            email='agent2@zywolabs.com',
            defaults={
                'first_name': 'Priya',
                'last_name': 'Agent',
                'role': UserRole.SALES_AGENT,
                'brand': brand,
            }
        )
        if created:
            agent2.set_password(password)
            agent2.save()

        self.stdout.write(self.style.SUCCESS('Users created/updated successfully.'))

        # 3. Qualification Rules
        QualificationRule.objects.get_or_create(
            brand=brand,
            name='Investment Capacity >= ₹25 Lakhs',
            defaults={
                'field': 'investment_capacity',
                'operator': OperatorChoices.GTE,
                'value': '2500000',
                'score': 30,
                'priority': 1,
                'active': True,
            }
        )
        QualificationRule.objects.get_or_create(
            brand=brand,
            name='Preferred Location Available',
            defaults={
                'field': 'preferred_location',
                'operator': OperatorChoices.IS_TRUE,
                'value': '',
                'score': 20,
                'priority': 2,
                'active': True,
            }
        )
        QualificationRule.objects.get_or_create(
            brand=brand,
            name='Property Available',
            defaults={
                'field': 'property_available',
                'operator': OperatorChoices.IS_TRUE,
                'value': '',
                'score': 20,
                'priority': 3,
                'active': True,
            }
        )
        QualificationRule.objects.get_or_create(
            brand=brand,
            name='Business Experience Present',
            defaults={
                'field': 'business_experience',
                'operator': OperatorChoices.IS_TRUE,
                'value': '',
                'score': 10,
                'priority': 4,
                'active': True,
            }
        )
        QualificationRule.objects.get_or_create(
            brand=brand,
            name='Expected Start within 6 months',
            defaults={
                'field': 'expected_start',
                'operator': OperatorChoices.CONTAINS,
                'value': 'month',
                'score': 20,
                'priority': 5,
                'active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Qualification Rules seeded.'))

        # 4. Test Leads
        # Ensure lead sequence is initialized
        seq, _ = LeadSequence.objects.get_or_create(brand=brand)
        if seq.next_number < 1:
            seq.next_number = 1
            seq.save()

        # TEST-001 (Ahmed, ₹50L, Score: 100 QUALIFIED)
        lead1, l1_created = Lead.objects.get_or_create(
            phone='+919999999001',
            defaults={
                'brand': brand,
                'lead_number': 'LEAD-000001',
                'name': 'Ahmed',
                'email': 'ahmed.test@example.com',
                'city': 'Kochi',
                'preferred_location': 'Kochi',
                'investment_capacity': Decimal('5000000'),
                'property_available': True,
                'business_experience': True,
                'expected_start': '3 months',
                'lead_source': LeadSource.TEST,
                'sales_status': SalesStatus.FOLLOW_UP,
                'assigned_to': agent1,
                'assigned_at': timezone.now(),
                'follow_up_required': True,
                'next_follow_up_at': timezone.now() + timedelta(hours=4),
                'follow_up_type': FollowUpType.CALL,
                'follow_up_note': 'Follow up regarding site visit details.',
            }
        )
        calculate_lead_qualification(lead1, save=True)

        # TEST-002 (Rahul, ₹10L, NOT_QUALIFIED - Hard Disqualified)
        lead2, l2_created = Lead.objects.get_or_create(
            phone='+919999999002',
            defaults={
                'brand': brand,
                'lead_number': 'LEAD-000002',
                'name': 'Rahul',
                'email': 'rahul.test@example.com',
                'city': 'Kochi',
                'preferred_location': 'Kochi',
                'investment_capacity': Decimal('1000000'),
                'property_available': False,
                'business_experience': False,
                'expected_start': '2 years',
                'lead_source': LeadSource.TEST,
                'sales_status': SalesStatus.CONTACTED,
                'assigned_to': agent2,
                'assigned_at': timezone.now(),
            }
        )
        calculate_lead_qualification(lead2, save=True)

        # TEST-003 (Arjun, ₹30L, Score: 80 QUALIFIED)
        lead3, l3_created = Lead.objects.get_or_create(
            phone='+919999999003',
            defaults={
                'brand': brand,
                'lead_number': 'LEAD-000003',
                'name': 'Arjun',
                'email': 'arjun.test@example.com',
                'city': 'Bangalore',
                'preferred_location': 'Bangalore',
                'investment_capacity': Decimal('3000000'),
                'property_available': False,
                'business_experience': True,
                'expected_start': '6 months',
                'lead_source': LeadSource.TEST,
                'sales_status': SalesStatus.NEW,
                'assigned_to': agent1,
                'assigned_at': timezone.now(),
            }
        )
        calculate_lead_qualification(lead3, save=True)

        # Ensure next lead number sequence is properly incremented
        seq.next_number = max(seq.next_number, 4)
        seq.save()

        # 5. Conversations & Messages for Lead 1
        conv1, _ = Conversation.objects.get_or_create(
            lead=lead1,
            channel=LeadSource.WHATSAPP,
            defaults={'status': ConversationStatus.OPEN}
        )
        Message.objects.get_or_create(
            conversation=conv1,
            message='I am interested in acquiring the franchise for Kochi location.',
            defaults={'direction': MessageDirection.INBOUND, 'message_type': MessageType.TEXT}
        )
        Message.objects.get_or_create(
            conversation=conv1,
            message='Thank you Ahmed! May I know your preferred site size and investment budget?',
            defaults={'direction': MessageDirection.OUTBOUND, 'message_type': MessageType.TEXT}
        )

        # 6. Internal Notes
        LeadNote.objects.get_or_create(
            lead=lead1,
            author=agent1,
            content='Customer is highly motivated. Requested evening call back after 6 PM.'
        )

        # 7. Activity Logs
        ActivityLog.objects.get_or_create(
            lead=lead1,
            action=ActivityAction.LEAD_CREATED,
            defaults={'brand': brand, 'actor': owner, 'description': 'Lead LEAD-000001 created via seed data.'}
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded MVP database with test users and leads!'))
