from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
import os
import secrets
import string
from dotenv import load_dotenv

load_dotenv()

def ensure_timezone_aware(dt):
    """Ensure datetime object is timezone-aware (UTC)"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# MongoDB setup
client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client.waitbin
users_collection = db.users
waitbins_collection = db.waitbins

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.context_processor
def inject_datetime():
    return {'datetime': datetime, 'timezone': timezone}

@app.template_filter('ensure_tz')
def ensure_timezone_filter(dt):
    """Template filter to ensure datetime is timezone-aware"""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.full_name = user_data['full_name']
        self.password_hash = user_data['password_hash']

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

def generate_edit_code():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        content = request.form.get('content')
        unlock_date = request.form.get('unlock_date')
        unlock_time = request.form.get('unlock_time', '00:00')
        
        if not content or not unlock_date:
            flash('Content and unlock date are required!', 'error')
            return render_template('create.html')
        
        # Combine date and time
        unlock_datetime_str = f"{unlock_date} {unlock_time}"
        try:
            unlock_datetime = datetime.strptime(unlock_datetime_str, '%Y-%m-%d %H:%M')
            unlock_datetime = unlock_datetime.replace(tzinfo=timezone.utc)
        except ValueError:
            flash('Invalid date or time format!', 'error')
            return render_template('create.html')
        
        edit_code = generate_edit_code()
        
        waitbin_data = {
            'title': title,
            'content': content,
            'unlock_datetime': unlock_datetime,
            'created_at': datetime.now(timezone.utc),
            'edit_code': edit_code,
            'user_id': ObjectId(current_user.id) if current_user.is_authenticated else None
        }
        
        result = waitbins_collection.insert_one(waitbin_data)
        waitbin_id = str(result.inserted_id)
        
        return render_template('created.html', 
                             waitbin_id=waitbin_id, 
                             edit_code=edit_code,
                             show_edit_code=not current_user.is_authenticated)
    
    return render_template('create.html')

@app.route('/w/<waitbin_id>')
def view_waitbin(waitbin_id):
    try:
        waitbin = waitbins_collection.find_one({'_id': ObjectId(waitbin_id)})
    except:
        abort(404)
    
    if not waitbin:
        abort(404)
    
    now = datetime.now(timezone.utc)
    unlock_datetime = waitbin['unlock_datetime']
    
    # Ensure unlock_datetime is timezone-aware
    if unlock_datetime.tzinfo is None:
        unlock_datetime = unlock_datetime.replace(tzinfo=timezone.utc)
    
    is_unlocked = now >= unlock_datetime
    
    return render_template('view.html', 
                         waitbin=waitbin, 
                         is_unlocked=is_unlocked,
                         time_remaining=unlock_datetime - now if not is_unlocked else None)

@app.route('/edit/<waitbin_id>')
def edit_form(waitbin_id):
    return render_template('edit_form.html', waitbin_id=waitbin_id)

@app.route('/edit/<waitbin_id>', methods=['POST'])
def edit_waitbin(waitbin_id):
    edit_code = request.form.get('edit_code')
    
    try:
        waitbin = waitbins_collection.find_one({'_id': ObjectId(waitbin_id)})
    except:
        abort(404)
    
    if not waitbin:
        abort(404)
    
    # Check if user has permission to edit
    can_edit = False
    
    # First check if the user owns this waitbin (logged in and created it)
    if current_user.is_authenticated and waitbin.get('user_id') == ObjectId(current_user.id):
        can_edit = True
    # If not owned by user, check edit code (works for both logged in and anonymous users)
    elif edit_code and waitbin.get('edit_code') == edit_code:
        can_edit = True
    # If no edit code provided, show the edit form (don't fail immediately)
    elif not edit_code:
        return render_template('edit_form.html', waitbin_id=waitbin_id)
    
    if not can_edit:
        flash('Invalid edit code!', 'error')
        return render_template('edit_form.html', waitbin_id=waitbin_id)
    
    if request.form.get('action') == 'edit':
        return render_template('edit.html', waitbin=waitbin)
    
    # Update waitbin
    title = request.form.get('title', waitbin['title'])
    content = request.form.get('content', waitbin['content'])
    unlock_date = request.form.get('unlock_date')
    unlock_time = request.form.get('unlock_time', '00:00')
    
    if unlock_date:
        unlock_datetime_str = f"{unlock_date} {unlock_time}"
        try:
            unlock_datetime = datetime.strptime(unlock_datetime_str, '%Y-%m-%d %H:%M')
            unlock_datetime = unlock_datetime.replace(tzinfo=timezone.utc)
        except ValueError:
            flash('Invalid date or time format!', 'error')
            return render_template('edit.html', waitbin=waitbin)
        
        waitbins_collection.update_one(
            {'_id': ObjectId(waitbin_id)},
            {'$set': {
                'title': title,
                'content': content,
                'unlock_datetime': unlock_datetime
            }}
        )
        
        flash('WaitBin updated successfully!', 'success')
    
    return redirect(url_for('view_waitbin', waitbin_id=waitbin_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        
        if not all([username, email, full_name, password]):
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
            flash('Username or email already exists!', 'error')
            return render_template('register.html')
        
        password_hash = generate_password_hash(password)
        
        user_data = {
            'username': username,
            'email': email,
            'full_name': full_name,
            'password_hash': password_hash,
            'created_at': datetime.now(timezone.utc)
        }
        
        users_collection.insert_one(user_data)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        
        user_data = users_collection.find_one({
            '$or': [
                {'username': username_or_email},
                {'email': username_or_email}
            ]
        })
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_waitbins = waitbins_collection.find({'user_id': ObjectId(current_user.id)}).sort('created_at', -1)
    return render_template('dashboard.html', waitbins=list(user_waitbins), datetime=datetime, timezone=timezone)

@app.route('/api/time-remaining/<waitbin_id>')
def api_time_remaining(waitbin_id):
    try:
        waitbin = waitbins_collection.find_one({'_id': ObjectId(waitbin_id)})
    except:
        return jsonify({'error': 'Not found'}), 404
    
    if not waitbin:
        return jsonify({'error': 'Not found'}), 404
    
    now = datetime.now(timezone.utc)
    unlock_datetime = waitbin['unlock_datetime']
    
    # Ensure unlock_datetime is timezone-aware
    if unlock_datetime.tzinfo is None:
        unlock_datetime = unlock_datetime.replace(tzinfo=timezone.utc)
    
    if now >= unlock_datetime:
        return jsonify({'unlocked': True})
    
    time_remaining = unlock_datetime - now
    return jsonify({
        'unlocked': False,
        'seconds_remaining': int(time_remaining.total_seconds())
    })

if __name__ == '__main__':
    app.run(debug=True)
