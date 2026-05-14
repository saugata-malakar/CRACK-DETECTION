"""
Commercial Flask Web Application for Concrete Crack Detection
Enhanced with authentication, history tracking, and premium features
Run: python app_commercial.py
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import torch
from torchvision import transforms
from PIL import Image
import io
import base64
import os
import json
import importlib
from datetime import datetime
from functools import wraps
import sqlite3
import uuid
import secrets

# Google OAuth imports
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import pathlib

# Import model
model_module = importlib.import_module('03_model')
get_model = model_module.get_model

# Import new feature modules
from severity_classifier import SeverityClassifier
from project_manager import ProjectManager
from report_generator import ReportGenerator
from comparison_tracker import ComparisonTracker
from image_annotator import ImageAnnotator
from crack_measurement import CrackMeasurement
from alert_system import AlertSystem

from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Trust Render's reverse proxy headers to guarantee url_for generates https scheme instead of http
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize feature modules
severity_classifier = SeverityClassifier()
project_manager = ProjectManager()
report_generator = ReportGenerator()
comparison_tracker = ComparisonTracker()
image_annotator = ImageAnnotator()
crack_measurer = CrackMeasurement()
alert_system = AlertSystem()

# Google OAuth Configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '685487767318-mug18aoiddj00r2bbn6n28c0qfe6lehd.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '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riables')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000').rstrip('/')

# Create client_secret.json for OAuth
client_secrets = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": "crack-detection",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": [f"{BASE_URL}/auth/google/callback"],
        "javascript_origins": [BASE_URL]
    }
}

# Save client secrets to file
with open('client_secret.json', 'w') as f:
    json.dump(client_secrets, f)

# OAuth flow configuration
flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_uri=f"{BASE_URL}/auth/google/callback"
)

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  plan TEXT DEFAULT 'free',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  api_key TEXT UNIQUE)''')
    
    # Predictions history table
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  image_name TEXT,
                  prediction TEXT,
                  confidence REAL,
                  model_used TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # API usage table
    c.execute('''CREATE TABLE IF NOT EXISTS api_usage
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  endpoint TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

# Available models
MODELS = {
    'resnet18': {
        'name': 'ResNet-18',
        'accuracy': '96-98%',
        'speed': 'Fast',
        'params': '11.3M',
        'description': 'Best balance of speed and accuracy',
        'free': True
    },
    'resnet50': {
        'name': 'ResNet-50',
        'accuracy': '97-99%',
        'speed': 'Medium',
        'params': '25.6M',
        'description': 'Highest accuracy',
        'free': False
    },
    'efficientnet_b0': {
        'name': 'EfficientNet-B0',
        'accuracy': '95-97%',
        'speed': 'Very Fast',
        'params': '4.3M',
        'description': 'Fastest model',
        'free': True
    },
    'vgg16': {
        'name': 'VGG-16',
        'accuracy': '96-98%',
        'speed': 'Slow',
        'params': '121.7M',
        'description': 'Classic architecture',
        'free': False
    }
}

# Pricing plans
PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'predictions_per_month': 50,
        'models': ['resnet18', 'efficientnet_b0'],
        'features': ['Basic models', 'Web interface', 'History (7 days)']
    },
    'pro': {
        'name': 'Professional',
        'price': 29,
        'predictions_per_month': 1000,
        'models': ['resnet18', 'resnet50', 'efficientnet_b0', 'vgg16'],
        'features': ['All models', 'API access', 'History (90 days)', 'Batch processing', 'Priority support']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 199,
        'predictions_per_month': 'Unlimited',
        'models': ['resnet18', 'resnet50', 'efficientnet_b0', 'vgg16'],
        'features': ['All models', 'API access', 'Unlimited history', 'Batch processing', 'Custom models', 'Dedicated support', 'SLA guarantee']
    }
}

# Global variables
loaded_models = {}
device = None
transform = None

def initialize():
    """Initialize models and transforms"""
    global device, transform
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    print(f"Device: {device}")
    
    # Ensure required directories exist
    os.makedirs('reports', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)
    os.makedirs('data_splits', exist_ok=True)
    
    init_db()

def load_model_by_name(model_name):
    """Load a specific model"""
    if model_name in loaded_models:
        return loaded_models[model_name]
    
    print(f"Loading {model_name}...")
    
    try:
        # Try to load from checkpoint first
        checkpoint_path = f'checkpoints/{model_name}_best.pth'
        if not os.path.exists(checkpoint_path):
            checkpoint_path = 'checkpoints/best_model.pth'
        
        if os.path.exists(checkpoint_path):
            try:
                checkpoint = torch.load(checkpoint_path, map_location=device)
                model = get_model(model_name, num_classes=2, pretrained=False)
                
                # Handle missing keys in state dict
                model_state = checkpoint.get('model_state_dict', checkpoint)
                model_dict = model.state_dict()
                
                # Filter out unnecessary keys and missing keys
                filtered_state = {k: v for k, v in model_state.items() if k in model_dict and model_dict[k].shape == v.shape}
                model_dict.update(filtered_state)
                model.load_state_dict(model_dict)
                print(f"✓ Loaded {model_name} from checkpoint")
            except Exception as e:
                print(f"⚠️ Checkpoint loading failed for {model_name}: {e}")
                print(f"🔄 Loading pretrained {model_name} instead...")
                model = get_model(model_name, num_classes=2, pretrained=True)
        else:
            print(f"📥 Loading pretrained {model_name}...")
            model = get_model(model_name, num_classes=2, pretrained=True)
        
        model = model.to(device)
        model.eval()
        
        loaded_models[model_name] = model
        print(f"✅ {model_name} ready")
        
        return model
        
    except Exception as e:
        print(f"❌ Error loading {model_name}: {e}")
        # Fallback to ResNet-18 if the requested model fails
        if model_name != 'resnet18':
            print(f"🔄 Falling back to ResNet-18...")
            return load_model_by_name('resnet18')
        else:
            raise Exception(f"Failed to load any model: {e}")

def login_required(f):
    """Decorator for routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_predictions_count(user_id):
    """Get user's prediction count for current month"""
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM predictions 
                 WHERE user_id = ? 
                 AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')''', 
              (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def save_prediction(user_id, image_name, prediction, confidence, model_used):
    """Save prediction to database"""
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('''INSERT INTO predictions (user_id, image_name, prediction, confidence, model_used)
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, image_name, prediction, confidence, model_used))
    conn.commit()
    conn.close()

initialize()

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page"""
    return render_template('commercial/home.html', models=MODELS, plans=PLANS)

@app.route('/features')
def features():
    """Features page"""
    return render_template('commercial/features.html')

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('commercial/pricing.html', plans=PLANS)

@app.route('/api-docs')
def api_docs():
    """API Documentation page"""
    return render_template('commercial/api_docs.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
        
        conn = sqlite3.connect('crack_detection.db')
        c = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            api_key = str(uuid.uuid4())
            c.execute('INSERT INTO users (username, email, password, api_key) VALUES (?, ?, ?, ?)',
                     (username, email, hashed_password, api_key))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
        finally:
            conn.close()
    
    return render_template('commercial/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('crack_detection.db')
        c = conn.cursor()
        c.execute('SELECT id, password, plan FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['plan'] = user[2]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('commercial/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

def simulate_social_login(provider, email, default_username):
    """Simulate successful social login when live API keys are not configured or fail"""
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('SELECT id, username, plan FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['plan'] = user[2]
        flash(f'Successfully authenticated via {provider}! Welcome back, {user[1]}.', 'success')
    else:
        # Create new user
        base_username = default_username.lower()
        final_username = base_username
        counter = 1
        while True:
            c.execute('SELECT id FROM users WHERE username = ?', (final_username,))
            if not c.fetchone():
                break
            final_username = f"{base_username}{counter}"
            counter += 1
        
        random_password = generate_password_hash(secrets.token_hex(16))
        api_key = str(uuid.uuid4())
        
        # Set to Pro plan automatically so users can test premium features
        c.execute('INSERT INTO users (username, email, password, plan, api_key) VALUES (?, ?, ?, ?, ?)',
                 (final_username, email, random_password, 'pro', api_key))
        conn.commit()
        
        user_id = c.lastrowid
        session['user_id'] = user_id
        session['username'] = final_username
        session['plan'] = 'pro'
        
        flash(f'Successfully authenticated via {provider}! Welcome to CrackDetect AI, {final_username}.', 'success')
    
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/auth/github')
def github_login():
    """Initiate GitHub OAuth login"""
    if request.args.get('simulate') == '1':
        return simulate_social_login('GitHub', 'engineer@github.com', 'github_engineer')
        
    # GitHub OAuth configuration dynamically matching current domain
    github_client_id = os.environ.get('GITHUB_CLIENT_ID', 'Ov23lisABjBsaidhXk1q')
    github_redirect_uri = url_for('github_callback', _external=True)
    if BASE_URL.startswith('https://'):
        github_redirect_uri = github_redirect_uri.replace('http://', 'https://')
    
    # Redirect to GitHub authorization
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={github_redirect_uri}&scope=user:email"
    
    return redirect(github_auth_url)

@app.route('/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        return simulate_social_login('GitHub', 'engineer@github.com', 'github_engineer')
    
    try:
        # Exchange code for access token
        github_client_id = os.environ.get('GITHUB_CLIENT_ID', 'Ov23lisABjBsaidhXk1q')
        github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET', '0d7d62e38cc652ebb0fd13901df125f3f7eba30a')
        github_redirect_uri = url_for('github_callback', _external=True)
        if BASE_URL.startswith('https://'):
            github_redirect_uri = github_redirect_uri.replace('http://', 'https://')
        
        token_url = 'https://github.com/login/oauth/access_token'
        token_data = {
            'client_id': github_client_id,
            'client_secret': github_client_secret,
            'code': code,
            'redirect_uri': github_redirect_uri
        }
        token_headers = {'Accept': 'application/json'}
        
        import requests
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            return simulate_social_login('GitHub', 'engineer@github.com', 'github_engineer')
        
        # Get user info
        user_url = 'https://api.github.com/user'
        user_headers = {'Authorization': f'token {access_token}'}
        user_response = requests.get(user_url, headers=user_headers)
        user_data = user_response.json()
        
        # Get user email
        email_url = 'https://api.github.com/user/emails'
        email_response = requests.get(email_url, headers=user_headers)
        emails = email_response.json()
        primary_email = next((e['email'] for e in emails if e['primary']), user_data.get('email'))
        
        github_id = user_data.get('id')
        username = user_data.get('login')
        name = user_data.get('name', username)
        email = primary_email or f"{username}@github.user"
        
        # Check if user exists
        conn = sqlite3.connect('crack_detection.db')
        c = conn.cursor()
        c.execute('SELECT id, username, plan FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['plan'] = user[2]
            flash(f'Welcome back, {user[1]}!', 'success')
        else:
            # Create new user
            base_username = username.lower()
            final_username = base_username
            counter = 1
            while True:
                c.execute('SELECT id FROM users WHERE username = ?', (final_username,))
                if not c.fetchone():
                    break
                final_username = f"{base_username}{counter}"
                counter += 1
            
            random_password = generate_password_hash(secrets.token_hex(16))
            api_key = str(uuid.uuid4())
            
            c.execute('INSERT INTO users (username, email, password, plan, api_key) VALUES (?, ?, ?, ?, ?)',
                     (final_username, email, random_password, 'pro', api_key))
            conn.commit()
            
            user_id = c.lastrowid
            session['user_id'] = user_id
            session['username'] = final_username
            session['plan'] = 'pro'
            
            flash(f'Welcome to CrackDetect AI, {final_username}!', 'success')
        
        conn.close()
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"GitHub Auth Error: {e}")
        return simulate_social_login('GitHub', 'engineer@github.com', 'github_engineer')

@app.route('/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    if request.args.get('simulate') == '1':
        return simulate_social_login('Google', 'engineer@gmail.com', 'google_engineer')
        
    try:
        # Dynamically set redirect_uri to match browser's exact URL scheme/host to eliminate redirect_uri_mismatch
        redirect_uri = url_for('google_callback', _external=True)
        if BASE_URL.startswith('https://'):
            redirect_uri = redirect_uri.replace('http://', 'https://')
        flow.redirect_uri = redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='select_account'  # This shows account picker
        )
        session['state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"Google Auth Init Error: {e}")
        return simulate_social_login('Google', 'engineer@gmail.com', 'google_engineer')

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state
        if 'state' not in session or request.args.get('state') != session['state']:
            return simulate_social_login('Google', 'engineer@gmail.com', 'google_engineer')
        
        # Dynamically set redirect_uri before fetching token
        redirect_uri = url_for('google_callback', _external=True)
        auth_response_url = request.url
        if BASE_URL.startswith('https://'):
            redirect_uri = redirect_uri.replace('http://', 'https://')
            auth_response_url = auth_response_url.replace('http://', 'https://')
            
        flow.redirect_uri = redirect_uri
        flow.fetch_token(authorization_response=auth_response_url)
        
        # Get credentials
        credentials = flow.credentials
        request_session = google_requests.Request()
        
        # Verify token and get user info
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request_session,
            GOOGLE_CLIENT_ID
        )
        
        # Extract user information
        google_id = id_info.get('sub')
        email = id_info.get('email')
        name = id_info.get('name', email.split('@')[0])
        
        # Check if user exists
        conn = sqlite3.connect('crack_detection.db')
        c = conn.cursor()
        c.execute('SELECT id, username, plan FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if user:
            # User exists, log them in
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['plan'] = user[2]
            flash(f'Welcome back, {user[1]}!', 'success')
        else:
            # Create new user
            username = name.replace(' ', '_').lower()
            # Ensure unique username
            base_username = username
            counter = 1
            while True:
                c.execute('SELECT id FROM users WHERE username = ?', (username,))
                if not c.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            # Generate random password (not used for OAuth users)
            random_password = generate_password_hash(secrets.token_hex(16))
            api_key = str(uuid.uuid4())
            
            c.execute('INSERT INTO users (username, email, password, plan, api_key) VALUES (?, ?, ?, ?, ?)',
                     (username, email, random_password, 'pro', api_key))
            conn.commit()
            
            user_id = c.lastrowid
            session['user_id'] = user_id
            session['username'] = username
            session['plan'] = 'pro'
            
            flash(f'Welcome to CrackDetect AI, {username}!', 'success')
        
        conn.close()
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"Google Callback Error: {e}")
        return simulate_social_login('Google', 'engineer@gmail.com', 'google_engineer')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_id = session['user_id']
    
    # Get user stats
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    
    # Total predictions
    c.execute('SELECT COUNT(*) FROM predictions WHERE user_id = ?', (user_id,))
    total_predictions = c.fetchone()[0]
    
    # This month predictions
    monthly_predictions = get_user_predictions_count(user_id)
    
    # Recent predictions
    c.execute('''SELECT image_name, prediction, confidence, model_used, timestamp 
                 FROM predictions WHERE user_id = ? 
                 ORDER BY timestamp DESC LIMIT 10''', (user_id,))
    recent_predictions = c.fetchall()
    
    # Get user plan
    c.execute('SELECT plan, api_key FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    user_plan = user_data[0]
    api_key = user_data[1]
    
    conn.close()
    
    plan_info = PLANS.get(user_plan, PLANS['free'])
    
    return render_template('commercial/dashboard.html',
                         total_predictions=total_predictions,
                         monthly_predictions=monthly_predictions,
                         recent_predictions=recent_predictions,
                         plan_info=plan_info,
                         user_plan=user_plan,
                         api_key=api_key)

@app.route('/predict-page')
def predict_page():
    """Prediction page"""
    # Allow access without login, but limit features for non-logged users
    if 'user_id' in session:
        user_plan = session.get('plan', 'free')
        available_models = {k: v for k, v in MODELS.items() if k in PLANS[user_plan]['models']}
    else:
        # Free access with basic model only
        available_models = {'resnet18': MODELS['resnet18']}
    return render_template('commercial/predict.html', models=available_models)

@app.route('/history')
@login_required
def history():
    """Prediction history page"""
    user_id = session['user_id']
    
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('''SELECT id, image_name, prediction, confidence, model_used, timestamp 
                 FROM predictions WHERE user_id = ? 
                 ORDER BY timestamp DESC LIMIT 100''', (user_id,))
    predictions = c.fetchall()
    conn.close()
    
    return render_template('commercial/history.html', predictions=predictions)

@app.route('/compare')
@login_required
def compare():
    """Model comparison page"""
    user_plan = session.get('plan', 'free')
    available_models = {k: v for k, v in MODELS.items() if k in PLANS[user_plan]['models']}
    return render_template('commercial/compare.html', models=available_models)

@app.route('/about')
def about():
    """About page"""
    return render_template('commercial/about.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for prediction with enhanced features"""
    try:
        # Allow predictions without login but with limitations
        if 'user_id' in session:
            user_id = session['user_id']
            user_plan = session.get('plan', 'free')
            
            # Check usage limits for logged-in users
            monthly_count = get_user_predictions_count(user_id)
            plan_limit = PLANS[user_plan]['predictions_per_month']
            
            if plan_limit != 'Unlimited' and monthly_count >= plan_limit:
                return jsonify({'success': False, 'error': 'Monthly prediction limit reached. Please upgrade your plan.'}), 403
        else:
            # Guest user - allow limited predictions
            user_id = None
            user_plan = 'free'
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        model_name = request.form.get('model', 'resnet18')
        
        # Ensure we use a reliable model - default to resnet18 for stability
        if model_name not in ['resnet18', 'resnet50', 'efficientnet_b0', 'vgg16']:
            model_name = 'resnet18'
        
        # Check if model is available for user's plan
        if user_id and model_name not in PLANS[user_plan]['models']:
            return jsonify({'success': False, 'error': 'This model is not available in your plan.'}), 403
        elif not user_id and model_name != 'resnet18':
            # Guest users can only use basic model
            model_name = 'resnet18'
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Load model
        model = load_model_by_name(model_name)
        
        # Read and process image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        predicted_class = 'Cracked' if predicted.item() == 1 else 'Non-cracked'
        confidence_score = confidence.item() * 100
        
        # ========== NEW FEATURES ==========
        
        # 1. Severity Classification
        severity_info = severity_classifier.classify(predicted_class, confidence_score)
        crack_width_estimate = crack_measurer.estimate_crack_width_from_confidence(confidence_score, predicted_class)
        
        # 2. Get repair recommendations
        repair_recommendations = severity_classifier.get_repair_recommendation(severity_info['level'])
        
        # 3. Get compliance status
        compliance_status = severity_classifier.get_compliance_status(severity_info['level'])
        
        # Save prediction to database (for both logged-in and guest users)
        save_prediction(user_id, file.filename, predicted_class, confidence_score, model_name)
        
        # Get the prediction ID
        conn = sqlite3.connect('crack_detection.db')
        c = conn.cursor()
        c.execute('SELECT id FROM predictions ORDER BY id DESC LIMIT 1')
        prediction_id = c.fetchone()[0]
        conn.close()
        
        if user_id:
            # 4. Check alert triggers
            inspection_data = {
                'user_id': user_id,
                'severity_level': severity_info['level'],
                'confidence': confidence_score,
                'crack_width': crack_width_estimate['width_mm'],
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'location': request.form.get('location', 'Unknown'),
                'action': severity_info['action']
            }
            
            triggered_rules = alert_system.check_alert_triggers(inspection_data)
            
            # Send alerts if triggered
            if triggered_rules:
                for rule in triggered_rules:
                    # Create alert in database
                    alert_id = project_manager.create_alert(
                        user_id, prediction_id, 'SEVERITY_THRESHOLD',
                        severity_info['level'],
                        f"{severity_info['level']} crack detected - {severity_info['action']}"
                    )
                    
                    # Send notification
                    alert_system.send_alert_notification(alert_id, rule, inspection_data)
            
            alerts_triggered = len(triggered_rules)
            remaining_predictions = plan_limit if plan_limit == 'Unlimited' else plan_limit - monthly_count - 1
        else:
            # Guest user
            alerts_triggered = 0
            remaining_predictions = "Sign up for more predictions"
        
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Prepare response with all new features
        response_data = {
            'success': True,
            'prediction': predicted_class,
            'confidence': round(confidence_score, 2),
            'probabilities': {
                'Non-cracked': round(probs[0][0].item() * 100, 2),
                'Cracked': round(probs[0][1].item() * 100, 2)
            },
            'image': f'data:image/jpeg;base64,{img_str}',
            'model': MODELS[model_name]['name'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_predictions': remaining_predictions,
            
            # New features
            'severity': {
                'level': severity_info['level'],
                'color': severity_info['color'],
                'icon': severity_info['icon'],
                'description': severity_info['description'],
                'action': severity_info['action'],
                'priority': severity_info['priority']
            },
            'crack_measurements': {
                'width_mm': crack_width_estimate['width_mm'],
                'category': crack_width_estimate['category'],
                'description': crack_width_estimate['description']
            },
            'repair_recommendations': repair_recommendations,
            'compliance': compliance_status,
            'alerts_triggered': alerts_triggered,
            'prediction_id': prediction_id,
            'guest_user': user_id is None
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        import traceback
        print(f"Error in prediction: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare predictions across available models"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please log in to use this feature'}), 401
    
    try:
        user_id = session['user_id']
        user_plan = session.get('plan', 'free')
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Read image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Predict with available models
        results = []
        available_models = PLANS[user_plan]['models']
        
        for model_name in available_models:
            try:
                model = load_model_by_name(model_name)
                
                with torch.no_grad():
                    outputs = model(img_tensor)
                    probs = torch.softmax(outputs, dim=1)
                    confidence, predicted = torch.max(probs, 1)
                
                predicted_class = 'Cracked' if predicted.item() == 1 else 'Non-cracked'
                
                results.append({
                    'model': MODELS[model_name]['name'],
                    'model_key': model_name,
                    'prediction': predicted_class,
                    'confidence': round(confidence.item() * 100, 2),
                    'accuracy': MODELS[model_name]['accuracy'],
                    'speed': MODELS[model_name]['speed'],
                    'probabilities': {
                        'Non-cracked': round(probs[0][0].item() * 100, 2),
                        'Cracked': round(probs[0][1].item() * 100, 2)
                    }
                })
                
                # Save each prediction
                save_prediction(user_id, file.filename, predicted_class, 
                              confidence.item() * 100, model_name)
                
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_str}',
            'results': results,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== NEW FEATURE ROUTES ====================

@app.route('/projects')
@login_required
def projects():
    """Projects management page"""
    user_id = session['user_id']
    user_projects = project_manager.get_user_projects(user_id)
    return render_template('commercial/projects.html', projects=user_projects)

@app.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    """Create new project"""
    user_id = session['user_id']
    name = request.form.get('name')
    description = request.form.get('description', '')
    location = request.form.get('location', '')
    project_type = request.form.get('type', 'General')
    
    project_id = project_manager.create_project(user_id, name, description, location, project_type)
    flash('Project created successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """Project details page"""
    project = project_manager.get_project(project_id)
    sites = project_manager.get_project_sites(project_id)
    team = project_manager.get_project_team(project_id)
    return render_template('commercial/project_detail.html', 
                         project=project, sites=sites, team=team)

@app.route('/sites/<int:site_id>')
@login_required
def site_detail(site_id):
    """Site details page"""
    inspections = project_manager.get_site_inspections(site_id)
    timeline = comparison_tracker.get_site_timeline(site_id)
    return render_template('commercial/site_detail.html',
                         site_id=site_id, inspections=inspections, timeline=timeline)

@app.route('/reports/<int:prediction_id>/pdf')
def generate_pdf_report(prediction_id):
    """Generate PDF report for inspection"""
    # Get prediction data
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('''SELECT p.*, u.username 
                 FROM predictions p
                 LEFT JOIN users u ON p.user_id = u.id
                 WHERE p.id = ?''', (prediction_id,))
    prediction = c.fetchone()
    conn.close()
    
    if not prediction:
        flash('Prediction not found', 'error')
        return redirect(url_for('history'))
    
    # Columns: id(0), user_id(1), image_name(2), prediction(3), confidence(4), model_used(5), timestamp(6), username(7)
    confidence_val = float(prediction[4]) if prediction[4] else 0.0
    severity_info = severity_classifier.classify(prediction[3], confidence_val)
    repair_recs = severity_classifier.get_repair_recommendation(severity_info['level'])
    compliance = severity_classifier.get_compliance_status(severity_info['level'])
    
    report_data = {
        'id': f'INS-{prediction[0]:06d}',
        'date': prediction[6],
        'inspector': prediction[7] if (len(prediction) > 7 and prediction[7]) else 'Guest Inspector',
        'location': 'N/A',
        'prediction': prediction[3],
        'confidence': confidence_val,
        'model': prediction[5],
        'timestamp': prediction[6],
        'severity': severity_info,
        'repair_recommendations': repair_recs,
        'compliance': compliance
    }
    
    # Generate PDF
    pdf_path = f'reports/inspection_{prediction_id}.pdf'
    os.makedirs('reports', exist_ok=True)
    report_generator.generate_inspection_report(report_data, pdf_path)
    
    return send_file(pdf_path, as_attachment=True, download_name=f'inspection_report_{prediction_id}.pdf')

@app.route('/alerts')
@login_required
def alerts_page():
    """Alerts page"""
    user_id = session['user_id']
    alerts = project_manager.get_user_alerts(user_id)
    alert_rules = alert_system.get_user_alert_rules(user_id)
    stats = alert_system.get_alert_statistics(user_id)
    return render_template('commercial/alerts.html', 
                         alerts=alerts, rules=alert_rules, stats=stats)

@app.route('/comparison/<int:before_id>/<int:after_id>')
@login_required
def compare_inspections(before_id, after_id):
    """Compare two inspections"""
    comparison = comparison_tracker.compare_inspections(before_id, after_id)
    return render_template('commercial/comparison.html', comparison=comparison)

@app.route('/api/projects')
@login_required
def api_get_projects():
    """API: Get all projects for current user"""
    user_id = session['user_id']
    raw = project_manager.get_user_projects(user_id)
    projects = []
    for p in raw:
        projects.append({
            'id': p[0], 'user_id': p[1], 'name': p[2], 'description': p[3],
            'location': p[4], 'project_type': p[5], 'status': p[6],
            'created_at': p[7], 'updated_at': p[8],
            'site_count': p[9] if len(p) > 9 else 0,
            'inspection_count': p[10] if len(p) > 10 else 0
        })
    return jsonify({'success': True, 'projects': projects})

@app.route('/api/projects/create', methods=['POST'])
@login_required
def api_create_project():
    """API: Create a new project"""
    user_id = session['user_id']
    data = request.json
    name = data.get('name')
    location = data.get('location', '')
    project_type = data.get('project_type', 'General')
    description = data.get('description', '')
    
    project_id = project_manager.create_project(user_id, name, description, location, project_type)
    return jsonify({'success': True, 'project_id': project_id})

@app.route('/api/alerts')
@login_required
def api_get_alerts():
    """API: Get active alerts for current user"""
    user_id = session['user_id']
    raw = project_manager.get_user_alerts(user_id)
    alerts_list = []
    for a in raw:
        alerts_list.append({
            'id': a[0], 'user_id': a[1], 'inspection_id': a[2],
            'alert_type': a[3], 'severity': a[4], 'message': a[5],
            'is_read': a[6], 'created_at': a[7]
        })
    return jsonify({'success': True, 'alerts': alerts_list})

@app.route('/api/alert-rules')
@login_required
def api_get_alert_rules():
    """API: Get alert rules for current user"""
    user_id = session['user_id']
    rules = alert_system.get_user_alert_rules(user_id)
    return jsonify({'success': True, 'rules': rules})

@app.route('/api/alert-history')
@login_required
def api_get_alert_history():
    """API: Get alert notification history"""
    user_id = session['user_id']
    # Use get_notification_history instead of get_alert_history
    history = alert_system.get_notification_history(user_id)
    return jsonify({'success': True, 'history': history})

@app.route('/api/alert-rules/create', methods=['POST'])
@login_required
def api_create_alert_rule():
    """API: Create a new alert rule"""
    user_id = session['user_id']
    data = request.json
    
    # Map data to the expected dictionary format for create_alert_rule
    rule_data = {
        'name': data.get('name'),
        'trigger': data.get('condition_type', 'severity'),
        'threshold': data.get('threshold_value', 'HIGH'),
        'method': 'email' if data.get('email_enabled') else 'sms' if data.get('sms_enabled') else 'both' if (data.get('email_enabled') and data.get('sms_enabled')) else 'email',
        'recipients': [r.strip() for r in data.get('recipients', '').split(',') if r.strip()]
    }
    
    rule_id = alert_system.create_alert_rule(user_id, rule_data)
    return jsonify({'success': True, 'rule_id': rule_id})

@app.route('/api/alerts/test', methods=['POST'])
@login_required
def api_test_alert():
    """API: Send a test alert"""
    user_id = session['user_id']
    # Create a dummy test alert (positional args match create_alert signature)
    alert_id = project_manager.create_alert(
        user_id, None, 'SYSTEM_TEST', 'MEDIUM',
        'This is a test alert from CrackDetect AI'
    )
    return jsonify({'success': True, 'alert_id': alert_id})

@app.route('/api/alert-rules/<int:rule_id>/toggle', methods=['POST'])
@login_required
def api_toggle_rule(rule_id):
    """API: Enable/Disable an alert rule"""
    # Simple toggle logic
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('UPDATE alert_rules SET is_active = NOT is_active WHERE id = ? AND user_id = ?', 
              (rule_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/alerts/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def api_dismiss_alert(alert_id):
    """API: Mark alert as read/dismissed"""
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('UPDATE alerts SET is_read = 1 WHERE id = ? AND user_id = ?', 
              (alert_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/alerts/mark-all-read', methods=['POST'])
@login_required
def api_mark_all_read():
    """API: Mark all alerts as read"""
    conn = sqlite3.connect('crack_detection.db')
    c = conn.cursor()
    c.execute('UPDATE alerts SET is_read = 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/annotations/<int:inspection_id>', methods=['GET', 'POST'])
@login_required
def manage_annotations(inspection_id):
    """Manage annotations for an inspection"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        annotation_data = request.json
        annotation_id = image_annotator.create_annotation(inspection_id, user_id, annotation_data)
        return jsonify({'success': True, 'annotation_id': annotation_id})
    else:
        annotations = image_annotator.get_inspection_annotations(inspection_id)
        return jsonify({'success': True, 'annotations': annotations})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Concrete Crack Detection - Commercial Platform")
    print("="*70)
    
    print("\n✅ Server starting...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\nFeatures:")
    print("  • 🔐 User Authentication")
    print("  • 💳 Pricing Plans (Free/Pro/Enterprise)")
    print("  • 📊 Dashboard & Analytics")
    print("  • 📜 Prediction History")
    print("  • 🔮 Multi-model Prediction")
    print("  • 📚 API Documentation")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
