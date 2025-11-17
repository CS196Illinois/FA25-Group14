# Environment Variables Configuration

This file documents all environment variables needed for Course Compass.

## Development (.env file)

Create a `.env` file in the project root with these variables:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Optional: Google Gemini AI
GOOGLE_API_KEY=your-google-api-key-here

# Optional: Server Configuration
PORT=5000
```

## Production (Render Dashboard)

Set these environment variables in the Render dashboard:

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Sets Flask to production mode |
| `FLASK_DEBUG` | `False` | Disables debug mode (security) |
| `SECRET_KEY` | `<64-char-random-string>` | Flask session security |
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | Your Supabase project URL |
| `SUPABASE_KEY` | `eyJhbGc...` | Your Supabase anon/public key |
| `DATABASE_URL` | `postgresql://postgres:...` | Supabase connection string |

### Optional Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `GOOGLE_API_KEY` | `AIza...` | For AI course recommendations |
| `PORT` | `10000` | Auto-set by Render |

## How to Get Supabase Credentials

1. **Go to your Supabase project**: https://app.supabase.com
2. **Navigate to Settings → API**
3. **Copy these values**:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon public key** → Use as `SUPABASE_KEY`
4. **Navigate to Settings → Database**
5. **Connection string** → Use as `DATABASE_URL`
   - Format: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

## How to Get Google Gemini API Key

1. **Go to**: https://ai.google.dev/
2. **Click "Get API key"**
3. **Create a new API key**
4. **Copy the key** → Use as `GOOGLE_API_KEY`

## Generating a Secure SECRET_KEY

### Method 1: Python
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Method 2: OpenSSL
```bash
openssl rand -hex 32
```

### Method 3: Online (use with caution)
Visit: https://randomkeygen.com/ (CodeIgniter Encryption Keys)

## Security Best Practices

✅ **DO:**
- Use strong, random SECRET_KEY (64+ characters)
- Set FLASK_DEBUG=False in production
- Keep .env file out of git (add to .gitignore)
- Use different SECRET_KEY for dev and production
- Rotate SECRET_KEY periodically
- Use environment variables in Render (never hardcode)

❌ **DON'T:**
- Commit .env file to git
- Use the same SECRET_KEY across environments
- Share API keys publicly
- Use weak or default SECRET_KEY values
- Enable debug mode in production

## Verifying Configuration

### Local Development
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('SUPABASE_URL:', os.getenv('SUPABASE_URL')[:30] + '...')"
```

### Production (Render)
Check the Render dashboard → Your Service → Environment

## Troubleshooting

### Issue: "SECRET_KEY not set"
**Solution**: Add SECRET_KEY to your .env file or Render environment variables

### Issue: "Could not find the table 'public.user'"
**Solution**: Run the SQL schema in Supabase SQL Editor (see DEPLOYMENT.md)

### Issue: "Connection to server failed"
**Solution**: Verify DATABASE_URL format and credentials

### Issue: "Supabase key invalid"
**Solution**: Check you're using the anon/public key, not the service_role key

## Example .env.template

Save this as `.env.template` (commit to git) and copy to `.env` (do NOT commit):

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-me-in-production

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Optional
GOOGLE_API_KEY=your-google-api-key
PORT=5000
```

## Quick Setup Commands

```bash
# 1. Copy template
cp .env.template .env

# 2. Edit with your values
nano .env  # or use your preferred editor

# 3. Verify configuration
python -c "from dotenv import load_dotenv; load_dotenv(); print('Config loaded')"

# 4. Run application
python run.py
```
