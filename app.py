from flask import Flask, render_template, request, redirect, url_for, session, flash
from mongodb import connect_mongodb
from user_auth import (
    is_valid_email, 
    hash_password, 
    verify_password, 
    is_valid_username, 
    normalize_username,
    is_valid_password,
    login_required
)
from google_auth import google_login, google_callback, is_google_authenticated
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Use secret key from .env file

# Connect to MongoDB once at application startup
mongodb_collection = connect_mongodb()

@app.route('/')
@login_required
def home():
    user = mongodb_collection.find_one({'_id': session.get('user_id')})
    is_google_user = session.get('is_google_user', False)
    return render_template('home.html', user=user, is_google_user=is_google_user)

@app.route('/login/google')
def google_login_route():
    return google_login()

@app.route('/callback/google')
def google_callback_route():
    return google_callback(mongodb_collection)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    form_data = {}
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        form_data['username'] = username

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html', form_data=form_data)

        user = mongodb_collection.find_one({"username": normalize_username(username)})
        if user:
            # First try: Check with hashed password
            if verify_password(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session['is_google_user'] = False
                # Update ONLY last login time
                mongodb_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                return redirect(url_for('home'))
            
            # Second try: Check with non-hashed password
            elif 'password_nohash' in user and user['password_nohash'] == password:
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session['is_google_user'] = False
                # Update ONLY last login time
                mongodb_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
                return render_template('login.html', form_data=form_data)
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html', form_data=form_data)

    return render_template('login.html', form_data=form_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        form_data = {
            'fullname': request.form['fullname'],
            'username': request.form['username'],
            'email': request.form['email']
        }
        
        fullname = form_data['fullname']
        username = form_data['username']
        email = form_data['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        # Validation
        if not all([fullname, username, email, password, confirm_password]):
            flash('All fields are required!', 'error')
            return render_template('register.html', form_data=form_data)
            
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html', form_data=form_data)
            
        if not is_valid_password(password):
            flash('Password does not meet the requirements!', 'error')
            return render_template('register.html', form_data=form_data)
            
        normalized_username = normalize_username(username)
        if not is_valid_username(normalized_username):
            flash('Username must be 3-20 characters long and can only contain letters, numbers, and underscores!', 'error')
            return render_template('register.html', form_data=form_data)
            
        if not is_valid_email(email):
            flash('Invalid email format!', 'error')
            return render_template('register.html', form_data=form_data)
            
        # Check if username or email already exists
        if mongodb_collection.find_one({'$or': [
            {'username': normalized_username},
            {'emailid': email}
        ]}):
            flash('Username or email already exists!', 'error')
            return render_template('register.html', form_data=form_data)
            
        # Create new user with both hashed and non-hashed passwords
        current_time = datetime.utcnow()
        user = {
            'name': fullname,
            'username': normalized_username,
            'emailid': email,
            'password': hash_password(password),
            'password_nohash': password,  # Store non-hashed password
            'google_login': False,
            'created_at': current_time,  # Set creation time
            'last_login': current_time   # Initial login time is same as creation time
        }
        
        result = mongodb_collection.insert_one(user)
        
        # Log user in
        session['user_id'] = str(result.inserted_id)
        session['username'] = normalized_username
        session['is_google_user'] = False
        
        return redirect(url_for('home'))
        
    return render_template('register.html', form_data={})

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/guru')
def guru():
    return "The application was built by Paramaguru."

if __name__ == '__main__':
    # Use environment variable for port with fallback to 5000
    port = int(os.environ.get('PORT', 5000))
    # In production, bind to 0.0.0.0 to accept connections from any source
    app.run(host='0.0.0.0', port=port, debug=False) 
    app.run(debug=True) 
