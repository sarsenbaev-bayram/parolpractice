# GitHub Setup Guide

## Quick Start

### 1. Initialize Git (first time only)

```bash
cd password_app
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2. Add all files

```bash
git add .
git status  # Check what will be committed
```

### 3. First Commit

```bash
git commit -m "Initial commit - Password Security Web App

- User registration and login
- Password strength checker
- Secure password storage (SHA-256)
- Admin panel for user management
- Multi-language support
- Brute-force protection"
```

### 4. Add Remote Repository

```bash
git remote add origin https://github.com/sarsenbaev-bayram/parolpractice.git
git branch -M main
git push -u origin main
```

---

## Subsequent Updates

```bash
# Make changes to files...

# Stage changes
git add .

# Commit with meaningful message
git commit -m "Added feature: X"

# Push to GitHub
git push origin main
```

---

## GitHub Repository Settings

### 1. Enable GitHub Actions (CI/CD)
- Go to Settings → Actions → Set to "Allow"
- CI/CD tests run automatically on push/PR

### 2. Set Up Secrets (for production)
- Settings → Secrets and variables → Actions
- Add: `DIGITAL_OCEAN_TOKEN` (if using automation)
- Add: `SECRET_KEY` (generated value)

### 3. Enable Discussions
- Settings → Features → Enable "Discussions"
- Good for community support

### 4. Branch Protection (optional)
- Settings → Branches → Add rule
- Require PR reviews before merge
- Require status checks to pass

---

## Deployment from GitHub

### Option A: Digital Ocean App Platform (Easiest)
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Select "GitHub" as source
4. Authenticate and select `parolpractice` repo
5. Set branch to `main`
6. Configure build/run commands (see DEPLOYMENT.md)
7. Click Deploy

### Option B: Using Webhooks
1. Set up a Digital Ocean droplet with your app
2. Add webhook in GitHub: Settings → Webhooks
3. Payload URL: `https://your-server.com/webhook`
4. On push, webhook triggers deployment script

---

## Useful GitHub Commands

```bash
# View commit history
git log --oneline -10

# See what changed
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Stash changes (save for later)
git stash
git stash pop

# Create new branch for features
git checkout -b feature/awesome-feature
git push origin feature/awesome-feature
# Then create Pull Request on GitHub

# Sync with latest version
git pull origin main
```

---

## GitHub Best Practices

✅ **DO:**
- Write clear commit messages
- One feature per commit when possible
- Use branches for features/fixes
- Pull before pushing if multiple people work on project

❌ **DON'T:**
- Commit `.env` files with secrets
- Commit database files (`*.db`)
- Commit `__pycache__` or `.venv`
- Force push to `main` branch

---

## .gitignore Recap

We've included `.gitignore` which excludes:
- Virtual environments (`venv/`, `env/`, `.venv`)
- Python cache (`__pycache__/`, `*.pyc`)
- Databases (`*.db`, `*.sqlite`)
- Environment files (`.env`)
- IDE files (`.vscode/`, `.idea/`)

---

## Troubleshooting

### "fatal: Not a git repository"
```bash
git init
git remote add origin https://github.com/sarsenbaev-bayram/parolpractice.git
```

### "Permission denied (publickey)"
Set up SSH key: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### "Rejected (non-fast-forward)"
```bash
git pull origin main
# Fix conflicts, then:
git add .
git commit -m "Merge changes"
git push origin main
```

---

## Next Steps

1. ✅ Push to GitHub: `git push origin main`
2. ✅ Enable GitHub Actions in Settings
3. ✅ Deploy to Digital Ocean: https://cloud.digitalocean.com/apps
4. ✅ Set up custom domain (optional)
5. ✅ Configure SSL certificate

See `DEPLOYMENT.md` for detailed deployment instructions!
