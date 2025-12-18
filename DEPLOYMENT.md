# PromptLab Deployment Guide

Step-by-step instructions to deploy PromptLab to production.

---

## Step 1: Set Up Stripe

### 1.1 Create Stripe Account
1. Go to [stripe.com](https://stripe.com) and create an account
2. Complete business verification

### 1.2 Create Products and Prices
1. Go to **Products** in Stripe Dashboard
2. Click **+ Add product**

**Create Pro Plan:**
- Name: `PromptLab Pro`
- Description: `50,000 requests/month, 100 optimizations, 90-day retention`
- Click **Add pricing**:
  - Price: `$99.00`
  - Billing period: `Monthly`
  - Click **Save**
- Copy the **Price ID** (starts with `price_`)

**Create Team Plan:**
- Name: `PromptLab Team`
- Description: `500,000 requests/month, unlimited optimizations, 1-year retention`
- Click **Add pricing**:
  - Price: `$299.00`
  - Billing period: `Monthly`
  - Click **Save**
- Copy the **Price ID** (starts with `price_`)

### 1.3 Get API Keys
1. Go to **Developers > API keys**
2. Copy your **Secret key** (starts with `sk_live_` for production)

### 1.4 Set Up Webhook
1. Go to **Developers > Webhooks**
2. Click **+ Add endpoint**
3. Endpoint URL: `https://your-api-domain.com/billing/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy the **Signing secret** (starts with `whsec_`)

---

## Step 2: Set Up Production Database

### Option A: Managed PostgreSQL (Recommended)

**Using Supabase (Free tier available):**
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to **Settings > Database**
4. Copy the **Connection string** (URI format)
5. Replace `[YOUR-PASSWORD]` with your database password

**Using Railway:**
1. Go to [railway.app](https://railway.app)
2. Click **New Project > Provision PostgreSQL**
3. Click on the database, go to **Connect**
4. Copy the **DATABASE_URL**

**Using Neon (Free tier available):**
1. Go to [neon.tech](https://neon.tech)
2. Create new project
3. Copy the connection string

### Option B: Self-Hosted
```bash
# On your server
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE promptlab;
CREATE USER promptlab WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE promptlab TO promptlab;
\q
```

---

## Step 3: Deploy Backend

### Option A: Railway (Recommended for simplicity)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click **New Project > Deploy from GitHub repo**
4. Select your repository
5. Railway will auto-detect the Python app
6. Add environment variables in **Variables** tab:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/promptlab
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_TEAM=price_...
APP_URL=https://your-frontend-domain.com
```

7. Set **Root Directory** to `backend`
8. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
9. Deploy and copy the generated URL

### Option B: Render

1. Go to [render.com](https://render.com)
2. Click **New > Web Service**
3. Connect your GitHub repo
4. Configure:
   - Name: `promptlab-api`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as above)
6. Click **Create Web Service**

### Option C: DigitalOcean App Platform

1. Go to [cloud.digitalocean.com/apps](https://cloud.digitalocean.com/apps)
2. Click **Create App**
3. Connect GitHub repo
4. Configure component:
   - Source Directory: `/backend`
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
5. Add environment variables
6. Deploy

---

## Step 4: Deploy Frontend

### Option A: Vercel (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Click **New Project**
3. Import your GitHub repo
4. Configure:
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
5. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-url.com
   ```
6. Click **Deploy**

**Update API base URL in frontend:**

Edit `frontend/src/lib/api.ts`:
```typescript
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : "http://localhost:8000/api/v1"
```

### Option B: Netlify

1. Go to [netlify.com](https://netlify.com)
2. Click **Add new site > Import an existing project**
3. Connect GitHub repo
4. Configure:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
5. Add environment variable: `VITE_API_URL`
6. Deploy

### Option C: Cloudflare Pages

1. Go to [pages.cloudflare.com](https://pages.cloudflare.com)
2. Click **Create a project**
3. Connect GitHub repo
4. Configure:
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `frontend/dist`
5. Add environment variable: `VITE_API_URL`
6. Deploy

---

## Step 5: Configure Domain (Optional but Recommended)

### 5.1 Purchase Domain
- [Namecheap](https://namecheap.com)
- [Google Domains](https://domains.google)
- [Cloudflare Registrar](https://cloudflare.com)

### 5.2 Configure DNS

**For frontend (e.g., promptlab.io):**
- Add CNAME record pointing to your Vercel/Netlify domain

**For backend API (e.g., api.promptlab.io):**
- Add CNAME record pointing to your Railway/Render domain

### 5.3 Update URLs
1. Update `APP_URL` in backend environment to `https://promptlab.io`
2. Update `VITE_API_URL` in frontend to `https://api.promptlab.io`
3. Update Stripe webhook URL to `https://api.promptlab.io/billing/webhook`

---

## Step 6: Update CORS Settings

Edit `backend/app/main.py` for production:

```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://promptlab.io",
        "https://www.promptlab.io",
        # Add any other domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 7: Final Checklist

### Pre-Launch Testing
- [ ] Create test organization
- [ ] Log a test request via SDK
- [ ] Test prompt optimization
- [ ] Test Stripe checkout (use test mode first)
- [ ] Verify webhook receives events
- [ ] Test subscription upgrade/downgrade
- [ ] Verify usage limits work

### Security Checklist
- [ ] All API keys are in environment variables (not in code)
- [ ] CORS is configured for production domains only
- [ ] HTTPS is enabled on all endpoints
- [ ] Database has strong password
- [ ] Stripe is in live mode (not test mode)

### Go Live Steps
1. Switch Stripe to **live mode**
2. Update Stripe API keys to live keys
3. Create new webhook with live endpoint
4. Update webhook secret
5. Test a real payment with small amount
6. Monitor logs for errors

---

## Step 8: Post-Launch

### Monitoring
- Set up error tracking (Sentry)
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor Stripe dashboard for payments

### Analytics
- Add Google Analytics or Plausible to frontend
- Track key conversion metrics

### Backup
- Enable automated database backups
- Test restore process

---

## Quick Reference: Environment Variables

### Backend (.env)
```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/promptlab
OPENAI_API_KEY=sk-...

# Stripe (required for payments)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_TEAM=price_...

# App
APP_URL=https://promptlab.io
```

### Frontend
```bash
VITE_API_URL=https://api.promptlab.io
```

---

## Troubleshooting

### Database Connection Issues
- Ensure DATABASE_URL uses `postgresql+asyncpg://` prefix
- Check if database allows connections from your server IP
- Verify SSL settings if required

### Stripe Webhook Not Working
- Check webhook signing secret is correct
- Verify endpoint URL is accessible
- Check webhook logs in Stripe Dashboard

### CORS Errors
- Ensure frontend domain is in allow_origins list
- Check for trailing slashes in URLs
- Verify credentials are being sent correctly

### 502/503 Errors
- Check backend logs for startup errors
- Verify all environment variables are set
- Check memory/CPU limits on hosting platform
