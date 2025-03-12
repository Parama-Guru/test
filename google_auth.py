from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
from flask import session, redirect, url_for, flash, request
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OAuth 2.0 client configuration
# Use environment variables instead of direct file path
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
AUTH_URI = os.getenv('GOOGLE_AUTH_URI')
TOKEN_URI = os.getenv('GOOGLE_TOKEN_URI')
AUTH_PROVIDER_X509_CERT_URL = os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
JAVASCRIPT_ORIGINS = os.getenv('GOOGLE_JAVASCRIPT_ORIGINS')

# Create client config dictionary from environment variables
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "project_id": PROJECT_ID,
        "auth_uri": AUTH_URI,
        "token_uri": TOKEN_URI,
        "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [REDIRECT_URI],
        "javascript_origins": [JAVASCRIPT_ORIGINS]
    }
}
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

# Create OAuth2 flow
flow = Flow.from_client_config(
    client_config=CLIENT_CONFIG,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

def is_google_authenticated():
    return 'google_id' in session

def google_login():
    try:
        # Add prompt=select_account to force Google to show the account selection screen
        authorization_url, state = flow.authorization_url(
            prompt='select_account'
        )
        session['state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"Error in google_login: {e}")
        flash('Failed to initiate Google login. Please try again.', 'error')
        return redirect(url_for('login'))

def google_callback(mongodb_collection):
    try:
        flow.fetch_token(authorization_response=request.url)

        if not session.get('state') == request.args.get('state'):
            flash('Authentication failed: State mismatch', 'error')
            return redirect(url_for('login'))

        credentials = flow.credentials
        token_request = requests.Request()
        
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=os.getenv('GOOGLE_CLIENT_ID')
        )

        # Extract only required information
        google_id = id_info.get('sub')
        email = id_info.get('email')
        fullname = id_info.get('name')
        username = email.split('@')[0]  # Get username from email

        # Check if user exists
        existing_user = mongodb_collection.find_one({'google_id': google_id})
        
        if existing_user:
            # Update login time for existing user
            mongodb_collection.update_one(
                {'google_id': google_id},
                {
                    '$set': {
                        'last_login': datetime.utcnow()
                    }
                }
            )
            user_id = existing_user['_id']
            username = existing_user['username']
        else:
            # Check if username already exists
            while mongodb_collection.find_one({'username': username}):
                username = f"{username}{str(datetime.utcnow().microsecond)[:3]}"
            
            # Create new user with specified fields
            new_user = {
                'fullname': fullname,
                'emailid': email,
                'username': username,
                'google_login': True,
                'google_id': google_id,
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            result = mongodb_collection.insert_one(new_user)
            user_id = result.inserted_id

        # Set session data
        session['user_id'] = str(user_id)
        session['username'] = username
        session['google_id'] = google_id
        session['is_google_user'] = True
        session['fullname'] = fullname
        session['email'] = email

        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('home'))

    except Exception as e:
        print(f"Error during Google authentication: {e}")
        flash('Failed to log in with Google. Please try again.', 'error')
        return redirect(url_for('login'))

def google_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_google_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function 