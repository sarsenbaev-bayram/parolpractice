# Digital Ocean Deployment Guide

This guide walks you through deploying **parolpractice** to Digital Ocean.

## Quick Start (Recommended)

### Using App Platform (5 minutes)

1. **Push to GitHub first**:
```bash
cd password_app
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/sarsenbaev-bayram/parolpractice.git
git branch -M main
git push -u origin main
```

2. **Create App in Digital Ocean**:
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App" → Select "GitHub"
   - Authenticate and select `parolpractice`
   - Choose `main` branch

3. **Configure**:
   - Build command: `pip install -r password_app/requirements.txt`
   - Run command: `gunicorn -w 4 -b 0.0.0.0:$PORT password_app.app:app`
   - HTTP port: 5000
   - Add environment variables:
     - `FLASK_ENV=production`
     - `FLASK_DEBUG=False`

4. **Deploy** - Click deploy button, wait 5 minutes

✅ Your app will be live at a `.ondigitalocean.app` domain!

---

## Option 2: Using `app.yaml`

We've included `app.yaml` which contains all configuration:

1. Push to GitHub (see above)
2. In Digital Ocean console, upload `app.yaml`
3. It auto-configures everything
4. Click Deploy

---

## Option 3: Manual Droplet Setup

For more control, use a traditional Ubuntu Droplet:

### Step 1: Create Droplet

- **Image**: Ubuntu 22.04 x64
- **Size**: $4/month (512MB → $6 recommended)
- **Region**: Closest to your users
- **Authentication**: SSH Key (recommended)

### Step 2: Server Setup

```bash
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3.11 python3.11-venv python3.11-dev git nginx supervisor curl -y
```

### Step 3: Clone & Setup App

```bash
cd /var/www
git clone https://github.com/sarsenbaev-bayram/parolpractice.git
cd parolpractice

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r password_app/requirements.txt
```

### Step 4: Environment Configuration

```bash
cd password_app

# Create .env file
cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:////var/www/parolpractice/password_app/users.db
EOF

# Test the app
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

Press `Ctrl+C` to stop. If it runs without errors, continue.

### Step 5: Supervisor Configuration

Supervisor keeps your app running and auto-restarts on crashes:

```bash
sudo nano /etc/supervisor/conf.d/parolpractice.conf
```

Paste:
```ini
[program:parolpractice]
directory=/var/www/parolpractice/password_app
command=/var/www/parolpractice/venv/bin/gunicorn \
  -w 4 \
  -b 127.0.0.1:8000 \
  --access-logfile /var/log/parol_access.log \
  --error-logfile /var/log/parol_error.log \
  app:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
```

Save (Ctrl+X → Y → Enter)

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start parolpractice
sudo supervisorctl status parolpractice
```

### Step 6: Nginx Reverse Proxy

Nginx handles incoming traffic and forwards to Gunicorn:

```bash
sudo nano /etc/nginx/sites-available/parolpractice
```

Paste:
```nginx
upstream parolpractice {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 10M;

    location / {
        proxy_pass http://parolpractice;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static {
        alias /var/www/parolpractice/password_app/static;
        expires 30d;
    }
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/parolpractice /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: SSL Certificate (Optional but Recommended)

Using Let's Encrypt (free):

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Monitoring & Logs

### View app logs:
```bash
sudo supervisorctl tail parolpractice
```

### Check status:
```bash
sudo supervisorctl status
```

### Restart app:
```bash
sudo supervisorctl restart parolpractice
```

### Nginx logs:
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### App won't start?
```bash
# Test manually
cd /var/www/parolpractice/password_app
source ../venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

### Permission errors?
```bash
sudo chown -R www-data:www-data /var/www/parolpractice
```

### Port already in use?
```bash
lsof -i :8000
kill -9 <PID>
```

---

## Maintenance

### Update code:
```bash
cd /var/www/parolpractice
git pull origin main
source venv/bin/activate
pip install -r password_app/requirements.txt
sudo supervisorctl restart parolpractice
```

### Database backup:
```bash
cp password_app/users.db password_app/users.db.backup
```

---

## Security Checklist

- [ ] Change admin password on first login
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use HTTPS (SSL certificate)
- [ ] Keep system updated: `apt update && apt upgrade`
- [ ] Use SSH keys (no password login)
- [ ] Configure firewall: `ufw enable`
- [ ] Backup database regularly

---

## Support

For issues, check:
- `/var/log/parol_error.log`
- Supervisor status: `sudo supervisorctl status`
- Nginx error log: `sudo tail -f /var/log/nginx/error.log`
