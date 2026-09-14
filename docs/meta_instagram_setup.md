# Meta Instagram Messaging Integration & Webhook Setup Guide

This guide provides step-by-step instructions to connect the `@coolcane_india` Instagram Professional account with Meta Webhooks, n8n, and the Django Lead Management backend.

---

## 1. Prerequisites & Account Setup

1. **Instagram Professional Account**: Ensure `@coolcane_india` is converted to an Instagram Business or Creator account.
2. **Facebook Page Link**: Connect `@coolcane_india` to an authoritative Facebook Page under your Meta Business Manager.
3. **Meta Developer App**: Create a Meta App of type **Business** on [developers.facebook.com](https://developers.facebook.com).

---

## 2. Meta App Configuration & Webhook Setup

1. In the Meta Developer Dashboard, add the **Instagram Graph API** product to your app.
2. Under **Webhooks** $\rightarrow$ **Instagram**:
   - **Callback URL**: `https://<your-n8n-domain>/webhook/instagram-webhook`
   - **Verify Token**: Generate a secure random string (e.g. `coolcane_ig_sec_token_2026`).
   - **Subscriptions**: Subscribe to `messages` and `messaging_postbacks`.
3. Test Webhook verification challenge to ensure n8n / Caddy routes requests properly.

---

## 3. Required Meta Permissions

Request the following Meta API permissions:
- `instagram_basic`
- `instagram_manage_messages`
- `pages_manage_metadata`
- `pages_read_engagement`

> [!NOTE]
> During development, test DMs can be received from assigned Meta App Testers.
> For production access across all Instagram users, submit the app for **Meta App Review / Advanced Access**.

---

## 4. Environment Variables in n8n

Configure the following environment secrets in your n8n container:
- `META_PAGE_ACCESS_TOKEN`: Long-lived Meta Page Access Token with `instagram_manage_messages` scope.
- `DJANGO_API_URL`: Internal URL of the Django service (e.g., `http://backend:8000`).
- `N8N_INTEGRATION_TOKEN`: Active `IntegrationToken` secret generated for the CoolCane Brand in Django.

---

## 5. End-to-End Testing Procedure

1. **Send Test Instagram DM**: Send a direct message to `@coolcane_india` from a test Instagram user.
2. **Verify Qualification Flow**:
   - First Message $\rightarrow$ Bot sends greeting and Investment range question.
   - Reply `"10 lakh"` $\rightarrow$ Bot asks Current Profession.
   - Reply `"Business owner"` $\rightarrow$ Bot asks Business Duration.
   - Reply `"3 years"` $\rightarrow$ Bot asks Location.
   - Reply `"Kochi"` $\rightarrow$ Bot asks Opening Timeline.
   - Reply `"Within 2 months"` $\rightarrow$ Bot sends thank you message and updates lead to `HOT`.
3. **Verify Disqualification**:
   - Send `"5 lakh"` $\rightarrow$ Bot sends polite minimum threshold message and halts further questions. Lead is marked `DISQUALIFIED`.
4. **Human Handoff Verification**:
   - When a sales agent opens the lead detail and updates status or sends a message, `is_automation_enabled` halts bot replies.

---

## 6. Disconnecting Automation

To pause or disconnect automated responses:
- Disable the workflow in n8n UI, OR
- Set `is_automation_enabled = False` on the Target Lead/Conversation in Django.
