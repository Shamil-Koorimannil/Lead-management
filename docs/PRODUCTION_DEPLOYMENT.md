# Production Deployment & Infrastructure Guide
**Lead Management & Enquiry Automation Platform**

Target Architecture:
- **Server OS**: Ubuntu 24.04 LTS VPS (Hostinger / DigitalOcean / AWS EC2)
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy / SSL**: Caddy v2 (Automated Let's Encrypt HTTPS)
- **Frontend**: Nginx (Multi-stage container serving compiled Vite SPA `dist/`)
- **Backend**: Gunicorn WSGI (Django REST Framework)
- **Database**: PostgreSQL 15 (Isolated container network)

---

## 1. Initial VPS Setup & Dependencies

Connect to your Ubuntu 24.04 server via SSH:

```bash
ssh root@your-vps-ip
```

Update system packages and install Docker:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw ca-certificates gnupg

# Install Docker & Docker Compose Plugin
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable Docker on startup
sudo systemctl enable --now docker
```

Configure Firewall (UFW):

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 2. Application Setup & Environment Secrets

Clone the repository to `/opt/lead-management`:

```bash
sudo git clone https://github.com/Shamil-Koorimannil/Lead-management.git /opt/lead-management
cd /opt/lead-management
```

Generate secure production credentials:

```bash
# Generate a strong Django secret key
python3 -c 'import secretes; print(secrets.token_urlsafe(50))'
```

Create production `.env` file:

```bash
cat << 'EOF' > .env
# Production Django Environment
DJANGO_SECRET_KEY=YOUR_GENERATED_STRONG_SECRET_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,backend
DOMAIN=yourdomain.com

# PostgreSQL Credentials
POSTGRES_DB=lead_management_prod
POSTGRES_USER=lead_prod_user
POSTGRES_PASSWORD=YOUR_STRONG_DB_PASSWORD_HERE
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# CORS & CSRF Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend API URL
VITE_API_BASE_URL=https://yourdomain.com/api
EOF
```

---

## 3. Production Deployment Execution

Start production containers in detached mode:

```bash
docker compose up -d --build
```

Verify running containers:

```bash
docker compose ps
```

Run database migrations and collect static files:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

Seed initial administrative accounts & baseline qualification rules:

```bash
docker compose exec backend python manage.py seed_data
```

---

## 4. Automated Database Backup & Recovery

### Running Manual Backup
Execute the repository backup script:

```bash
chmod +x infrastructure/postgres/backup.sh
docker compose exec -T postgres sh -c "POSTGRES_DB=lead_management_prod POSTGRES_USER=lead_prod_user POSTGRES_PASSWORD=YOUR_STRONG_DB_PASSWORD_HERE pg_dump -h localhost -U lead_prod_user -d lead_management_prod --clean --if-exists | gzip" > backups/lead_mgmt_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Automated Daily Cron Job
Set up a daily backup cron job:

```bash
sudo crontab -e
```

Add the following line to run backups every night at 2:00 AM:

```cron
0 2 * * * cd /opt/lead-management && ./infrastructure/postgres/backup.sh ./backups >> /var/log/lead_mgmt_backup.log 2>&1
```

### Offsite Replication Requirement
> **CRITICAL**: Copy local backup archives to encrypted offsite object storage (AWS S3, Cloudflare R2, or Backblaze B2) using `rclone` or `aws-cli`:
```bash
rclone copy ./backups remote:your-bucket-name/backups/
```

### Database Restore Procedure
> **WARNING**: Overwrites existing database data.

```bash
chmod +x infrastructure/postgres/restore.sh
./infrastructure/postgres/restore.sh ./backups/lead_mgmt_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 5. Application Update & Rollback Procedures

### Updating Application to Latest Commit
```bash
cd /opt/lead-management
git pull origin main
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

### Rollback Procedure
If a deployment fails:
```bash
git checkout PREVIOUS_COMMIT_HASH
docker compose up -d --build
```

---

## 6. Logs & Diagnostics

View real-time production container logs:

```bash
# View backend Gunicorn logs
docker compose logs -f backend

# View Caddy SSL & proxy logs
docker compose logs -f caddy

# View PostgreSQL database logs
docker compose logs -f postgres

# View n8n workflow logs
docker compose logs -f n8n
```

---

## 7. Self-Hosted n8n Infrastructure & M2M Authentication

### Architecture & Security Isolation
- **Subdomain Routing**: Proxying via Caddy at `n8n.yourdomain.com` (`n8n.{$DOMAIN:localhost}`).
- **Network Boundaries**: n8n is connected strictly to `app_network` and exposes no public host ports.
- **Database Access Restriction**: n8n does NOT connect directly to PostgreSQL. All operations flow through Django API.
- **Machine-to-Machine Credentials**: n8n authenticates to Django using a dedicated API key (`X-Integration-Api-Key` or `Authorization: Api-Key <token>`).
- **Brand Isolation**: The Django server resolves `request.user.brand` strictly from the integration credential. Payload parameter `brand_id` cannot override or bypass brand authority.
- **Idempotency**: Django models track `IntegrationEvent(brand, external_event_id)` with a DB unique constraint. Duplicate webhook calls return the existing Lead with `X-Idempotent-Replay: true` without duplicating records.

### Credential Rotation
To rotate an integration token for a Brand:
1. In Django Admin or CLI:
   ```bash
   docker compose exec backend python manage.py shell -c "
   from integrations.models import IntegrationToken
   from users.models import Brand
   brand = Brand.objects.get(slug='zywo-franchise')
   token = IntegrationToken.objects.filter(brand=brand).first()
   token.key = IntegrationToken.generate_key()
   token.save()
   print('New Key:', token.key)
   "
   ```
2. Update the `X-Integration-Api-Key` in n8n HTTP Request node credentials or `.env`.

