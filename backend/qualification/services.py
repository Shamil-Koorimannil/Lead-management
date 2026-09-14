import re
from decimal import Decimal
from leads.models import (
    Lead, QualificationStatus, LeadTemperature, CurrentProfession, OpeningTimeline
)
from .models import QualificationRule, OperatorChoices

def normalize_investment(text: str) -> dict:
    """
    Parses natural language investment responses into numeric Decimal values.
    Supports Indian notation (10 lakh, 10L, 10 lacs, ₹10,00,000, 10-15 lakh, etc.)
    Returns dict: {'status': 'CONFIRMED' | 'AMBIGUOUS' | 'INVALID', 'value': Decimal | None}
    """
    if not text:
        return {'status': 'INVALID', 'value': None}

    cleaned = text.strip().lower()

    # Check for range choices e.g. "10-15 lakh", "10 to 15 lakhs", "₹10–15 lakh", "1"
    if '10' in cleaned and ('15' in cleaned or '–' in text or '-' in cleaned or 'to' in cleaned):
        return {'status': 'CONFIRMED', 'value': Decimal('1000000.00')}
    if '15' in cleaned and ('25' in cleaned or '–' in text or '-' in cleaned or 'to' in cleaned):
        return {'status': 'CONFIRMED', 'value': Decimal('1500000.00')}
    if '25' in cleaned and ('50' in cleaned or '–' in text or '-' in cleaned or 'to' in cleaned):
        return {'status': 'CONFIRMED', 'value': Decimal('2500000.00')}
    if '50' in cleaned and ('+' in cleaned or 'above' in cleaned or 'more' in cleaned):
        return {'status': 'CONFIRMED', 'value': Decimal('5000000.00')}

    is_ambiguous = any(word in cleaned for word in ['around', 'approx', 'approximate', 'maybe', 'nearly', 'about', 'guess'])

    # Standard Lakh / Lac / L regex: e.g. "10 lakh", "10.5 lakh", "10l", "10 lacs"
    lakh_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|\s*l\b)', cleaned)
    if lakh_match:
        val = Decimal(lakh_match.group(1)) * Decimal('100000')
        return {'status': 'AMBIGUOUS' if is_ambiguous else 'CONFIRMED', 'value': val}

    # Crore regex: e.g. "1 cr", "1 crore"
    crore_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:crore|crores|cr\b)', cleaned)
    if crore_match:
        val = Decimal(crore_match.group(1)) * Decimal('10000000')
        return {'status': 'AMBIGUOUS' if is_ambiguous else 'CONFIRMED', 'value': val}

    # Direct raw number e.g. "10,00,000", "1000000"
    raw_num_str = re.sub(r'[^\d.]', '', cleaned)
    if raw_num_str:
        try:
            num = Decimal(raw_num_str)
            # If user just wrote "10" without lakh context in natural text
            if num <= 50 and ('lakh' not in cleaned and 'l' not in cleaned):
                # Assume 10 means 10 lakh in franchise context, but flag as AMBIGUOUS
                return {'status': 'AMBIGUOUS', 'value': num * Decimal('100000')}
            return {'status': 'AMBIGUOUS' if is_ambiguous else 'CONFIRMED', 'value': num}
        except Exception:
            pass

    return {'status': 'INVALID', 'value': None}

def normalize_profession(text: str) -> str:
    """Normalizes natural language input into CurrentProfession choice."""
    if not text:
        return CurrentProfession.OTHER
    cleaned = text.strip().lower()
    if any(k in cleaned for k in ['business', 'owner', 'entrepreneur', 'company', 'shop', 'store']):
        return CurrentProfession.BUSINESS
    if any(k in cleaned for k in ['salary', 'salaried', 'job', 'employee', 'corporate', 'work', 'working']):
        return CurrentProfession.SALARIED
    if any(k in cleaned for k in ['self', 'freelance', 'consultant', 'doctor', 'lawyer', 'chartered', 'ca', 'agent']):
        return CurrentProfession.SELF_EMPLOYED
    if any(k in cleaned for k in ['student', 'college', 'university', 'study']):
        return CurrentProfession.STUDENT
    return CurrentProfession.OTHER

def normalize_timeline(text: str) -> str:
    """Normalizes natural language input into OpeningTimeline choice."""
    if not text:
        return OpeningTimeline.NOT_DECIDED
    cleaned = text.strip().lower()

    if cleaned in ['1', 'option 1', 'option1'] or any(k in cleaned for k in ['within 2', '2 month', '2months', 'immediate', 'asap', 'soon', '2 mon']):
        return OpeningTimeline.WITHIN_2_MONTHS
    if cleaned in ['2', 'option 2', 'option2'] or any(k in cleaned for k in ['within 6', '6 month', '6months', '3 month', '4 month', '5 month']):
        return OpeningTimeline.WITHIN_6_MONTHS
    if cleaned in ['4', 'option 4', 'option4'] or any(k in cleaned for k in ['more than 1 year', '> 1 year', '>1 year', 'above 1 year', '2 year', '3 year']):
        return OpeningTimeline.MORE_THAN_1_YEAR
    if cleaned in ['3', 'option 3', 'option3'] or any(k in cleaned for k in ['within 1 year', '1 year', '12 month', '12months']):
        return OpeningTimeline.WITHIN_1_YEAR
    if cleaned in ['5', 'option 5', 'option5'] or any(k in cleaned for k in ['not decided', 'undecided', 'no idea', 'not sure', 'later']):
        return OpeningTimeline.NOT_DECIDED

    return OpeningTimeline.NOT_DECIDED

def evaluate_rule(lead: Lead, rule: QualificationRule) -> bool:
    """Evaluates a single qualification rule against lead parameters."""
    field_value = getattr(lead, rule.field, None)
    if field_value is None:
        return False

    op = rule.operator
    val = rule.value

    try:
        if op == OperatorChoices.IS_TRUE:
            return bool(field_value)
        elif op == OperatorChoices.IS_FALSE:
            return not bool(field_value)
        elif op == OperatorChoices.GTE:
            num_val = Decimal(val)
            lead_val = Decimal(str(field_value)) if field_value is not None else Decimal('0')
            return lead_val >= num_val
        elif op == OperatorChoices.LTE:
            num_val = Decimal(val)
            lead_val = Decimal(str(field_value)) if field_value is not None else Decimal('0')
            return lead_val <= num_val
        elif op == OperatorChoices.EQ:
            return str(field_value).strip().lower() == str(val).strip().lower()
        elif op == OperatorChoices.CONTAINS:
            return str(val).strip().lower() in str(field_value).strip().lower()
    except Exception:
        return False

    return False

def calculate_lead_qualification(lead: Lead, save: bool = True) -> Lead:
    """
    Authoritative Server-Side Qualification Engine Service.
    Evaluates investment threshold, calculates qualification status & score,
    and classifies lead temperature (HOT, WARM, COLD, LONG_TERM, DISQUALIFIED, or NULL).
    """
    # 1. Determine Brand Minimum Investment Threshold (Default: ₹10,00,000 for CoolCane/Franchise)
    threshold = Decimal('1000000.00')
    if lead.brand and hasattr(lead.brand, 'min_investment_threshold') and lead.brand.min_investment_threshold is not None:
        threshold = Decimal(str(lead.brand.min_investment_threshold))

    # 2. Hard Investment Disqualification Floor (< ₹10,00,000)
    if lead.investment_capacity is not None and lead.investment_capacity < threshold:
        lead.qualification_score = 0
        lead.qualification_status = QualificationStatus.NOT_QUALIFIED
        lead.lead_temperature = LeadTemperature.DISQUALIFIED
        lead.qualification_reason = f"Lead is not qualified because investment capacity is below the minimum threshold (₹{threshold:,.2f})."
        if save:
            lead.save(update_fields=[
                'qualification_score', 'qualification_status', 'lead_temperature',
                'qualification_reason', 'updated_at'
            ])
        return lead

    # 3. Determine Lead Temperature based on Opening Timeline after Investment Minimum (>= ₹10,00,000) is satisfied
    if lead.investment_capacity is not None and lead.investment_capacity >= threshold:
        if lead.opening_timeline:
            if lead.opening_timeline == OpeningTimeline.WITHIN_2_MONTHS:
                lead.lead_temperature = LeadTemperature.HOT
                lead.follow_up_required = True
            elif lead.opening_timeline == OpeningTimeline.WITHIN_6_MONTHS:
                lead.lead_temperature = LeadTemperature.WARM
            elif lead.opening_timeline == OpeningTimeline.WITHIN_1_YEAR:
                lead.lead_temperature = LeadTemperature.COLD
            elif lead.opening_timeline in [OpeningTimeline.MORE_THAN_1_YEAR, OpeningTimeline.NOT_DECIDED]:
                lead.lead_temperature = LeadTemperature.LONG_TERM
        elif lead.expected_start:
            exp_lower = lead.expected_start.lower()
            if any(term in exp_lower for term in ['2 month', 'immediate', 'asap']):
                lead.lead_temperature = LeadTemperature.HOT
                lead.follow_up_required = True
            elif any(term in exp_lower for term in ['6 month', '3 month']):
                lead.lead_temperature = LeadTemperature.WARM
            elif '1 year' in exp_lower or '12 month' in exp_lower:
                lead.lead_temperature = LeadTemperature.COLD
            elif any(term in exp_lower for term in ['more than', 'long', 'not decided']):
                lead.lead_temperature = LeadTemperature.LONG_TERM

    # 4. Fetch Active Brand Qualification Rules for Qualification Status & Score Calculation
    rules = QualificationRule.objects.filter(brand=lead.brand, active=True).order_by('priority')

    total_score = 0
    reasons = []

    if rules.exists():
        for rule in rules:
            if evaluate_rule(lead, rule):
                total_score += rule.score
                reasons.append(f"{rule.name} (+{rule.score})")
    else:
        # Fallback to standard baseline criteria if no DB rules have been created for the brand yet
        if lead.investment_capacity and lead.investment_capacity >= Decimal('2500000'):
            total_score += 30
            reasons.append("Investment capacity meets required threshold (+30)")

        if lead.preferred_location and lead.preferred_location.strip():
            total_score += 20
            reasons.append("Preferred location is available (+20)")

        if lead.property_available:
            total_score += 20
            reasons.append("Property is available (+20)")

        if lead.business_experience or lead.previous_business_experience or lead.current_profession == CurrentProfession.BUSINESS:
            total_score += 10
            reasons.append("Business experience is present (+10)")

        if (lead.opening_timeline in [OpeningTimeline.WITHIN_2_MONTHS, OpeningTimeline.WITHIN_6_MONTHS]) or (lead.expected_start and any(term in lead.expected_start.lower() for term in ['3 month', '6 month', 'immediate'])):
            total_score += 20
            reasons.append("Expected start is within 6 months (+20)")

    # 5. Determine Qualification Status based on Score Thresholds
    if total_score >= 80:
        status = QualificationStatus.QUALIFIED
    elif total_score >= 50:
        status = QualificationStatus.REVIEW
    else:
        status = QualificationStatus.NOT_QUALIFIED

    # 6. Generate Reason Summary
    if reasons:
        reason_summary = "Qualification breakdown: " + ", ".join(reasons) + f". Total Score: {total_score}."
    else:
        reason_summary = "Does not currently meet minimum criteria. Total Score: 0."

    lead.qualification_score = total_score
    lead.qualification_status = status
    lead.qualification_reason = reason_summary

    if save:
        lead.save(update_fields=[
            'qualification_score', 'qualification_status', 'lead_temperature',
            'qualification_reason', 'follow_up_required', 'updated_at'
        ])

    return lead


