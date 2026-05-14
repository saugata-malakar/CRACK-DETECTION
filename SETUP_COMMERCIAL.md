# 🚀 CrackDetect AI - Commercial Setup Guide

Complete guide to set up and run the commercial crack detection platform.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)
- 4GB RAM minimum
- GPU recommended (CUDA support for faster inference)

## 🔧 Installation Steps

### 1. Clone or Download the Project

```bash
# If using Git
git clone https://github.com/saugata-malakar/concrete-crack-detection.git
cd concrete-crack-detection

# Or download and extract the ZIP file
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install commercial version dependencies
pip install -r requirements_commercial.txt

# Or install manually
pip install torch torchvision Flask Werkzeug Pillow numpy pandas matplotlib scikit-learn
```

### 4. Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import flask; print(f'Flask: {flask.__version__}')"
```

## 🎯 Running the Application

### Quick Start

```bash
# Run the commercial platform
python app_commercial.py
```

The application will start on `http://localhost:5000`

### First Time Setup

1. **Open your browser** and navigate to `http://localhost:5000`
2. **Register an account** by clicking "Get Started" or "Register"
3. **Login** with your credentials
4. **Start detecting cracks!**

## 👤 Creating Your First Account

### Registration

1. Go to `http://localhost:5000/register`
2. Fill in the form:
   - Username: Choose a unique username
   - Email: Your email address
   - Password: Strong password (8+ characters, mixed case, numbers)
3. Accept terms and conditions
4. Click "Create Account"

### Login

1. Go to `http://localhost:5000/login`
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to your dashboard

## 🔑 Getting Your API Key

1. Login to your account
2. Go to Dashboard (`/dashboard`)
3. Scroll to the "API Key" section
4. Copy your API key
5. Use it in your API requests

**Note**: API access is only available for Pro and Enterprise plans.

## 📊 Using the Platform

### Web Interface

#### 1. Single Prediction
- Go to "Predict" page
- Select an AI model
- Upload an image (JPG, PNG, max 16MB)
- View results with confidence scores

#### 2. Model Comparison
- Go to "Compare" page
- Upload an image
- See predictions from all available models
- Compare accuracy and confidence

#### 3. View History
- Go to "History" page
- See all your past predictions
- Filter by model or result
- Download reports

### API Usage

#### Python Example

```python
import requests

# Your API key from dashboard
API_KEY = "your-api-key-here"

# Predict endpoint
url = "http://localhost:5000/api/predict"
headers = {"Authorization": f"Bearer {API_KEY}"}
files = {"file": open("crack_image.jpg", "rb")}
data = {"model": "resnet18"}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

if result['success']:
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}%")
else:
    print(f"Error: {result['error']}")
```

#### JavaScript Example

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('model', 'resnet18');

fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Prediction:', data.prediction);
    console.log('Confidence:', data.confidence + '%');
});
```

## 🎨 Customization

### Changing Colors

Edit `templates/commercial/base.html` and modify CSS variables:

```css
:root {
    --primary: #6366f1;      /* Primary color */
    --secondary: #8b5cf6;    /* Secondary color */
    --accent: #ec4899;       /* Accent color */
    --success: #10b981;      /* Success color */
    --warning: #f59e0b;      /* Warning color */
    --danger: #ef4444;       /* Danger color */
}
```

### Modifying Pricing Plans

Edit `app_commercial.py` and update the `PLANS` dictionary:

```python
PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'predictions_per_month': 50,
        'models': ['resnet18', 'efficientnet_b0'],
        'features': ['Basic models', 'Web interface', 'History (7 days)']
    },
    # Add or modify plans here
}
```

### Adding New Models

1. Add model to `MODELS` dictionary in `app_commercial.py`
2. Train or download model checkpoint
3. Place checkpoint in `checkpoints/` folder
4. Update pricing plans to include new model

## 🗄️ Database Management

### View Database

```bash
# Open SQLite database
sqlite3 crack_detection.db

# View users
SELECT * FROM users;

# View predictions
SELECT * FROM predictions;

# Exit
.exit
```

### Backup Database

```bash
# Create backup
copy crack_detection.db crack_detection_backup.db

# Or use SQLite command
sqlite3 crack_detection.db ".backup crack_detection_backup.db"
```

### Reset Database

```bash
# Delete database file
del crack_detection.db  # Windows
rm crack_detection.db   # Linux/Mac

# Restart application to create fresh database
python app_commercial.py
```

## 🚀 Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app_commercial.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app_commercial.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel --prod
```

### Deploy to Heroku

1. Create `Procfile`:
```
web: gunicorn app_commercial:app
```

2. Create `runtime.txt`:
```
python-3.9.16
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Deploy to AWS/Azure/GCP

See detailed deployment guides in the documentation.

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Change port in app_commercial.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

#### 2. Model Not Found

```bash
# Download or train models first
python 06_train.py

# Or use pretrained models (will download automatically)
```

#### 3. Database Locked

```bash
# Close all connections and restart
# Or delete and recreate database
```

#### 4. Import Errors

```bash
# Reinstall dependencies
pip install -r requirements_commercial.txt --force-reinstall
```

#### 5. CUDA Out of Memory

```python
# In app_commercial.py, force CPU usage
device = torch.device('cpu')  # Instead of 'cuda'
```

## 📈 Performance Optimization

### 1. Use GPU

```python
# Verify CUDA is available
python -c "import torch; print(torch.cuda.is_available())"
```

### 2. Model Caching

Models are automatically cached after first load. No action needed.

### 3. Image Optimization

- Resize large images before upload
- Use JPEG format for smaller file sizes
- Compress images to reduce upload time

### 4. Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX idx_user_predictions ON predictions(user_id);
CREATE INDEX idx_timestamp ON predictions(timestamp);
```

## 🔒 Security Best Practices

1. **Change Secret Key**
```python
# In app_commercial.py
app.secret_key = 'your-very-secure-random-key-here'
```

2. **Use Environment Variables**
```bash
# Create .env file
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///crack_detection.db
```

3. **Enable HTTPS** (in production)
4. **Regular Backups** of database
5. **Update Dependencies** regularly

## 📚 Additional Resources

- **Documentation**: See README_COMMERCIAL.md
- **API Reference**: Visit `/api-docs` page
- **GitHub**: https://github.com/saugata-malakar/concrete-crack-detection
- **Live Demo**: https://concrete-crack-detection-nine.vercel.app

## 💡 Tips & Tricks

1. **Keyboard Shortcuts**
   - `Ctrl + /` to open search
   - `Ctrl + K` for quick actions

2. **Batch Processing**
   - Use API for processing multiple images
   - Write scripts for automation

3. **Model Selection**
   - ResNet-18: Best for real-time applications
   - ResNet-50: Best for highest accuracy
   - EfficientNet-B0: Best for mobile/edge devices
   - VGG-16: Best for research/comparison

4. **Monitoring Usage**
   - Check dashboard regularly
   - Set up alerts for limit approaching
   - Upgrade plan before hitting limits

## 🆘 Getting Help

- **Issues**: Open GitHub issue
- **Email**: support@crackdetect.ai
- **Community**: Join our Discord/Slack
- **Documentation**: Read full docs

## 🎉 You're All Set!

Your CrackDetect AI commercial platform is now ready to use. Start detecting cracks with AI!

---

**Happy Detecting! 🏗️🤖**
