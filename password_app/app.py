"""
Password Security Web Application
A Flask app with user registration, login, password strength checking,
and password generation — all with proper security practices.
"""

import os
import re
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Try relative import (for Gunicorn/production), fall back to absolute (for local)
try:
    from .translations import get_translation, get_all_languages
except ImportError:
    from translations import get_translation, get_all_languages

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────
app = Flask(__name__)

# Use SECRET_KEY from environment or generate random one
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Rate Limiter - prevent brute force and DDoS attacks
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# SQLite database stored in the project folder
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'users.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session expires after 30 min

db = SQLAlchemy(app)

def get_lang():
    """Get current language from session or default to 'en'"""
    return session.get('lang', 'en')

def t(key, **kwargs):
    """Translation helper - get translated string"""
    return get_translation(get_lang(), key, **kwargs)

@app.context_processor
def inject_translations():
    """Make translations available in all templates"""
    return {
        't': t,
        'current_lang': get_lang(),
        'all_languages': get_all_languages()
    }

class User(db.Model):
    """Stores user accounts. Passwords are NEVER stored in plain text."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)  # SHA-256 produces 64 hex chars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    failed_attempts = db.Column(db.Integer, default=0)       # Count failed logins
    locked_until = db.Column(db.DateTime, nullable=True)     # Lockout timestamp
    is_admin = db.Column(db.Boolean, default=False)           # Admin flag
    password_purpose = db.Column(db.String(255), nullable=True)  # Purpose of password

    def __repr__(self):
        return f'<User {self.username}>'


class SavedPassword(db.Model):
    """Stores passwords generated and saved by users."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    password_text = db.Column(db.String(255), nullable=False)  # Store hashed password
    purpose = db.Column(db.String(255), nullable=True)  # What is this password for? (Gmail, Facebook, etc)
    account_username = db.Column(db.String(255), nullable=True)  # Username for this password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    strength_score = db.Column(db.Integer, nullable=True)  # Password strength 1-5
    
    user = db.relationship('User', backref='saved_passwords')

    def __repr__(self):
        return f'<SavedPassword {self.purpose}>'


def hash_password(password: str) -> str:
    """Hash a password using SHA-256. Returns a hex string."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def check_password_strength(password: str) -> dict:
    """
    Analyse a password and return its strength + feedback.
    Returns: { score: int, label: str, tips: [str] }
    """
    tips = []
    score = 0

    if len(password) >= 8:
        score += 1
    else:
        tips.append("Use at least 8 characters")

    if len(password) >= 12:
        score += 1  # Bonus for longer passwords

    if re.search(r'[A-Z]', password):
        score += 1
    else:
        tips.append("Add an uppercase letter (A–Z)")

    if re.search(r'[a-z]', password):
        score += 1
    else:
        tips.append("Add a lowercase letter (a–z)")

    if re.search(r'\d', password):
        score += 1
    else:
        tips.append("Add a number (0–9)")

    if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        score += 1
    else:
        tips.append("Add a special character (!@#$%...)")

    # Map score to label
    if score <= 2:
        label = "Weak"
    elif score <= 4:
        label = "Medium"
    else:
        label = "Strong"

    return {"score": score, "max_score": 6, "label": label, "tips": tips}


def meets_policy(password: str) -> tuple[bool, str]:
    """
    Enforce the password policy.
    Returns (True, "") if valid, or (False, reason) if not.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, "Password must contain at least one special character."
    return True, ""


def generate_strong_password(length: int = 16) -> str:
    """Generate a cryptographically secure random password."""
    alphabet = (
        string.ascii_uppercase +
        string.ascii_lowercase +
        string.digits +
        "!@#$%^&*()_+-="
    )
    # Guarantee at least one of each required character type
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()_+-="),
    ]
    # Fill the rest randomly
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    # Shuffle so the required chars aren't always at the start
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


def is_account_locked(user: User) -> bool:
    """Check whether a user's account is currently locked out."""
    if user.locked_until and datetime.utcnow() < user.locked_until:
        return True
    return False


def login_required(f):
    """Decorator: redirect to /login if the user isn't logged in."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: redirect if user isn't an admin."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route('/set-language/<lang>')
def set_language(lang):
    """Set user's language preference"""
    if lang in get_all_languages():
        session['lang'] = lang
    
    # Redirect to referrer or dashboard
    return redirect(request.referrer or url_for('index'))


@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Max 10 registrations per hour (prevent spam)
def register():
    """Handle new user registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # ── Input validation ──────────────────
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('register.html')

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return render_template('register.html')

        # ── Password policy ───────────────────
        valid, reason = meets_policy(password)
        if not valid:
            flash(reason, "error")
            return render_template('register.html')

        # ── Check for duplicate username ──────
        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "error")
            return render_template('register.html')

        # ── Save user with hashed password ────
        new_user = User(
            username=username,
            password_hash=hash_password(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute (brute force protection)
def login():
    """Handle user login with brute-force protection."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        # ── Unknown username ──────────────────
        if not user:
            flash("Invalid username or password.", "error")
            return render_template('login.html')

        # ── Account locked? ───────────────────
        if is_account_locked(user):
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60
            flash(f"Account locked. Try again in ~{remaining + 1} minute(s).", "error")
            return render_template('login.html')

        # ── Wrong password ────────────────────
        if user.password_hash != hash_password(password):
            user.failed_attempts += 1

            if user.failed_attempts >= 3:
                # Lock account for 15 minutes
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                db.session.commit()
                flash("Too many failed attempts. Account locked for 15 minutes.", "error")
            else:
                remaining = 3 - user.failed_attempts
                db.session.commit()
                flash(f"Invalid password. {remaining} attempt(s) remaining.", "error")

            return render_template('login.html')

        # ── Successful login ──────────────────
        user.failed_attempts = 0
        user.locked_until = None
        db.session.commit()

        session.permanent = True
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin

        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard — only visible when logged in."""
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/logout')
@login_required
def logout():
    """Clear the session and redirect to login."""
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for('login'))


@app.route('/check-password', methods=['POST'])
@limiter.limit("30 per minute")  # API rate limit - prevent abuse
def check_password():
    """
    API endpoint: accepts JSON { "password": "..." }
    Returns strength analysis as JSON.
    """
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({"error": "No password provided"}), 400

    result = check_password_strength(data['password'])
    return jsonify(result)


@app.route('/generate-password', methods=['POST'])
@login_required
@limiter.limit("20 per minute")  # API rate limit - prevent abuse
def generate_password():
    """
    API endpoint: returns a freshly generated strong password.
    Accepts JSON: { "length": 16, "purpose": "..." }
    Stores purpose in user profile.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        length = int(data.get('length', 16))
        length = max(12, min(length, 64))   # clamp between 12 and 64
    except (ValueError, TypeError):
        length = 16
    
    purpose = data.get('purpose', '').strip()
    if not purpose:
        purpose = 'General use'
    
    # Save purpose to current user
    user = User.query.get(session['user_id'])
    if user:
        user.password_purpose = purpose
        db.session.commit()
    
    password = generate_strong_password(length)
    return jsonify({"password": password, "purpose": purpose})


@app.route('/save-password', methods=['POST'])
@login_required
@limiter.limit("20 per minute")  # API rate limit
def save_password():
    """
    Save a generated password to the user's vault.
    Accepts JSON: { "password": "...", "purpose": "Gmail", "account_username": "user@gmail.com" }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    password = data.get('password', '').strip()
    purpose = data.get('purpose', 'General use').strip()
    account_username = data.get('account_username', '').strip()
    
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    # Check password strength
    strength = check_password_strength(password)
    strength_score = strength.get('score', 0)
    
    # Hash the password before saving (extra security)
    password_hash = hash_password(password)
    
    # Create and save to database
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    saved_pwd = SavedPassword(
        user_id=user.id,
        password_text=password_hash,
        purpose=purpose,
        account_username=account_username,
        strength_score=strength_score
    )
    
    db.session.add(saved_pwd)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"Password saved for {purpose}",
        "strength": strength
    }), 201


@app.route('/saved-passwords')
@admin_required
def saved_passwords():
    """
    Display all saved passwords (Admin only).
    """
    all_passwords = SavedPassword.query.order_by(SavedPassword.created_at.desc()).all()
    
    return render_template('saved_passwords.html', passwords=all_passwords, t=t)


# ─────────────────────────────────────────────
# Admin Routes
# ─────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_panel():
    """Display admin panel with all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin.html', users=users, now=datetime.utcnow())


@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)."""
    if user_id == session.get('user_id'):
        flash("You cannot delete your own account.", "error")
        return redirect(url_for('admin_panel'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('admin_panel'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{username}' has been deleted.", "success")
    return redirect(url_for('admin_panel'))


@app.route('/admin/toggle-lock/<int:user_id>', methods=['POST'])
@admin_required
def toggle_lock(user_id):
    """Lock or unlock a user account (admin only)."""
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('admin_panel'))
    
    if user.locked_until and datetime.utcnow() < user.locked_until:
        # Unlock
        user.locked_until = None
        db.session.commit()
        flash(f"User '{user.username}' has been unlocked.", "success")
    else:
        # Lock for 24 hours
        user.locked_until = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        flash(f"User '{user.username}' has been locked for 24 hours.", "success")
    
    return redirect(url_for('admin_panel'))


# ─────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────
with app.app_context():
    db.create_all()   # Create tables if they don't exist yet

if __name__ == '__main__':
    print("=" * 50)
    print("  Password Security App is running!")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)


