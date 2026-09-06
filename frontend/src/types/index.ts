export type UserRole = 'BRAND_OWNER' | 'SALES_MANAGER' | 'SALES_AGENT';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: UserRole;
  brand: number | null;
  brand_name: string | null;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
}

export type LeadSource =
  | 'MANUAL'
  | 'TEST'
  | 'WHATSAPP'
  | 'WEBSITE'
  | 'INSTAGRAM'
  | 'FACEBOOK'
  | 'GOOGLE_ADS'
  | 'OTHER';

export type SalesStatus =
  | 'NEW'
  | 'CONTACTED'
  | 'FOLLOW_UP'
  | 'MEETING'
  | 'NEGOTIATION'
  | 'CONVERTED'
  | 'LOST';

export type QualificationStatus = 'QUALIFIED' | 'REVIEW' | 'NOT_QUALIFIED';

export type FollowUpType = 'CALL' | 'WHATSAPP' | 'MEETING' | 'EMAIL' | 'OTHER';

export interface ActivityLog {
  id: number;
  lead: number;
  actor: number | null;
  actor_name: string | null;
  action: string;
  description: string;
  created_at: string;
}

export interface Lead {
  id: number;
  brand: number;
  lead_number: string;
  name: string;
  phone: string;
  email: string;
  city: string;
  preferred_location: string;
  investment_capacity: string | number | null;
  property_available: boolean;
  business_experience: boolean;
  expected_start: string;
  lead_source: LeadSource;
  qualification_score: number;
  qualification_status: QualificationStatus;
  qualification_reason: string;
  follow_up_required: boolean;
  next_follow_up_at: string | null;
  follow_up_type: FollowUpType | null;
  follow_up_note: string;
  sales_status: SalesStatus;
  assigned_to: number | null;
  assigned_to_name?: string | null;
  assigned_to_detail?: User | null;
  assigned_at: string | null;
  activities?: ActivityLog[];
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation: number;
  direction: 'INBOUND' | 'OUTBOUND';
  message: string;
  message_type: 'TEXT' | 'IMAGE' | 'DOCUMENT' | 'SYSTEM' | 'AI' | 'NOTE';
  external_message_id?: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  lead: number;
  lead_number: string;
  channel: LeadSource;
  status: 'OPEN' | 'CLOSED';
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface LeadNote {
  id: number;
  lead: number;
  author: number;
  author_name: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface QualificationRule {
  id: number;
  brand: number;
  name: string;
  field: string;
  operator: 'gte' | 'lte' | 'eq' | 'contains' | 'is_true' | 'is_false';
  operator_display: string;
  value: string;
  score: number;
  active: boolean;
  priority: number;
  created_at: string;
  updated_at: string;
}

export interface OwnerDashboardData {
  total_leads: number;
  qualified: number;
  review: number;
  not_qualified: number;
  conversion_rate: number;
  avg_qualification_score: number;
  active_followups: number;
  converted: number;
  lost: number;
  sales_funnel: { sales_status: SalesStatus; count: number }[];
  lead_sources: { lead_source: LeadSource; count: number }[];
  locations: { city: string; count: number }[];
  team_performance: {
    id: number;
    name: string;
    email: string;
    role: UserRole;
    assigned_leads: number;
    qualified_leads: number;
    converted_leads: number;
  }[];
}

export interface SalesDashboardData {
  metrics: {
    new_leads: number;
    qualified_leads: number;
    followups_due: number;
    meetings_today: number;
    priority_leads: number;
  };
  overdue_followups: Lead[];
  upcoming_followups: Lead[];
  recently_qualified: Lead[];
}
