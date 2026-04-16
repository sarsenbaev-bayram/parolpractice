# 🔐 Bayram — Password Security Web App

A beginner-friendly Flask app that demonstrates secure password handling:
hashed storage, strength checking, generation, and brute-force protection.

---

## 📁 Project Structure

```
password_app/
├── app.py               ← Main Flask application
├── requirements.txt     ← Python dependencies
├── users.db             ← SQLite database (auto-created on first run)
└── templates/
    ├── base.html        ← Shared layout + styles
    ├── register.html    ← Registration page
    ├── login.html       ← Login page
    └── dashboard.html   ← Protected dashboard
```

---

## 🚀 How to Run

### 1. Install Python (3.10+)
Download from https://python.org if needed.

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in your browser
```
http://127.0.0.1:5000
```

---

## 🔑 Features

| Feature | Details |
|---|---|
| Registration | Username + strong password, hashed with SHA-256 |
| Login | Session-based, with lockout after 3 failed attempts |
| Password strength | Real-time Weak / Medium / Strong meter |
| Password generator | Cryptographically secure, 12–40 chars |
| Brute-force protection | 15-minute lockout after 3 wrong passwords |
| Session management | Expires after 30 minutes of inactivity |

---

## 🛡 Security Notes

- **Passwords are NEVER stored in plain text** — SHA-256 hash only
- Input validation on all forms (length, policy enforcement)
- Password policy: 8+ chars, uppercase, lowercase, number, special char
- Sessions cleared on logout
- Login attempt counter resets on successful login

---

## 🌐 API Endpoints

| Route | Method | Description |
|---|---|---|
| `/register` | GET/POST | Create a new account |
| `/login` | GET/POST | Log in |
| `/dashboard` | GET | Protected user dashboard |
| `/logout` | GET | End session |
| `/check-password` | POST (JSON) | Returns strength analysis |
| `/generate-password` | GET | Returns a strong random password |

### Example: Check password strength
```bash
curl -X POST http://127.0.0.1:5000/check-password \
  -H "Content-Type: application/json" \
  -d '{"password": "Hello@123"}'
```

### Example: Generate password
```bash
curl http://127.0.0.1:5000/generate-password?length=20
```

---

## 📦 Deployment

### Deploy to GitHub

1. **Initialize Git** (if not already done):
```bash
cd password_app
git init
git add .
git commit -m "Initial commit - Password Security App"
```

2. **Push to GitHub**:
```bash
git remote add origin https://github.com/sarsenbaev-bayram/parolpractice.git
git branch -M main
git push -u origin main
```

### Deploy to Digital Ocean

#### Option 1: Using App Platform (Easiest)

1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Select **GitHub** as source
4. Connect your account and select the `parolpractice` repository
5. Select **"main"** branch
6. Configure App:
   - **Framework**: Python
   - **Build command**: `pip install -r password_app/requirements.txt`
   - **Run command**: `gunicorn -w 4 -b 0.0.0.0:$PORT password_app.app:app`
   - **Environment variables**:
     - `FLASK_ENV=production`
     - `FLASK_DEBUG=False`
7. Click **"Deploy"**

The app will be live in ~5 minutes!

#### Option 2: Using `app.yaml` (Recommended)

We've included an `app.yaml` file that automates the configuration:

1. Push to GitHub (see above)
2. In Digital Ocean, upload the `app.yaml` file
3. App Platform will auto-configure everything
4. Click **Deploy** and you're done!

#### Option 3: Manual Deployment (Droplet)

1. **Create a Droplet** (Ubuntu 22.04 recommended)

2. **SSH into your droplet**:
```bash
ssh root@your-droplet-ip
```

3. **Install dependencies**:
```bash
apt update && apt upgrade -y
apt install python3.11 python3.11-venv python3.11-dev git nginx supervisor -y
```

4. **Clone your repository**:
```bash
cd /var/www
git clone https://github.com/sarsenbaev-bayram/parolpractice.git
cd parolpractice
```

5. **Set up virtual environment**:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r password_app/requirements.txt
```

6. **Create `.env` file**:
```bash
echo "FLASK_ENV=production" > password_app/.env
echo "FLASK_DEBUG=False" >> password_app/.env
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" >> password_app/.env
```

7. **Test the app**:
```bash
cd password_app
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

8. **Configure Supervisor** (for auto-restart):
```bash
sudo nano /etc/supervisor/conf.d/parol.conf
```

Add:
```
[program:parol]
directory=/var/www/parolpractice/password_app
command=/var/www/parolpractice/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/parol.err.log
stdout_logfile=/var/log/parol.out.log
```

9. **Configure Nginx**:
```bash
sudo nano /etc/nginx/sites-available/parol
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/parol /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread && supervisorctl update && supervisorctl start parol
```

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and set your values:

```bash
cp .env.example .env
```

Required variables:
- `FLASK_ENV`: Set to `production` on servers
- `FLASK_DEBUG`: Always `False` in production
- `SECRET_KEY`: Generate with `python3 -c 'import secrets; print(secrets.token_hex(32))'`
- `DATABASE_URL`: (optional) Custom database path

---

## 📝 Admin Panel

Access at `/admin` after logging in as admin.

**Default admin credentials:**
- Username: `admin`
- Password: Use the `change_password.py` script to set your own

**Admin features:**
- View all registered users
- Delete user accounts
- Lock/unlock accounts (24-hour lockout)

---
