import re
import bcrypt
from email_validator import validate_email, EmailNotValidError
from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def verify_password(hashed_password, password):
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    except Exception:
        return False


def is_valid_username(username):
    """Check if the username is valid (alphanumeric and underscores only, 3-20 characters)."""
    if not username:
        return False
    # Allow only letters, numbers, and underscores, 3-20 characters
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


def normalize_username(username):
    """Convert username to lowercase for consistent storage and comparison."""
    return username.lower() if username else None


def is_valid_password(password):
    """
    Validate password meets all requirements:
    - Contains at least one lowercase letter
    - Contains at least one uppercase letter
    - Contains at least one number
    - Contains at least one special character
    - Is at least 7 characters long
    - Contains no spaces
    """
    patterns = {
        'lowercase': r'[a-z]',
        'uppercase': r'[A-Z]',
        'number': r'[0-9]',
        'special': r'[!@#$%^&*(),.?":{}|<>]',
        'length': r'.{7,}',
        'space': r'^\S*$'
    }
    
    checks = {
        'lowercase': False,
        'uppercase': False,
        'number': False,
        'special': False,
        'length': False,
        'space': False
    }
    
    for key, pattern in patterns.items():
        checks[key] = bool(re.search(pattern, password))
    
    return all(checks.values())
