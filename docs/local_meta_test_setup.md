# Local Meta Instagram End-to-End Test Setup Guide

This document provides step-by-step instructions for manually configuring Meta Developer Console, n8n, and a local public secure tunnel to perform a real end-to-end Instagram DM test without deploying to VPS.

---

> [!IMPORTANT]
> **SAFETY GATE & CREDENTIAL POLICY**:
> - Never hardcode real Meta Access Tokens, App Secrets, or Integration API Keys into Git.
> - Store all secrets in local environment variables (`.env`) or n8n credential settings.
> - Only test using assigned Meta App Testers before App Review / Advanced Access is granted.

---

## 1. Prerequisites

1. **Instagram Professional Account**: Converted to a **Business** or **Creator** profile.
2. **Facebook Page Link**: Instagram profile linked to a Facebook Page under Meta Business Suite.
3. **Meta Developer App**: Created on [developers.facebook.com](https://developers.facebook.com) (App Type: **Business**).
4. **Secure Tunnel Tool**: `cloudflared` or `ngrok` installed on the host machine.
5. **Docker Desktop**: Running locally (or local Python + n8n instance active).

---

## 2. Meta API Permissions

Configure the following Meta Graph API permissions in your Meta App:

- `instagram_basic`: Profile & account identity lookup.
- `instagram_manage_messages`: Access to Instagram Direct Messages & Webhook events.
- `pages_show_list`: Enumerate Facebook Pages linked to the Instagram account.
- `pages_read_engagement`: Access Page engagement data required for webhook delivery.

---

## 3. Required Environment Variables & Secrets Mapping

| Variable Name | Description | Where It Belongs | Placeholder Value |
|---|---|---|---|
| `META_PAGE_ACCESS_TOKEN` | Long-Lived Page Access Token with `instagram_manage_messages` | n8n Workflow Environment / Secrets | `<SET_LOCALLY_IN_N8N>` |
| `META_VERIFY_TOKEN` | Custom string for Meta Webhook verification handshake (`hub.verify_token`) | n8n Webhook / Reverse Proxy | `<SET_LOCALLY_MY_SECRET_VERIFY_TOKEN>` |
| `N8N_INTEGRATION_TOKEN` | Active `IntegrationToken.key` generated for the target Brand in Django | n8n Workflow Request Header | `<SET_LOCALLY_N8N_SEC_TOKEN>` |
| `DJANGO_API_URL` | Base URL of Django backend | n8n Workflow Environment | `http://backend:8000` (Docker) or `http://localhost:8000` |

---

## 4. Step-by-Step Manual Setup Instructions

### Step 1: Start Local Docker Stack & Services
1. Launch **Docker Desktop**.
2. Open terminal in workspace root and start stack:
   ```powershell
   docker compose up -d
   ```
3. Verify containers are healthy:
   ```powershell
   docker compose ps
   ```

### Step 2: Establish Secure Tunnel to Local n8n Webhook
1. In terminal, launch tunnel forwarding to local n8n (port 5678):
   ```powershell
   # Using ngrok:
   ngrok http 5678

   # OR using cloudflared:
   cloudflared tunnel --url http://localhost:5678
   ```
2. Copy the generated public HTTPS URL (e.g., `https://a1b2c3d4.ngrok-free.app`).

### Step 3: Configure Webhook in Meta Developer Console
1. Navigate to **Meta Developer Console** $\rightarrow$ **Your App** $\rightarrow$ **Instagram** $\rightarrow$ **Configuration**.
2. Click **Edit Webhook URL**.
3. **Callback URL**: Enter `https://<YOUR_TUNNEL_URL>/webhook/instagram-webhook`
4. **Verify Token**: Enter your secret `META_VERIFY_TOKEN`.
5. Click **Verify and Save**. (Meta sends a GET request with `hub.challenge` which n8n validates).
6. Under **Webhook Subscriptions**, subscribe to:
   - `messages`
   - `messaging_postbacks`

### Step 4: Add Meta App Testers (Development Mode Safety)
1. Navigate to **App Roles** $\rightarrow$ **Roles** in Meta Developer Console.
2. Add your personal Instagram user account as an **Instagram Tester**.
3. Accept the tester invitation inside Instagram app: **Settings** $\rightarrow$ **Apps and Websites** $\rightarrow$ **Tester Invites**.

### Step 5: Perform Controlled Instagram DM Test
1. From the assigned tester account, send an Instagram Direct Message to your test Business account:
   > *"10 lakh"*
2. Observe local execution:
   - Meta sends webhook payload $\rightarrow$ Tunnel $\rightarrow$ local n8n.
   - n8n calls Django Integration API (`/api/integrations/v1/instagram/process-message/`).
   - Django updates state to `WAITING_PROFESSION` and returns prompt text.
   - n8n receives reply text and calls Meta Graph API (`/v18.0/me/messages`).
3. Verify reply received in Instagram DM:
   > *"Thank you! What is your current profession? ..."*

### Step 6: Safe Teardown / Disconnection
- To pause automated replies immediately:
  - Stop the tunnel process in PowerShell (`Ctrl + C`), OR
  - Deactivate workflow in n8n UI, OR
  - Set `is_automation_enabled = False` on the conversation in Django Admin.

---

## 5. Verification Checklist & Status

- [x] Local simulation runner created (`python backend/manage.py simulate_instagram_dm`)
- [x] Phase 9 qualification matrix scenarios verified (11/11 PASSED)
- [x] n8n workflow Graph API URL typo fixed
- [ ] Docker Desktop running (*Requires manual start by User*)
- [ ] Secure Tunnel running (`ngrok` / `cloudflared`) (*Requires manual setup by User*)
- [ ] Meta Developer Console configured (*Requires manual setup by User*)
- [ ] Live Instagram DM verified (*Requires manual execution by User*)

> [!NOTE]
> Requires manual verification in Meta Developer Console.
