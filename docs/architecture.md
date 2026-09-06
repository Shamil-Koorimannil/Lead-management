# Platform Architecture Overview

## Data Flow
React UI -> Django REST API -> PostgreSQL

## Security Matrix
- BRAND_OWNER: Full brand scope access (all leads, team, rules, analytics)
- SALES_MANAGER: Team scope access
- SALES_AGENT: Assigned lead scope access only

## Qualification Engine
- Hard Disqualifier check first (e.g. Investment < ₹15,00,000 -> NOT_QUALIFIED)
- Active rule evaluation & dynamic score accumulation (80+: QUALIFIED, 50-79: REVIEW, 0-49: NOT_QUALIFIED)
- Server-side calculation only (Django authoritative source of truth)
