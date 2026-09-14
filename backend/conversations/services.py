from decimal import Decimal
from django.db import transaction
from leads.models import (
    Lead, LeadSource, ActivityLog, ActivityAction, CurrentProfession, OpeningTimeline
)
from qualification.services import (
    calculate_lead_qualification, normalize_investment, normalize_profession, normalize_timeline
)
from .models import Conversation, ConversationState, InstagramContact, Message, MessageDirection, MessageType

class InstagramQualificationService:
    """
    Authoritative Progressive State Machine for Instagram Franchise Enquiry Qualification.
    Enforces state persistence, deterministic qualification & temperature evaluation,
    immediate disqualification below ₹10L, investment confirmation, and human handoff safety.
    """

    GREETING_AND_INVESTMENT_PROMPT = (
        "Great! We'd be happy to help you explore the CoolCane franchise opportunity. "
        "I'll ask you a few quick questions so we can understand whether it's suitable for you.\n\n"
        "What approximate investment are you planning for the franchise?\n"
        "• ₹10–15 lakh\n"
        "• ₹15–25 lakh\n"
        "• ₹25–50 lakh\n"
        "• ₹50 lakh+\n"
        "• Not sure"
    )

    PROFESSION_PROMPT = (
        "Thank you! What is your current profession?\n"
        "• Business owner\n"
        "• Salaried / Job\n"
        "• Self-employed / Professional\n"
        "• Student\n"
        "• Other"
    )

    BUSINESS_DURATION_PROMPT = "How long have you been running your current business?"

    PREVIOUS_EXPERIENCE_PROMPT = "Have you previously owned or operated a business?"

    LOCATION_PROMPT = "Which city or location are you considering for your CoolCane outlet?"

    TIMELINE_PROMPT = (
        "When are you planning to open your CoolCane outlet?\n"
        "1. Within 2 months\n"
        "2. Within 6 months\n"
        "3. Within 1 year\n"
        "4. More than 1 year\n"
        "5. Not decided yet"
    )

    COMPLETION_MESSAGE = (
        "Thank you! We have collected your franchise enquiry details. "
        "A representative from our CoolCane franchise team will review your application and contact you shortly."
    )

    DISQUALIFICATION_MESSAGE = (
        "Thank you for your interest in CoolCane. Our franchise opportunity currently requires a minimum "
        "investment of ₹10 lakh. Based on the investment range you've shared, it may not be the right fit at this stage."
    )

    @classmethod
    def process_inbound_message(cls, brand, instagram_account_id: str, instagram_user_id: str,
                                username: str, display_name: str, message_text: str,
                                external_message_id: str = '', external_event_id: str = '') -> dict:
        """
        Main processing method for inbound Instagram messages.
        Returns dict containing reply_text, conversation, lead, state, and is_duplicate flag.
        """
        with transaction.atomic():
            # 1. Find or create InstagramContact
            contact, _ = InstagramContact.objects.get_or_create(
                brand=brand,
                instagram_account_id=instagram_account_id,
                instagram_user_id=instagram_user_id,
                defaults={
                    'username': username or '',
                    'display_name': display_name or ''
                }
            )
            if username and contact.username != username:
                contact.username = username
                contact.save(update_fields=['username'])
            if display_name and contact.display_name != display_name:
                contact.display_name = display_name
                contact.save(update_fields=['display_name'])

            # 2. Find or create associated Lead
            lead = contact.lead
            if not lead:
                # Try finding lead by Instagram contact or create new Lead
                lead_name = display_name or (f"@{username}" if username else f"IG User {instagram_user_id[:8]}")
                from leads.models import LeadSequence
                lead_num = LeadSequence.get_next_lead_number(brand)
                lead = Lead.objects.create(
                    brand=brand,
                    lead_number=lead_num,
                    name=lead_name,
                    phone=f"IG:{instagram_user_id}",
                    email='',
                    city='',
                    lead_source=LeadSource.INSTAGRAM
                )
                contact.lead = lead
                contact.save(update_fields=['lead'])

                ActivityLog.objects.create(
                    brand=brand,
                    lead=lead,
                    actor=None,
                    action=ActivityAction.LEAD_CREATED,
                    description=f"Lead {lead.lead_number} created via Instagram DM from IG User ID {instagram_user_id} (@{username})."
                )

            # 3. Find or create Conversation
            conversation = Conversation.objects.filter(
                lead=lead, channel=LeadSource.INSTAGRAM, instagram_contact=contact
            ).first()

            if not conversation:
                conversation = Conversation.objects.create(
                    lead=lead,
                    channel=LeadSource.INSTAGRAM,
                    instagram_contact=contact,
                    state=ConversationState.NEW
                )

            # 4. Check for duplicate Message by external_message_id
            if external_message_id and Message.objects.filter(conversation=conversation, external_message_id=external_message_id).exists():
                return {
                    'reply_text': '',
                    'conversation': conversation,
                    'lead': lead,
                    'is_duplicate': True
                }

            # 5. Persist Inbound Message
            Message.objects.create(
                conversation=conversation,
                direction=MessageDirection.INBOUND,
                message=message_text,
                message_type=MessageType.TEXT,
                external_message_id=external_message_id or ''
            )

            ActivityLog.objects.create(
                brand=brand,
                lead=lead,
                actor=None,
                action=ActivityAction.INSTAGRAM_MESSAGE_RECEIVED,
                description=f"Received IG DM: \"{message_text[:100]}\""
            )

            # 6. Safety check: If automation disabled or human handoff state, do not send bot reply
            if not conversation.is_automation_enabled or conversation.state in [ConversationState.HUMAN_HANDOFF, ConversationState.QUALIFIED]:
                return {
                    'reply_text': '',
                    'conversation': conversation,
                    'lead': lead,
                    'is_duplicate': False
                }

            # If already disqualified, do not send further automated responses
            if conversation.state == ConversationState.DISQUALIFIED:
                return {
                    'reply_text': '',
                    'conversation': conversation,
                    'lead': lead,
                    'is_duplicate': False
                }

            # 7. Progressive State Machine Evaluation
            reply_text, next_state = cls._evaluate_state_transition(conversation, lead, message_text)

            # Update conversation state
            if next_state != conversation.state:
                conversation.state = next_state
                conversation.save(update_fields=['state', 'pending_investment_amount', 'updated_at'])

            # 8. Persist Outbound Message if reply_text exists
            if reply_text:
                Message.objects.create(
                    conversation=conversation,
                    direction=MessageDirection.OUTBOUND,
                    message=reply_text,
                    message_type=MessageType.TEXT
                )
                ActivityLog.objects.create(
                    brand=brand,
                    lead=lead,
                    actor=None,
                    action=ActivityAction.INSTAGRAM_MESSAGE_SENT,
                    description=f"Sent IG Bot Reply: \"{reply_text[:100]}\""
                )

            return {
                'reply_text': reply_text,
                'conversation': conversation,
                'lead': lead,
                'is_duplicate': False
            }

    @classmethod
    def _evaluate_state_transition(cls, conversation: Conversation, lead: Lead, text: str) -> tuple[str, str]:
        current_state = conversation.state
        cleaned_text = text.strip()

        # Initial state -> send greeting & ask investment
        if current_state in [ConversationState.NEW, ConversationState.QUALIFYING]:
            # Ask investment
            parsed = normalize_investment(cleaned_text)
            if parsed['status'] != 'INVALID' and parsed['value'] is not None:
                # User provided investment in their first message!
                return cls._handle_investment_value(conversation, lead, parsed)
            return cls.GREETING_AND_INVESTMENT_PROMPT, ConversationState.WAITING_INVESTMENT

        elif current_state == ConversationState.WAITING_INVESTMENT:
            parsed = normalize_investment(cleaned_text)
            if parsed['status'] == 'INVALID' or parsed['value'] is None:
                return (
                    "Could you please specify your approximate investment budget? For example: ₹10 lakh, ₹15 lakh, or 25L.",
                    ConversationState.WAITING_INVESTMENT
                )
            return cls._handle_investment_value(conversation, lead, parsed)

        elif current_state == ConversationState.CONFIRMING_INVESTMENT:
            is_yes = any(word in cleaned_text.lower() for word in ['yes', 'yeah', 'yep', 'correct', 'right', 'true', 'confirm', 'sure', '1'])
            if is_yes and conversation.pending_investment_amount:
                parsed = {'status': 'CONFIRMED', 'value': conversation.pending_investment_amount}
                conversation.pending_investment_amount = None
                return cls._handle_investment_value(conversation, lead, parsed)
            else:
                conversation.pending_investment_amount = None
                return (
                    "No problem! Please enter your target investment amount (e.g. ₹10 lakh, ₹15 lakh, ₹25 lakh).",
                    ConversationState.WAITING_INVESTMENT
                )

        elif current_state == ConversationState.WAITING_PROFESSION:
            profession = normalize_profession(cleaned_text)
            lead.current_profession = profession
            lead.save(update_fields=['current_profession'])

            if profession == CurrentProfession.BUSINESS:
                return cls.BUSINESS_DURATION_PROMPT, ConversationState.WAITING_BUSINESS_DURATION
            else:
                return cls.PREVIOUS_EXPERIENCE_PROMPT, ConversationState.WAITING_PREVIOUS_EXPERIENCE

        elif current_state == ConversationState.WAITING_BUSINESS_DURATION:
            lead.business_duration = cleaned_text
            lead.business_experience = True
            lead.save(update_fields=['business_duration', 'business_experience'])
            return cls.LOCATION_PROMPT, ConversationState.WAITING_LOCATION

        elif current_state == ConversationState.WAITING_PREVIOUS_EXPERIENCE:
            has_exp = any(word in cleaned_text.lower() for word in ['yes', 'yeah', 'yep', 'owned', 'ran', 'have', 'true', '1'])
            lead.previous_business_experience = has_exp
            lead.business_experience = has_exp
            lead.save(update_fields=['previous_business_experience', 'business_experience'])
            return cls.LOCATION_PROMPT, ConversationState.WAITING_LOCATION

        elif current_state == ConversationState.WAITING_LOCATION:
            lead.preferred_location = cleaned_text
            if not lead.city:
                lead.city = cleaned_text
            lead.save(update_fields=['preferred_location', 'city'])
            return cls.TIMELINE_PROMPT, ConversationState.WAITING_OPENING_TIMELINE

        elif current_state == ConversationState.WAITING_OPENING_TIMELINE:
            timeline = normalize_timeline(cleaned_text)
            lead.opening_timeline = timeline
            lead.expected_start = cleaned_text
            lead.save(update_fields=['opening_timeline', 'expected_start'])

            # Perform final server-side qualification & temperature calculation
            calculate_lead_qualification(lead, save=True)

            ActivityLog.objects.create(
                brand=lead.brand,
                lead=lead,
                actor=None,
                action=ActivityAction.QUALIFICATION_COMPLETED,
                description=f"Franchise qualification completed. Temperature: {lead.lead_temperature}, Status: {lead.qualification_status}."
            )

            return cls.COMPLETION_MESSAGE, ConversationState.QUALIFIED

        return "", current_state

    @classmethod
    def _handle_investment_value(cls, conversation: Conversation, lead: Lead, parsed: dict) -> tuple[str, str]:
        val = parsed['value']
        if parsed['status'] == 'AMBIGUOUS':
            conversation.pending_investment_amount = val
            lakh_val = int(val / Decimal('100000')) if val % Decimal('100000') == 0 else float(val / Decimal('100000'))
            return (
                f"Just to confirm, are you considering an approximate investment of ₹{lakh_val} lakh for your CoolCane franchise?",
                ConversationState.CONFIRMING_INVESTMENT
            )

        # Standard confirmed investment value
        lead.investment_capacity = val
        lead.save(update_fields=['investment_capacity'])

        threshold = Decimal('1000000.00')
        if lead.brand and hasattr(lead.brand, 'min_investment_threshold') and lead.brand.min_investment_threshold is not None:
            threshold = Decimal(str(lead.brand.min_investment_threshold))

        # Check hard investment floor threshold
        if val < threshold:
            calculate_lead_qualification(lead, save=True)
            ActivityLog.objects.create(
                brand=lead.brand,
                lead=lead,
                actor=None,
                action=ActivityAction.LEAD_DISQUALIFIED,
                description=f"Lead disqualified automatically: Investment capacity (₹{val:,.2f}) is below minimum threshold (₹{threshold:,.2f})."
            )
            return cls.DISQUALIFICATION_MESSAGE, ConversationState.DISQUALIFIED
        else:
            calculate_lead_qualification(lead, save=True)
            return cls.PROFESSION_PROMPT, ConversationState.WAITING_PROFESSION
