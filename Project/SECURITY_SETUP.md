# Security Setup Guide

## Environment Configuration

This application uses environment variables for sensitive configuration. Follow these steps to set up your environment securely:

### 1. Copy the Environment Template

```bash
cp .env.example .env
```

### 2. Generate a Secure Secret Key

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

### 3. Update Your .env File

Edit `.env` with your actual configuration values. **Never commit this file to version control.**

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Security Features Implemented

- ✅ Environment variable configuration
- ✅ Secure secret key generation
- ✅ CSRF protection enabled
- ✅ Secure session cookies
- ✅ Password hashing with Werkzeug
- ✅ Proper gitignore configuration

## Production Deployment

For production deployment, ensure:

1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Use a strong, unique `SECRET_KEY`
4. Use a production database (PostgreSQL recommended)
5. Enable HTTPS for secure cookies
6. Never commit `.env` files

## Files to Never Commit

The following files contain sensitive information and should never be committed:

- `.env`
- Any database files (`*.db`, `*.sqlite`)
- Any files with passwords, API keys, or tokens

These are already included in `.gitignore` for your protection.
