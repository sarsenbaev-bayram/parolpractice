# Deployment Checklist

Use this checklist to ensure your app is ready for production deployment.

---

## 📋 Pre-Deployment

- [ ] Code is tested and working locally
- [ ] No sensitive data in code (hardcoded passwords, API keys)
- [ ] `.env.example` file created with template variables
- [ ] `.gitignore` prevents secrets from being committed
- [ ] `requirements.txt` updated with all dependencies
- [ ] `runtime.txt` specifies Python version (3.11.8)
- [ ] `Procfile` configured for production (Gunicorn)
- [ ] Security settings enabled in `app.py`:
  - [ ] `FLASK_ENV=production`
  - [ ] `FLASK_DEBUG=False`
  - [ ] `SECRET_KEY` from environment variables

---

## 🔐 Security Checklist

- [ ] Replace default `SECRET_KEY` with strong random value
- [ ] Database file (`.db`) is in `.gitignore`
- [ ] No plaintext passwords in code
- [ ] Password hashing properly implemented (SHA-256 or better)
- [ ] Input validation on all forms
- [ ] CSRF protection enabled
- [ ] Session timeout configured (30 min default)
- [ ] Brute-force protection active (account lockout)
- [ ] Admin panel requires authentication
- [ ] Error messages don't expose system details

---

## 📦 Deployment Files Ready

- [ ] `.gitignore` - prevents committing secrets
- [ ] `.env.example` - template for environment variables
- [ ] `Procfile` - tells platform how to run app
- [ ] `requirements.txt` - includes production dependencies (gunicorn)
- [ ] `runtime.txt` - specifies Python version
- [ ] `app.yaml` - Digital Ocean configuration (optional)
- [ ] `Dockerfile` - Docker image for containerized deployment (optional)
- [ ] `docker-compose.yml` - Local Docker testing (optional)

---

## 🚀 GitHub Deployment Steps

- [ ] Repository created: `https://github.com/sarsenbaev-bayram/parolpractice`
- [ ] Files added: `git add .`
- [ ] Initial commit: `git commit -m "Initial commit"`
- [ ] Remote configured: `git remote add origin ...`
- [ ] Pushed to main: `git push -u origin main`
- [ ] GitHub Actions workflow created (`.github/workflows/tests.yml`)
- [ ] Repository is public or access configured for deployment

---

## 🌐 Digital Ocean Deployment Steps

### Using App Platform (Recommended)

- [ ] Go to https://cloud.digitalocean.com/apps
- [ ] Create new app
- [ ] Select GitHub as source
- [ ] Authenticate with GitHub
- [ ] Select `sarsenbaev-bayram/parolpractice` repository
- [ ] Select `main` branch
- [ ] Configure App settings:
  - [ ] Build command: `pip install -r password_app/requirements.txt`
  - [ ] Run command: `gunicorn -w 4 -b 0.0.0.0:$PORT password_app.app:app`
  - [ ] HTTP port: 5000
  - [ ] Environment variables set:
    - [ ] `FLASK_ENV=production`
    - [ ] `FLASK_DEBUG=False`
    - [ ] `SECRET_KEY=<generated-value>`
- [ ] Deploy app
- [ ] Test at `.ondigitalocean.app` domain

### Using Droplet (Manual)

- [ ] Create Ubuntu 22.04 Droplet
- [ ] SSH into droplet
- [ ] Install system dependencies
- [ ] Clone GitHub repository
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Configure `.env` file
- [ ] Set up Supervisor for process management
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Test application at domain

---

## 🧪 Testing Before Deployment

- [ ] App runs locally without errors: `python app.py`
- [ ] Registration works
- [ ] Login works with correct password
- [ ] Failed login shows error (test lockout)
- [ ] Password strength checker works
- [ ] Password generator works
- [ ] Admin panel accessible with admin account
- [ ] All templates render correctly
- [ ] Responsive design works on mobile
- [ ] Session timeout works
- [ ] Logout clears session

---

## 📊 Post-Deployment

- [ ] App accessible at public URL
- [ ] Admin account working with new credentials
- [ ] Test user can register new account
- [ ] Database tables created successfully
- [ ] Error handling working (no 500 errors)
- [ ] Logging configured
- [ ] Monitoring configured (uptime, errors)
- [ ] Backups scheduled for database
- [ ] SSL certificate installed (HTTPS)
- [ ] Custom domain configured (optional)

---

## 🔄 Ongoing Maintenance

- [ ] Set up GitHub Actions for CI/CD
- [ ] Enable auto-deploy on push to main
- [ ] Schedule regular database backups
- [ ] Monitor application logs
- [ ] Plan for Droplet upgrades if needed
- [ ] Keep dependencies updated
- [ ] Review security logs monthly
- [ ] Test backup restoration process

---

## 📝 Quick Reference

| Task | Command | Location |
|------|---------|----------|
| Test locally | `python app.py` | `password_app/` |
| Install deps | `pip install -r requirements.txt` | `password_app/` |
| Change admin password | `python change_password.py admin NewPass` | `password_app/` |
| Check requirements | See `requirements.txt` | `password_app/` |
| See deployment steps | See `DEPLOYMENT.md` | Root |
| GitHub setup | See `GITHUB.md` | Root |

---

## ✅ Sign Off

- [ ] All items checked
- [ ] Ready for GitHub push
- [ ] Ready for Digital Ocean deployment
- [ ] Team notified of deployment

**Deployment Date**: ________________

**Deployed By**: ________________

---

For detailed instructions, see:
- `DEPLOYMENT.md` - Complete deployment guide
- `GITHUB.md` - GitHub setup and usage
- `README.md` - Project overview
