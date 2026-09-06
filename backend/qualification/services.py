from decimal import Decimal
from leads.models import Lead, QualificationStatus
from .models import QualificationRule, OperatorChoices

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
    Evaluates hard disqualifiers, dynamic database rules, calculates total score,
    determines status (QUALIFIED, REVIEW, NOT_QUALIFIED) and generates reason summary.
    """
    # 1. Hard Disqualifier Check
    HARD_DISQUALIFIER_THRESHOLD = Decimal('1500000.00')  # ₹15,00,000
    if lead.investment_capacity is not None and lead.investment_capacity < HARD_DISQUALIFIER_THRESHOLD:
        lead.qualification_score = 0
        lead.qualification_status = QualificationStatus.NOT_QUALIFIED
        lead.qualification_reason = "Lead is not qualified because investment capacity is below the minimum threshold (₹15,00,000)."
        if save:
            lead.save(update_fields=['qualification_score', 'qualification_status', 'qualification_reason', 'updated_at'])
        return lead

    # 2. Fetch Active Brand Qualification Rules
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

        if lead.business_experience:
            total_score += 10
            reasons.append("Business experience is present (+10)")

        if lead.expected_start and any(term in lead.expected_start.lower() for term in ['3 month', '6 month', 'immediate']):
            total_score += 20
            reasons.append("Expected start is within 6 months (+20)")

    # 3. Determine Qualification Status based on Score Thresholds
    if total_score >= 80:
        status = QualificationStatus.QUALIFIED
    elif total_score >= 50:
        status = QualificationStatus.REVIEW
    else:
        status = QualificationStatus.NOT_QUALIFIED

    # 4. Generate Reason Summary
    if reasons:
        reason_summary = "Qualification breakdown: " + ", ".join(reasons) + f". Total Score: {total_score}."
    else:
        reason_summary = "Does not currently meet minimum criteria. Total Score: 0."

    lead.qualification_score = total_score
    lead.qualification_status = status
    lead.qualification_reason = reason_summary

    if save:
        lead.save(update_fields=['qualification_score', 'qualification_status', 'qualification_reason', 'updated_at'])

    return lead
