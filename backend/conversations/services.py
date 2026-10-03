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
    brand-configurable investment floor, dynamic prompts, investment confirmation, and human handoff safety.
    """

    @classmethod
    def _get_brand_threshold(cls, brand) -> Decimal:
        threshold = Decimal('1000000.00')
        if brand and hasattr(brand, 'min_investment_threshold') and brand.min_investment_threshold is not None:
            threshold = Decimal(str(brand.min_investment_threshold))
        return threshold

    @classmethod
    def _format_lakh(cls, amount: Decimal) -> str:
        if amount % Decimal('100000') == 0:
            val = int(amount / Decimal('100000'))
            return f"₹{val} lakh"
        elif amount % Decimal('1000') == 0:
            val = float(amount / Decimal('100000'))
            return f"₹{val:g} lakh"
        else:
            return f"₹{amount:,.2f}"

    @classmethod
    def get_investment_prompt(cls, brand) -> str:
        brand_name = brand.name if (brand and brand.name) else "Franchise"
        threshold = cls._get_brand_threshold(brand)
        t_val = int(threshold / Decimal('100000')) if threshold % Decimal('100000') == 0 else float(threshold / Decimal('100000'))
        return (
            f"Great! We'd be happy to help you explore the {brand_name} franchise opportunity. "
            f"I'll ask you a few quick questions so we can understand whether it's suitable for you.\n\n"
            f"What approximate investment are you planning for the franchise?\n"
            f"• ₹{t_val:g}–{t_val+5:g} lakh\n"
            f"• ₹{t_val+5:g}–{t_val+15:g} lakh\n"
            f"• ₹{t_val+15:g}–{t_val+40:g} lakh\n"
            f"• ₹{t_val+40:g} lakh+\n"
            f"• Not sure"
        )

    @classmethod
    def get_profession_prompt(cls) -> str:
        return (
            "Thank you! What is your current profession?\n"
            "• Business owner\n"
            "• Salaried / Job\n"
            "• Self-employed / Professional\n"
            "• Student\n"
            "• Other"
        )

    @classmethod
    def get_business_duration_prompt(cls) -> str:
        return "How long have you been running your current business?"

    @classmethod
    def get_previous_experience_prompt(cls) -> str:
        return "Have you previously owned or operated a business?"

    @classmethod
    def get_location_prompt(cls, brand) -> str:
        brand_name = brand.name if (brand and brand.name) else "Franchise"
        return f"Which city or location are you considering for your {brand_name} outlet?"

    @classmethod
    def get_timeline_prompt(cls, brand) -> str:
        brand_name = brand.name if (brand and brand.name) else "Franchise"
        return (
            f"When are you planning to open your {brand_name} outlet?\n"
            f"1. Within 2 months\n"
            f"2. Within 6 months\n"
            f"3. Within 1 year\n"
            f"4. More than 1 year\n"
            f"5. Not decided yet"
        )

    @classmethod
    def get_completion_message(cls, brand) -> str:
        brand_name = brand.name if (brand and brand.name) else "Franchise"
        return (
            f"Thank you! We have collected your franchise enquiry details. "
            f"A representative from our {brand_name} franchise team will review your application and contact you shortly."
        )

    @classmethod
    def get_disqualification_message(cls, brand) -> str:
        brand_name = brand.name if (brand and brand.name) else "Franchise"
        threshold = cls._get_brand_threshold(brand)
        t_lakh = cls._format_lakh(threshold)
        return (
            f"Thank you for your interest in {brand_name}. Our franchise opportunity currently requires a minimum "
            f"investment of {t_lakh}. Based on the investment range you've shared, it may not be the right fit at this stage."
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
            # 1. Find or create InstagramContact scoped strictly to (brand, instagram_account_id, instagram_user_id)
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
                lead_name = display_name or (f"@{username}" if username else f"IG User {instagram_user_id[:8]}")
                from leads.models import LeadSequence
                lead_num = LeadSequence.get_next_lead_number(brand)
                lead = Lead.objects.create(
                    brand=brand,
                    lead_number=lead_num,
                    name=lead_name,
                    phone='',  # Kept blank until explicitly collected
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
            if not conversation.is_automation_enabled or conversation.state in [ConversationState.HUMAN_HANDOFF, ConversationState.QUALIFICATION_COMPLETE]:
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
        brand = lead.brand

        # Initial state -> send greeting & ask investment
        if current_state in [ConversationState.NEW, ConversationState.QUALIFYING]:
            parsed = normalize_investment(cleaned_text)
            if parsed['status'] != 'INVALID' and parsed['value'] is not None:
                return cls._handle_investment_value(conversation, lead, parsed)
            return cls.get_investment_prompt(brand), ConversationState.WAITING_INVESTMENT

        elif current_state == ConversationState.WAITING_INVESTMENT:
            parsed = normalize_investment(cleaned_text)
            if parsed['status'] == 'INVALID' or parsed['value'] is None:
                threshold = cls._get_brand_threshold(brand)
                t_lakh = cls._format_lakh(threshold)
                return (
                    f"Could you please specify your approximate investment budget? For example: {t_lakh}, ₹15 lakh, or 25L.",
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
                threshold = cls._get_brand_threshold(brand)
                t_lakh = cls._format_lakh(threshold)
                return (
                    f"No problem! Please enter your target investment amount (e.g. {t_lakh}, ₹15 lakh, ₹25 lakh).",
                    ConversationState.WAITING_INVESTMENT
                )

        elif current_state == ConversationState.WAITING_PROFESSION:
            profession = normalize_profession(cleaned_text)
            lead.current_profession = profession
            lead.save(update_fields=['current_profession'])

            if profession == CurrentProfession.BUSINESS:
                return cls.get_business_duration_prompt(), ConversationState.WAITING_BUSINESS_DURATION
            else:
                return cls.get_previous_experience_prompt(), ConversationState.WAITING_PREVIOUS_EXPERIENCE

        elif current_state == ConversationState.WAITING_BUSINESS_DURATION:
            lead.business_duration = cleaned_text
            lead.business_experience = True
            lead.save(update_fields=['business_duration', 'business_experience'])
            return cls.get_location_prompt(brand), ConversationState.WAITING_LOCATION

        elif current_state == ConversationState.WAITING_PREVIOUS_EXPERIENCE:
            has_exp = any(word in cleaned_text.lower() for word in ['yes', 'yeah', 'yep', 'owned', 'ran', 'have', 'true', '1'])
            lead.previous_business_experience = has_exp
            lead.business_experience = has_exp
            lead.save(update_fields=['previous_business_experience', 'business_experience'])
            return cls.get_location_prompt(brand), ConversationState.WAITING_LOCATION

        elif current_state == ConversationState.WAITING_LOCATION:
            lead.preferred_location = cleaned_text
            if not lead.city:
                lead.city = cleaned_text
            lead.save(update_fields=['preferred_location', 'city'])
            return cls.get_timeline_prompt(brand), ConversationState.WAITING_OPENING_TIMELINE

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

            return cls.get_completion_message(brand), ConversationState.QUALIFICATION_COMPLETE

        return "", current_state

    @classmethod
    def _handle_investment_value(cls, conversation: Conversation, lead: Lead, parsed: dict) -> tuple[str, str]:
        val = parsed['value']
        brand = lead.brand
        brand_name = brand.name if (brand and brand.name) else "Franchise"

        if parsed['status'] == 'AMBIGUOUS':
            conversation.pending_investment_amount = val
            lakh_val = int(val / Decimal('100000')) if val % Decimal('100000') == 0 else float(val / Decimal('100000'))
            return (
                f"Just to confirm, are you considering an approximate investment of ₹{lakh_val:g} lakh for your {brand_name} franchise?",
                ConversationState.CONFIRMING_INVESTMENT
            )

        # Standard confirmed investment value
        lead.investment_capacity = val
        lead.save(update_fields=['investment_capacity'])

        threshold = cls._get_brand_threshold(brand)

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
            return cls.get_disqualification_message(brand), ConversationState.DISQUALIFIED
        else:
            calculate_lead_qualification(lead, save=True)
            return cls.get_profession_prompt(), ConversationState.WAITING_PROFESSION
