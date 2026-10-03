# Meta Instagram Messaging Integration & Webhook Setup Guide

This guide provides step-by-step instructions to connect an Instagram Professional account (such as `@coolcane_india`) with Meta Webhooks, n8n, and the Django Lead Management backend.

---

> [!IMPORTANT]
> **SAFETY GATE NOTICE**: Do NOT connect `@coolcane_india` or any production Instagram account to the live Meta Webhook until local verification, test suite execution, and staging validation are fully completed.

---

## 1. Meta App & Account Prerequisites

1. **Instagram Professional Account**: Ensure your account is converted to an Instagram **Business** or **Creator** account.
2. **Facebook Page Association**: Link the Instagram account to an authoritative Facebook Page under your Meta Business Manager.
3. **Meta Developer App**: Create a Meta App of type **Business** (or containing **Instagram Graph API**) on [developers.facebook.com](https://developers.facebook.com).

---

## 2. Meta Instagram API Login & Permission Flow

To interact with Instagram Direct Messages via Meta Graph API v19.0+, request and configure the following Meta permissions:

### Required Meta API Permissions:
- `instagram_basic`: Access basic profile information and account identity.
- `instagram_manage_messages`: Read and send Instagram DMs, webhooks for message events.
- `pages_show_list`: Retrieve associated Facebook Pages linked to the Instagram account.
- `pages_read_engagement`: Access Page engagement data required for webhook delivery.
- `pages_manage_metadata`: Manage webhooks and Page subscriptions.

### Access Token Generation Flow:
1. Open **Meta Business Manager** $\rightarrow$ **System Users** (or Meta Developer Access Token Tool).
2. Generate a **Long-Lived Page Access Token** (or System User Access Token) with the permissions above.
3. Connect the Access Token to your n8n integration workflow or backend environment variable (`META_PAGE_ACCESS_TOKEN`).

### Development vs Production Access:
- **Development Mode**: Standard DMs can only be received/sent between assigned **Meta App Testers** and the Instagram account.
- **Production Mode**: Submit the Meta App for **App Review** to obtain **Advanced Access** for `instagram_manage_messages` and `instagram_basic`.

---

## 3. Webhook Architecture: Live Setup vs. Local Verification

### A. Live Meta Webhook Setup (Production Mode)
In a live Meta setup, Meta servers send real-time HTTP POST notifications when an Instagram DM is received:
1. **Webhook Callback URL**: `https://<your-domain>/webhook/instagram` (routed via n8n / reverse proxy to Django).
2. **Verification Token**: Meta sends a `hub.challenge` GET request with a secret `hub.verify_token` matching your configured secret.
3. **Webhook Subscriptions**: In Meta Developer Dashboard $\rightarrow$ **Instagram Webhooks**, subscribe to:
   - `messages`
   - `messaging_postbacks`
4. **Signature Verification**: Validate the `X-Hub-Signature-256` header on incoming payloads using your Meta App Secret.

### B. Local Verification Flow (Development & Testing)
During development and automated testing, **no connection to live Meta webhooks is made**. Instead:
1. Automated unit tests execute locally using Django DRF test client against `/api/integrations/v1/instagram/process-message/`.
2. Requests use internal integration authentication: `X-Integration-API-Key: <IntegrationToken.key>`.
3. Event deduplication is validated using `external_event_id` and `external_message_id`.
4. Lead isolation, dynamic brand prompts, and progressive state machine logic are verified deterministically without hitting external Meta APIs or sending DMs to real users.

---

## 4. Environment Variables in n8n

Configure the following secrets in your n8n container / workflow:
- `META_PAGE_ACCESS_TOKEN`: Long-lived Meta Page Access Token (`instagram_manage_messages`).
- `DJANGO_API_URL`: Internal URL of the Django backend service (e.g., `http://backend:8000`).
- `N8N_INTEGRATION_TOKEN`: Active `IntegrationToken` secret generated for the Brand in Django.

---

## 5. Disconnecting or Pausing Automation

To pause or disconnect automated responses:
- Toggle off the workflow trigger in n8n UI, OR
- Set `is_automation_enabled = False` on the Target Lead/Conversation in Django dashboard.

