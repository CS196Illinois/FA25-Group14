# Course Compass - Render Deployment Guide

This guide walks you through deploying Course Compass to Render.

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Supabase Account**: Your database at [supabase.com](https://supabase.com)

## Deployment Steps

### 1. Prepare Your Database (Supabase)

Ensure your Supabase database is set up:

```sql
-- Run this in Supabase SQL Editor if tables don't exist
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_requirements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    advanced_composition BOOLEAN DEFAULT FALSE,
    composition1 BOOLEAN DEFAULT FALSE,
    quantitative_reasoning1 BOOLEAN DEFAULT FALSE,
    quantitative_reasoning2 BOOLEAN DEFAULT FALSE,
    western_culture BOOLEAN DEFAULT FALSE,
    non_western_culture BOOLEAN DEFAULT FALSE,
    us_minority_culture BOOLEAN DEFAULT FALSE,
    language_requirement BOOLEAN DEFAULT FALSE,
    humanities_arts BOOLEAN DEFAULT FALSE,
    social_behavioral BOOLEAN DEFAULT FALSE,
    natural_sciences BOOLEAN DEFAULT FALSE,
    humanities_hp BOOLEAN DEFAULT FALSE,
    humanities_la BOOLEAN DEFAULT FALSE,
    social_behavioral_bsc BOOLEAN DEFAULT FALSE,
    social_behavioral_ss BOOLEAN DEFAULT FALSE,
    natural_sciences_ls BOOLEAN DEFAULT FALSE,
    natural_sciences_ps BOOLEAN DEFAULT FALSE,
    audit_uploaded BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    difficulty INTEGER CHECK (difficulty >= 1 AND difficulty <= 5),
    workload INTEGER CHECK (workload >= 1 AND workload <= 5),
    title VARCHAR(255),
    comment TEXT,
    semester_taken VARCHAR(20),
    professor VARCHAR(255),
    grade_received VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_flagged BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_flagged BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_review_course ON review(course_code);
CREATE INDEX IF NOT EXISTS idx_review_user ON review(user_id);
CREATE INDEX IF NOT EXISTS idx_message_course ON message(course_code);
CREATE INDEX IF NOT EXISTS idx_message_user ON message(user_id);
```

### 2. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin master
   ```

2. **Create New Web Service** in Render:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically

3. **Configure Environment Variables**:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon/public key
   - `SECRET_KEY`: Auto-generated (or set your own)
   - `FLASK_ENV`: production
   - `FLASK_DEBUG`: False

#### Option B: Manual Setup

1. **Create New Web Service**:
   - Name: `course-compass`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -c gunicorn_config.py run:app`

2. **Configure Settings**:
   - Branch: `master`
   - Region: Choose closest to your users
   - Instance Type: Free (or paid for better performance)

3. **Add Environment Variables** (in Render dashboard):
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   SECRET_KEY=<generate-a-long-random-string>
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=<your-supabase-anon-key>
   DATABASE_URL=<your-supabase-connection-string>
   ```

### 3. Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy these values:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon public key** → Use as `SUPABASE_KEY`
4. Navigate to **Settings** → **Database**
5. Copy the **Connection string** → Use as `DATABASE_URL`
   - Format: `postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres`

### 4. Deploy

Click **"Create Web Service"** or **"Manual Deploy"** to start deployment.

Render will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Start your app with Gunicorn
4. Provide you with a URL: `https://course-compass.onrender.com`

### 5. Post-Deployment

1. **Verify the deployment**:
   - Visit your Render URL
   - Test login/register
   - Check database connectivity

2. **Monitor logs**:
   - Go to your service in Render dashboard
   - Click "Logs" to see real-time application logs

3. **Set up custom domain** (optional):
   - Go to Settings → Custom Domains
   - Add your domain and configure DNS

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Check `DATABASE_URL` format:
   ```
   postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
   ```

2. Verify Supabase credentials are correct

3. Ensure tables are created (run SQL from step 1)

### Application Errors

1. **Check Render Logs**:
   - Dashboard → Your Service → Logs

2. **Common issues**:
   - Missing environment variables
   - Database connection string incorrect
   - Python version mismatch

3. **Debug mode** (temporary):
   - Set `FLASK_DEBUG=True` in Render env vars
   - Check detailed error messages
   - **Remember to set back to False for production!**

### Slow Performance

Free tier limitations:
- Spins down after 15 minutes of inactivity
- First request after spin-down is slow (cold start)

Solutions:
- Upgrade to paid tier ($7/month)
- Use external monitoring service to keep it alive
- Accept cold starts for free tier

## Updating Your App

Render auto-deploys on git push (if enabled):

```bash
git add .
git commit -m "Update feature"
git push origin master
```

Or manually trigger deploy in Render dashboard.

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_ENV` | Yes | Environment mode | `production` |
| `FLASK_DEBUG` | Yes | Debug mode | `False` |
| `SECRET_KEY` | Yes | Flask secret key | `<random-64-char-string>` |
| `SUPABASE_URL` | Yes | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Yes | Supabase anon key | `eyJhbGc...` |
| `DATABASE_URL` | Yes | PostgreSQL connection | `postgresql://...` |

## Security Checklist

- ✅ `FLASK_DEBUG=False` in production
- ✅ Strong `SECRET_KEY` (64+ random characters)
- ✅ Never commit `.env` file
- ✅ Use HTTPS (Render provides this automatically)
- ✅ Supabase Row Level Security enabled
- ✅ Regular backups of Supabase database

## Support

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
- **Flask Docs**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

## Cost Breakdown

### Free Tier
- Render Web Service: Free (with limitations)
- Supabase: Free (500MB database, 2GB bandwidth)
- **Total: $0/month**

### Paid Tier (Recommended for Production)
- Render Starter: $7/month (no cold starts, better performance)
- Supabase Pro: $25/month (8GB database, 50GB bandwidth)
- **Total: $32/month**

---

**Note**: Remember to migrate your SQLite data to Supabase before going live:
```bash
python migrate_sqlite_to_supabase.py
```
