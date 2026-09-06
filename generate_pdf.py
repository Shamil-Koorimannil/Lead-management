import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to add 'Page X of Y' footers and running headers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Skip running header on cover page (Page 1)
        if self._pageNumber > 1:
            # Header line and text
            self.drawString(54, 750, "Lead Management & Enquiry Automation Platform — Technical Walkthrough & Roadmap")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer line and text (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.drawString(54, 32, "CONFIDENTIAL — Zywo Labs Engineering")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

def build_pdf(filename="Lead_Management_System_Walkthrough.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=64
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A")    # Deep Navy
    accent_blue = colors.HexColor("#2563EB")      # Vibrant Blue
    teal_accent = colors.HexColor("#0D9488")      # Teal
    dark_gray = colors.HexColor("#1E293B")        # Dark Slate
    body_gray = colors.HexColor("#334155")        # Slate Text
    light_bg = colors.HexColor("#F8FAFC")         # Off-white / Ice

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=accent_blue,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=accent_blue,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=body_gray,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=body_gray,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=dark_gray
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=primary_color
    )

    table_cell_normal = ParagraphStyle(
        'TableCellNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=body_gray
    )

    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # Title Banner Block
    story.append(Paragraph("Lead Management & Enquiry Automation Platform", title_style))
    story.append(Paragraph("System Architecture, Implemented Features & Strategic Roadmap", subtitle_style))
    story.append(Paragraph("<b>Author:</b> Zywo Labs Engineering Team &nbsp;|&nbsp; <b>Date:</b> September 2026 &nbsp;|&nbsp; <b>Version:</b> 1.0 (MVP Complete)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=15))

    # SECTION 1: EXECUTIVE SUMMARY
    story.append(Paragraph("1. Executive Summary & Core System Architecture", h1_style))
    story.append(Paragraph(
        "The <b>Lead Management & Enquiry Automation Platform</b> is a production-quality, self-hosted franchise enquiry handling system built to operate 100% independently without reliance on mandatory third-party automation tools. It provides authoritative multi-tenant data isolation, strict role-based access control (RBAC), automated rule-based qualification scoring, and dynamic operational portals for both Brand Owners and Sales Teams.",
        body_style
    ))

    # Tech Stack Box
    stack_data = [
        [Paragraph("<b>Component</b>", table_cell_header), Paragraph("<b>Technology & Pattern</b>", table_cell_header), Paragraph("<b>Responsibility</b>", table_cell_header)],
        [Paragraph("Frontend", table_cell_bold), Paragraph("React, TypeScript, Vite, Tailwind CSS, Lucide", table_cell_normal), Paragraph("Interactive UI, responsive views, state management", table_cell_normal)],
        [Paragraph("Backend API", table_cell_bold), Paragraph("Python, Django, Django REST Framework, SimpleJWT", table_cell_normal), Paragraph("Authoritative business logic, qualification engine, RBAC", table_cell_normal)],
        [Paragraph("Database", table_cell_bold), Paragraph("PostgreSQL", table_cell_normal), Paragraph("ACID compliant relational storage & lead sequence state", table_cell_normal)],
        [Paragraph("Infrastructure", table_cell_bold), Paragraph("Docker & Docker Compose", table_cell_normal), Paragraph("Containerized multi-service orchestration", table_cell_normal)],
    ]
    t_stack = Table(stack_data, colWidths=[80, 200, 224])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 10))

    # Security Principle Callout
    callout_data = [[
        Paragraph("<b>Mandatory Security Principle:</b> All permissions, queryset isolation, object-level security, and qualification calculations are strictly enforced by Django REST Framework on the backend. React acts purely as a presentation layer.", callout_style)
    ]]
    t_callout = Table(callout_data, colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINELEFT', (0,0), (0,0), 4, accent_blue),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 12))

    # SECTION 2: CURRENTLY IMPLEMENTED FEATURES
    story.append(Paragraph("2. Currently Implemented Features (MVP Status: Complete)", h1_style))
    
    story.append(Paragraph("2.1 Multi-Tenant & RBAC Hierarchy", h2_style))
    story.append(Paragraph("• <b>Organization & Brand Scoping:</b> Clear hierarchical isolation where Organizations own multiple Brands, and users/leads are scoped strictly per Brand.", bullet_style))
    story.append(Paragraph("• <b>Role-Based Access Control:</b> Three distinct roles configured with granular permissions:", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Brand Owner:</b> Full admin rights across leads, qualification rules, team management, analytics, and organization settings.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Sales Manager:</b> Access to all brand leads, activity logs, and sales portal views.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Sales Agent:</b> Scoped view restricted exclusively to leads assigned to them.", bullet_style))
    story.append(Paragraph("• <b>JWT Authentication & Flow:</b> Access and Refresh tokens with automatic client header injection and role-based route guards in React.", bullet_style))
    story.append(Paragraph("• <b>Organization Creation Flow:</b> Streamlined setup allowing new brand creation with automatic slug generation and owner initialization.", bullet_style))

    story.append(Paragraph("2.2 Atomic Lead Management & Lifecycle", h2_style))
    story.append(Paragraph("• <b>Atomic Lead Numbering:</b> Database transactions (`select_for_update`) ensure zero collision in sequence counters (e.g. `LEAD-000001`).", bullet_style))
    story.append(Paragraph("• <b>Comprehensive Lead Model:</b> Customer contact info (name, phone, email, city), preferred location, investment capacity (Decimal format), property availability, business experience, and start timeframe.", bullet_style))
    story.append(Paragraph("• <b>Sales Status Pipeline:</b> Complete lifecycle states: <code>NEW</code>, <code>CONTACTED</code>, <code>FOLLOW_UP</code>, <code>MEETING</code>, <code>NEGOTIATION</code>, <code>CONVERTED</code>, <code>LOST</code>.", bullet_style))
    story.append(Paragraph("• <b>Lead Assignment Engine:</b> Instant assignment to sales agents with recorded timestamp (`assigned_at`) and automatic activity log generation.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("2.3 Automated Lead Qualification Engine", h2_style))
    story.append(Paragraph("• <b>Hard Disqualification Rules:</b> Instant automated disqualification if key requirements are unmet (e.g. investment capacity below the minimum brand threshold, such as ₹15,00,000).", bullet_style))
    story.append(Paragraph("• <b>Weighted Point Scoring (0 to 100):</b> Configurable dynamic scoring engine calculating cumulative points:", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Investment Tier:</b> High (+30 points), Medium (+15 points).", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Location Match:</b> Target city/state match (+20 points).", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Property Ready:</b> Existing commercial location available (+20 points).", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Business Experience:</b> Prior retail/franchise background (+10 points).", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;- <b>Immediate Start:</b> Ready to launch within 0-3 months (+20 points).", bullet_style))
    story.append(Paragraph("• <b>Qualification Outcomes:</b> Automated status classification into <code>QUALIFIED</code> (score >= threshold), <code>REVIEW</code>, or <code>NOT_QUALIFIED</code>.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("2.4 Communications & Activity Audit Trail", h2_style))
    story.append(Paragraph("• <b>Unified Timeline:</b> Customer communication log (Inbound/Outbound via WhatsApp, Call, Email) displayed chronologically.", bullet_style))
    story.append(Paragraph("• <b>Internal Staff Notes:</b> Sales managers and agents can post internal notes on lead files for team collaboration.", bullet_style))
    story.append(Paragraph("• <b>System Audit Logs (`ActivityLog`):</b> Immutable audit record capturing lead creation, field updates, qualification status recalculations, agent assignments, and follow-up schedules.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("2.5 Dual Role-Tailored Web Portals", h2_style))

    # Feature Matrix Table
    portal_data = [
        [Paragraph("<b>Feature Area</b>", table_cell_header), Paragraph("<b>Owner Portal Capability</b>", table_cell_header), Paragraph("<b>Sales Portal Capability</b>", table_cell_header)],
        [
            Paragraph("Dashboard KPI", table_cell_bold),
            Paragraph("Total leads, qualification breakdown, conversion rates, brand performance", table_cell_normal),
            Paragraph("My assigned leads, urgent follow-ups today, recent activity queue", table_cell_normal)
        ],
        [
            Paragraph("Lead Table & Search", table_cell_bold),
            Paragraph("Filter by qualification status, lead source, assigned agent, date range", table_cell_normal),
            Paragraph("Search assigned leads, fast status toggling, call logging", table_cell_normal)
        ],
        [
            Paragraph("Lead Detail View", table_cell_bold),
            Paragraph("Full lead parameters, score breakdown, qualification reason, activity timeline", table_cell_normal),
            Paragraph("Customer info, notes log, follow-up scheduler, quick whatsapp launch", table_cell_normal)
        ],
        [
            Paragraph("Rule Management", table_cell_bold),
            Paragraph("Dynamic rule builder for hard disqualifiers and point weightings", table_cell_normal),
            Paragraph("Read-only qualification badge and reason display", table_cell_normal)
        ],
        [
            Paragraph("Team & Admin", table_cell_bold),
            Paragraph("Invite/create agents, assign roles, analytics dashboard, organization settings", table_cell_normal),
            Paragraph("Personal profile management, password updates", table_cell_normal)
        ]
    ]
    t_portal = Table(portal_data, colWidths=[100, 202, 202])
    t_portal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_portal)

    story.append(Spacer(1, 8))
    story.append(Paragraph("2.6 Automated Verification & Test Suite", h2_style))
    story.append(Paragraph("• <b>Seeded Test Environment (`seed_data`):</b> Instant populated dev database with pre-configured Brand Owner (`owner@zywolabs.com`), Sales Manager (`manager@zywolabs.com`), and Sales Agents (`agent1@zywolabs.com`, `agent2@zywolabs.com`).", bullet_style))
    story.append(Paragraph("• <b>Backend Automated Test Suite:</b> Pytest / Django unittest suite validating authentication security, object-level queryset isolation, qualification calculation accuracy, and cross-brand privacy integrity.", bullet_style))

    story.append(Spacer(1, 14))

    # SECTION 3: NEEDED IMPLEMENTATIONS
    story.append(Paragraph("3. Needed Implementations (Gap Analysis for Production)", h1_style))
    story.append(Paragraph("While the core MVP application and business logic are fully functional and validated, the following key modules are required for complete enterprise deployment and automated enquiry scaling:", body_style))

    gaps_data = [
        [Paragraph("<b>Category</b>", table_cell_header), Paragraph("<b>Module / Feature</b>", table_cell_header), Paragraph("<b>Description & Technical Requirement</b>", table_cell_header), Paragraph("<b>Priority</b>", table_cell_header)],
        [
            Paragraph("Automation", table_cell_bold),
            Paragraph("WhatsApp Cloud API Integration", table_cell_normal),
            Paragraph("Inbound webhook receiver to parse incoming customer WhatsApp messages into the conversation timeline; Outbound template messaging for instant automated qualification responses.", table_cell_normal),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", table_cell_normal)
        ],
        [
            Paragraph("AI Engine", table_cell_bold),
            Paragraph("LLM Lead Parameter Extractor", table_cell_normal),
            Paragraph("OpenAI / LLM pipeline to automatically analyze raw chat transcripts and extract investment budget, city, property state, and timeline into structured Django Lead fields.", table_cell_normal),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", table_cell_normal)
        ],
        [
            Paragraph("Integrations", table_cell_bold),
            Paragraph("n8n Workflow Bridge", table_cell_normal),
            Paragraph("Webhook emission engine and n8n workflow triggers for external CRM sync, Meta Ads lead form webhooks, and automated email drip campaigns.", table_cell_normal),
            Paragraph("<font color='#D97706'><b>MEDIUM</b></font>", table_cell_normal)
        ],
        [
            Paragraph("Real-Time", table_cell_bold),
            Paragraph("Live Push Notifications", table_cell_normal),
            Paragraph("WebSocket / Server-Sent Events (SSE) notification bell alerting agents immediately when a new lead is assigned or a high-score lead registers.", table_cell_normal),
            Paragraph("<font color='#D97706'><b>MEDIUM</b></font>", table_cell_normal)
        ],
        [
            Paragraph("Reporting", table_cell_bold),
            Paragraph("CSV / PDF Export Engine", table_cell_normal),
            Paragraph("One-click CSV/Excel export for lead lists, qualification summary reports, and agent performance funnels in the Owner Portal.", table_cell_normal),
            Paragraph("<font color='#2563EB'><b>NORMAL</b></font>", table_cell_normal)
        ],
        [
            Paragraph("DevOps", table_cell_bold),
            Paragraph("Production Caddy & SSL Setup", table_cell_normal),
            Paragraph("Caddy reverse proxy configuration for automated Let's Encrypt SSL/TLS certs, rate limiting, and PostgreSQL automated backup scripts.", table_cell_normal),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", table_cell_normal)
        ]
    ]
    t_gaps = Table(gaps_data, colWidths=[70, 110, 254, 70])
    t_gaps.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_gaps)

    story.append(Spacer(1, 14))

    # SECTION 4: STRATEGIC NEXT STEPS & ROADMAP
    story.append(Paragraph("4. Strategic Next Steps & Phased Execution Plan", h1_style))
    story.append(Paragraph("To transition seamlessly from the current working MVP to a fully automated production system, the following 3-phase execution roadmap is recommended:", body_style))

    # Roadmap Phase Cards
    story.append(Paragraph("Phase 1: Platform Polish & Lead Export (Week 1)", h2_style))
    story.append(Paragraph("1. <b>Implement CSV / Excel Export:</b> Add export backend API endpoint and UI download buttons in <code>OwnerLeads.tsx</code> and <code>OwnerLeadDetail.tsx</code>.", bullet_style))
    story.append(Paragraph("2. <b>Notification Badge System:</b> Add visual indicator for overdue follow-ups and unassigned leads on the Sales and Owner dashboards.", bullet_style))
    story.append(Paragraph("3. <b>Enhanced Filters:</b> Add multi-select filtering by budget ranges, cities, and specific lead sources.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Phase 2: Communication & AI Automation (Weeks 2 - 3)", h2_style))
    story.append(Paragraph("1. <b>WhatsApp Webhook Endpoint:</b> Build <code>backend/integrations/whatsapp_views.py</code> to handle inbound WhatsApp messages, matching phone numbers to existing leads or creating new leads automatically.", bullet_style))
    story.append(Paragraph("2. <b>AI Extract Service:</b> Deploy lightweight LLM parser function in <code>backend/qualification/services.py</code> to automatically extract structured values (investment, city, property) from raw customer text.", bullet_style))
    story.append(Paragraph("3. <b>n8n Orchestration Workflows:</b> Connect n8n workflows for inbound Facebook/Instagram Ads webhook triggers directly into Django API.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Phase 3: Security Hardening & Production Deployment (Week 4)", h2_style))
    story.append(Paragraph("1. <b>Production Infrastructure:</b> Finalize <code>infrastructure/caddy/Caddyfile</code> with HTTPS domain routing and static asset compression.", bullet_style))
    story.append(Paragraph("2. <b>Database Resilience:</b> Configure daily automated encrypted PostgreSQL backups and environment variable secret storage.", bullet_style))
    story.append(Paragraph("3. <b>End-to-End Load & Security Audit:</b> Run cross-tenant penetration testing and concurrent lead creation benchmarks.", bullet_style))

    story.append(Spacer(1, 14))
    
    # Conclusion Box
    concl_data = [[
        Paragraph("<b>Summary & Conclusion:</b> The Lead Management & Enquiry Automation Platform has achieved a complete, robust MVP status with all core models, security isolation, scoring logic, and UI portals operating smoothly. Proceeding with Phase 1 polish and Phase 2 integrations will deliver a market-ready automated franchise lead engine.", callout_style)
    ]]
    t_concl = Table(concl_data, colWidths=[504])
    t_concl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINELEFT', (0,0), (0,0), 4, teal_accent),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BBF7D0")),
    ]))
    story.append(t_concl)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    build_pdf()
