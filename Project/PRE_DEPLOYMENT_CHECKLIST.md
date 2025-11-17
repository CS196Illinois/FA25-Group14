# 🎯 Pre-Deployment Checklist

Use this checklist before deploying to Render to ensure everything is configured correctly.

## ☑️ Code & Configuration

- [ ] All code changes committed to git
- [ ] `requirements.txt` includes all dependencies
- [ ] `gunicorn_config.py` exists and is configured
- [ ] `render.yaml` exists (for Infrastructure as Code)
- [ ] `Procfile` exists
- [ ] `runtime.txt` specifies Python 3.11.0
- [ ] `.gitignore` excludes `.env`, `instance/`, `__pycache__/`
- [ ] Health check endpoint `/health` implemented
- [ ] Database connection pooling configured

## ☑️ Local Testing

- [ ] Application runs locally without errors
  ```bash
  python run.py
  ```
- [ ] Can access homepage at http://localhost:5000
- [ ] Login/registration works
- [ ] Course search works
- [ ] Reviews can be submitted
- [ ] Messages can be sent
- [ ] Health check responds: http://localhost:5000/health

## ☑️ Database Setup (Supabase)

- [ ] Supabase account created
- [ ] Project created in Supabase
- [ ] Database tables created (run SQL from DEPLOYMENT.md)
- [ ] Tables verified in Supabase dashboard:
  - [ ] `user` table exists
  - [ ] `user_requirements` table exists
  - [ ] `review` table exists
  - [ ] `message` table exists
- [ ] Indexes created for performance
- [ ] Connection string obtained from Settings → Database
- [ ] API credentials obtained from Settings → API

## ☑️ Environment Variables Ready

Local (.env file):
- [ ] `FLASK_ENV=development`
- [ ] `FLASK_DEBUG=True`
- [ ] `SECRET_KEY` set (any value for dev)
- [ ] `SUPABASE_URL` set
- [ ] `SUPABASE_KEY` set
- [ ] `DATABASE_URL` set

Production (for Render dashboard):
- [ ] `FLASK_ENV=production`
- [ ] `FLASK_DEBUG=False`
- [ ] Strong `SECRET_KEY` generated (64+ characters)
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] `SUPABASE_URL` ready to paste
- [ ] `SUPABASE_KEY` ready to paste
- [ ] `DATABASE_URL` ready to paste
- [ ] Optional: `GOOGLE_API_KEY` for AI features

## ☑️ Git Repository

- [ ] Code pushed to GitHub
- [ ] Repository is accessible
- [ ] Branch is `master` (or update render.yaml)
- [ ] `.env` file is NOT committed (check git history)
- [ ] All deployment files committed:
  - [ ] `gunicorn_config.py`
  - [ ] `render.yaml`
  - [ ] `Procfile`
  - [ ] `runtime.txt`
  - [ ] `DEPLOYMENT.md`
  - [ ] `README.md`

## ☑️ Render Account

- [ ] Render account created at render.com
- [ ] GitHub account connected to Render
- [ ] Repository authorized in Render

## ☑️ Security Checks

- [ ] `FLASK_DEBUG=False` for production
- [ ] Strong `SECRET_KEY` (not the dev key!)
- [ ] `.env` in `.gitignore`
- [ ] No hardcoded credentials in code
- [ ] Database passwords not in commit history
- [ ] HTTPS will be enforced (automatic on Render)
- [ ] Secure cookies enabled for production

## ☑️ Data Migration (If Applicable)

If migrating from SQLite:
- [ ] Local SQLite database exists at `instance/course_compass.db`
- [ ] Migration script ready: `migrate_sqlite_to_supabase.py`
- [ ] Supabase tables created (empty)
- [ ] Migration tested locally
- [ ] Data verified in Supabase dashboard after migration

## ☑️ Documentation Review

- [ ] Read `DEPLOYMENT.md` - know the deployment steps
- [ ] Read `ENV_SETUP.md` - know how to configure variables
- [ ] Read `README.md` - understand project structure
- [ ] Read `RENDER_SETUP_COMPLETE.md` - understand what was set up

## ☑️ Deployment Readiness

Run the build verification script:

**Windows:**
```powershell
.\build.ps1
```

**Mac/Linux:**
```bash
chmod +x build.sh
./build.sh
```

Expected output:
- [ ] ✓ Python version displayed
- [ ] ✓ Flask installed
- [ ] ✓ Supabase installed
- [ ] ✓ Gunicorn installed
- [ ] ✓ psycopg2 installed
- [ ] ✓ All required files present

## ☑️ Final Steps Before Deploy

1. **Commit everything:**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin master
   ```

2. **Verify commit:**
   ```bash
   git log --oneline -1
   git status
   ```

3. **Double-check credentials:**
   - [ ] Supabase URL starts with `https://`
   - [ ] Supabase key is the anon/public key (not service_role)
   - [ ] DATABASE_URL format: `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres`

4. **Have these ready to paste in Render:**
   - [ ] Copy `SUPABASE_URL` to clipboard
   - [ ] Copy `SUPABASE_KEY` to clipboard
   - [ ] Copy `DATABASE_URL` to clipboard
   - [ ] Copy generated `SECRET_KEY` to clipboard

## 🚀 Ready to Deploy?

If all checkboxes are checked, you're ready to deploy!

### Deploy Now:

1. **Go to Render**: https://dashboard.render.com
2. **Click**: "New +" → "Web Service"
3. **Connect**: Your GitHub repository
4. **Configure**: Render will detect `render.yaml`
5. **Add Environment Variables**: From your checklist above
6. **Deploy**: Click "Create Web Service"

### After Deployment:

- [ ] Build completes successfully
- [ ] Service shows "Live" status
- [ ] Visit your app URL
- [ ] Test `/health` endpoint
- [ ] Register a test account
- [ ] Submit a test review
- [ ] Send a test message
- [ ] Check logs for any errors

## 🎉 Success!

Once deployed, your app will be live at:
```
https://your-app-name.onrender.com
```

## 📞 If Something Goes Wrong

1. **Check Render logs** for error messages
2. **Review** this checklist - did you miss anything?
3. **Verify** environment variables in Render dashboard
4. **Test locally** to isolate the issue
5. **Refer to** `DEPLOYMENT.md` troubleshooting section

---

**Note**: Keep this checklist handy for future deployments!
