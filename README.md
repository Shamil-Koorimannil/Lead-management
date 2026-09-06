# Lead Management & Enquiry Automation Platform — MVP

Production-quality, self-hosted Lead Management & Enquiry Automation Platform built for franchise enquiry management.

This core application MVP runs 100% independently without any external automation service or third-party dependency.

---

## Tech Stack Architecture

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui design patterns, Lucide Icons
- **Backend**: Python, Django, Django REST Framework, SimpleJWT (JWT Authentication), django-filters, CORS Headers
- **Database**: PostgreSQL
- **Infrastructure**: Docker & Docker Compose

---

## Core System Architecture

```
React (Presentation & Interactions)
  ↓
Django REST Framework (Authoritative Business Logic, Authentication, Authorization & Qualification Engine)
  ↓
PostgreSQL (Source of Truth)
```

> **Mandatory Security Principle**: Django REST Framework enforces all permission scoping, queryset isolation, object-level security, and qualification calculations. React handles UI rendering only.

---

## Directory Structure

```
lead-management-system/
├── frontend/             # React + TypeScript + Vite + Tailwind UI
├── backend/              # Django REST Framework Modular Monolith
│   ├── config/           # Core settings, WSGI, main URL routing
│   ├── users/            # Custom User model, Organization, Brand, Auth APIs
│   ├── leads/            # Lead CRUD, Atomic Lead Numbering, Dashboard APIs
│   ├── qualification/    # Qualification Engine & Dynamic Scoring Rules
│   ├── conversations/    # Customer Messages & Internal Staff Notes
│   └── integrations/     # Future Integration Boundary Placeholders
├── infrastructure/
│   ├── docker-compose.yml # Postgres, Backend, Frontend container orchestration
│   └── caddy/            # Future VPS reverse proxy configuration
├── n8n/
│   └── workflows/        # Placeholder for future n8n workflow definitions
├── docs/                 # Platform architecture documentation
├── .env.example          # Environment variables template
├── .gitignore
└── README.md
```

---

## Local Quickstart & Development Setup

### Option 1: Docker Compose (Recommended)

1. **Clone & Set Up Environment**:
   ```bash
   cp .env.example .env
   ```

2. **Start Infrastructure Services**:
   ```bash
   docker-compose up -d --build
   ```

3. **Run Database Migrations & Seed Test Data**:
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py seed_data
   ```

4. **Access the Applications**:
   - **Frontend App**: `http://localhost:5173`
   - **Django API Root**: `http://localhost:8000/api/`
   - **Django Admin**: `http://localhost:8000/admin/`

---

## Development Credentials (Seeded)

The `seed_data` command creates test credentials:

| Role | Email | Password | Access Scope |
|---|---|---|---|
| **Brand Owner** | `owner@zywolabs.com` | `Password123!` | Full brand access (Leads, Analytics, Team, Rules, Settings) |
| **Sales Manager** | `manager@zywolabs.com` | `Password123!` | Brand team leads & operational sales portal |
| **Sales Agent 1** | `agent1@zywolabs.com` | `Password123!` | Assigned leads only (`LEAD-000001`, `LEAD-000003`) |
| **Sales Agent 2** | `agent2@zywolabs.com` | `Password123!` | Assigned leads only (`LEAD-000002`) |

---

## Test Data Verification Matrix

| Lead # | Customer | Investment | Location | Expected Qualification | Expected Reason |
|---|---|---|---|---|---|
| **LEAD-000001** | Ahmed | ₹50,00,000 | Kochi | **QUALIFIED (100)** | Investment >= ₹25L (+30), Location (+20), Property (+20), Experience (+10), Start (+20) |
| **LEAD-000002** | Rahul | ₹10,00,000 | Kochi | **NOT_QUALIFIED (0)** | **Hard Disqualified**: Investment capacity below ₹15,00,000 minimum threshold |
| **LEAD-000003** | Arjun | ₹30,00,000 | Bangalore | **QUALIFIED (80)** | Investment >= ₹25L (+30), Location (+20), Experience (+10), Start (+20) |

---

## Running Automated Test Suite

To run the backend pytest / Django unittest suite verifying authentication, object-level permissions, qualification calculations, hard disqualifiers, and cross-brand security:

```bash
# Inside docker container or local venv:
python manage.py test
```

To run frontend TypeScript type-checking and production build validation:

```bash
cd frontend
npm run build
```

---

## Future Integration Boundaries (Phase 2 Roadmap)

This MVP leaves clean architectural boundaries for future automation additions:

- **n8n**: Workflow orchestration calling Django REST endpoints to create/update leads.
- **OpenAI**: NLP processing converting unstructured messages into structured lead parameters.
- **WhatsApp Meta Cloud API**: Inbound/Outbound message webhook handlers.
