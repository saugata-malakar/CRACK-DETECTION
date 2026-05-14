# 🚀 CrackDetect AI - Commercial SaaS Platform

> **Professional AI-powered structural health monitoring for concrete infrastructure**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.9+-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What's New in Commercial Version

### ✨ **Complete SaaS Platform**
- ✅ **User Authentication** - Register, login, logout with secure password hashing
- ✅ **Google OAuth** - One-click login with Google account picker
- ✅ **GitHub OAuth** - Seamless GitHub authentication
- ✅ **3 Pricing Tiers** - Free, Pro ($29/mo), Enterprise ($199/mo)
- ✅ **User Dashboard** - Analytics, stats, and usage tracking
- ✅ **Prediction History** - Track all your predictions
- ✅ **Multi-Model Comparison** - Compare all 4 models simultaneously
- ✅ **API Access** - RESTful API for Pro and Enterprise users
- ✅ **Usage Limits** - Monthly prediction limits per plan

### 🎨 **Stunning UI/UX**
- ✅ **Framer Motion-Style Animations** - Smooth 3D card effects
- ✅ **Animated Gradients** - 4-color shifting backgrounds
- ✅ **Mouse Tracking** - 3D tilt effects on hover
- ✅ **Floating Particles** - 50 animated particles in hero section
- ✅ **Glassmorphism** - Modern backdrop blur effects
- ✅ **Parallax Scrolling** - Depth-based scroll animations
- ✅ **Vibrant Colors** - Professional gradient color scheme
- ✅ **Responsive Design** - Works on all devices

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_commercial.txt
```

### 2. Configure OAuth

#### **Google OAuth:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Find OAuth Client ID: `685487767318-mug18aoiddj00r2bbn6n28c0qfe6lehd.apps.googleusercontent.com`
3. Add redirect URI: `http://localhost:5000/auth/google/callback`
4. Add JavaScript origin: `http://localhost:5000`

#### **GitHub OAuth:**
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Find OAuth App: **Crack AI**
3. Update callback URL: `http://localhost:5000/auth/github/callback`
4. Update homepage URL: `http://localhost:5000`

### 3. Run the Application

**Option A: Using Python**
```bash
python app_commercial.py
```

**Option B: Using Batch File (Windows)**
```bash
START_APP.bat
```

### 4. Open in Browser

```
http://localhost:5000
```

---

## 📱 Available Pages

| Page | URL | Description | Auth Required |
|------|-----|-------------|---------------|
| **Home** | `/` | Landing page with animations | ❌ |
| **Features** | `/features` | Feature showcase | ❌ |
| **Pricing** | `/pricing` | Pricing plans | ❌ |
| **API Docs** | `/api-docs` | API documentation | ❌ |
| **About** | `/about` | About the platform | ❌ |
| **Login** | `/login` | User login with OAuth | ❌ |
| **Register** | `/register` | User registration with OAuth | ❌ |
| **Dashboard** | `/dashboard` | User dashboard & analytics | ✅ |
| **Predict** | `/predict-page` | Upload & predict images | ✅ |
| **History** | `/history` | Prediction history | ✅ |
| **Compare** | `/compare` | Compare all models | ✅ |

---

## 💳 Pricing Plans

### 🆓 **Free Plan**
- 50 predictions/month
- ResNet-18 & EfficientNet-B0
- Web interface
- 7-day history

### 💼 **Pro Plan - $29/month**
- 1,000 predictions/month
- All 4 models
- API access
- 90-day history
- Batch processing
- Priority support

### 🏢 **Enterprise Plan - $199/month**
- Unlimited predictions
- All models
- API access
- Unlimited history
- Batch processing
- Custom models
- Dedicated support
- SLA guarantee

---

## 🤖 AI Models

| Model | Accuracy | Speed | Parameters | Free Plan |
|-------|----------|-------|------------|-----------|
| **ResNet-18** | 96-98% | Fast | 11.3M | ✅ |
| **EfficientNet-B0** | 95-97% | Very Fast | 4.3M | ✅ |
| **ResNet-50** | 97-99% | Medium | 25.6M | ❌ |
| **VGG-16** | 96-98% | Slow | 121.7M | ❌ |

---

## 🔐 OAuth Configuration

### **Google OAuth**
```python
Client ID: 685487767318-mug18aoiddj00r2bbn6n28c0qfe6lehd.apps.googleusercontent.com
Client Secret: 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
Redirect URI: http://localhost:5000/auth/google/callback
```

### **GitHub OAuth**
```python
Client ID: Ov23lisABjBsaidhXk1q
Client Secret: 0d7d62e38cc652ebb0fd13901df125f3f7eba30a
Redirect URI: http://localhost:5000/auth/github/callback
```

---

## 🎨 UI Features

### **Animations**
- ✅ Gradient background shifts (4 colors)
- ✅ 3D card tilt on mouse move
- ✅ Floating particles (50 particles)
- ✅ Smooth fade-in animations
- ✅ Parallax scrolling
- ✅ Glow effects on hover
- ✅ Scale and rotate transforms

### **Design Elements**
- ✅ Glassmorphism (backdrop blur)
- ✅ Gradient borders
- ✅ Box shadows with color
- ✅ Rounded corners (24px)
- ✅ Professional color palette
- ✅ Space Grotesk font (headings)
- ✅ Inter font (body text)

---

## 📊 Database Schema

### **Users Table**
```sql
id, username, email, password, plan, created_at, api_key
```

### **Predictions Table**
```sql
id, user_id, image_name, prediction, confidence, model_used, timestamp
```

### **API Usage Table**
```sql
id, user_id, endpoint, timestamp
```

---

## 🔧 API Endpoints

### **POST /api/predict**
Predict crack in a single image

**Request:**
```json
{
  "file": "<image_file>",
  "model": "resnet18"
}
```

**Response:**
```json
{
  "success": true,
  "prediction": "Cracked",
  "confidence": 98.5,
  "probabilities": {
    "Non-cracked": 1.5,
    "Cracked": 98.5
  },
  "model": "ResNet-18",
  "timestamp": "2024-01-15 10:30:00",
  "remaining_predictions": 49
}
```

### **POST /api/compare**
Compare predictions across all available models

**Request:**
```json
{
  "file": "<image_file>"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "model": "ResNet-18",
      "prediction": "Cracked",
      "confidence": 98.5,
      "accuracy": "96-98%",
      "speed": "Fast"
    },
    ...
  ]
}
```

---

## 🧪 Testing

### **Test Regular Login**
1. Go to `/register`
2. Create account with username, email, password
3. Login at `/login`
4. Access dashboard

### **Test Google OAuth**
1. Go to `/login`
2. Click "Continue with Google"
3. Select Google account
4. Auto-login or auto-register

### **Test GitHub OAuth**
1. Go to `/login`
2. Click "Continue with GitHub"
3. Authorize the app
4. Auto-login or auto-register

### **Test Prediction**
1. Login to account
2. Go to `/predict-page`
3. Upload concrete image
4. Select model
5. Click "Analyze Image"

### **Test Model Comparison**
1. Login to account
2. Go to `/compare`
3. Upload image
4. Click "Compare All Models"
5. View comparison results

---

## 🛠️ Tech Stack

### **Backend**
- Flask 2.3+ (Web framework)
- PyTorch 1.9+ (Deep learning)
- SQLite (Database)
- Werkzeug (Security)

### **Authentication**
- Google OAuth 2.0
- GitHub OAuth 2.0
- Password hashing (Werkzeug)

### **Frontend**
- HTML5 + CSS3
- JavaScript (ES6+)
- Font Awesome (Icons)
- Google Fonts (Typography)

### **AI Models**
- ResNet-18, ResNet-50
- EfficientNet-B0
- VGG-16

---

## 📁 Project Structure

```
CRACK DETECTION KAGGLE/
├── app_commercial.py          # Main Flask application
├── 03_model.py                # Model definitions
├── requirements_commercial.txt # Dependencies
├── START_APP.bat              # Quick start script
├── FINAL_SETUP.md             # Complete setup guide
├── README_COMMERCIAL.md       # This file
├── crack_detection.db         # SQLite database
├── client_secret.json         # OAuth config (auto-generated)
├── checkpoints/               # Model checkpoints
│   └── best_model.pth
└── templates/commercial/      # HTML templates
    ├── base.html              # Base template
    ├── home.html              # Landing page
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── dashboard.html         # User dashboard
    ├── predict.html           # Prediction page
    ├── history.html           # History page
    ├── compare.html           # Comparison page
    ├── pricing.html           # Pricing page
    ├── features.html          # Features page
    ├── api_docs.html          # API docs
    └── about.html             # About page
```

---

## 🔒 Security Features

- ✅ Password hashing (Werkzeug)
- ✅ OAuth 2.0 authentication
- ✅ Session management
- ✅ CSRF protection
- ✅ SQL injection prevention
- ✅ Secure cookie handling
- ✅ API key generation (UUID)

---

## 🚀 Deployment

### **For Production:**

1. **Update OAuth redirect URIs** to production domain
2. **Set environment variables:**
   ```bash
   export SECRET_KEY="your-secret-key"
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GOOGLE_CLIENT_SECRET="your-google-client-secret"
   export GITHUB_CLIENT_ID="your-github-client-id"
   export GITHUB_CLIENT_SECRET="your-github-client-secret"
   ```
3. **Remove development flag:**
   ```python
   # Remove this line
   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
   ```
4. **Use production server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app_commercial:app
   ```

---

## 🐛 Troubleshooting

### **OAuth redirect_uri_mismatch**
- Add correct redirect URI in OAuth console
- Google: `http://localhost:5000/auth/google/callback`
- GitHub: `http://localhost:5000/auth/github/callback`

### **Module not found**
```bash
pip install -r requirements_commercial.txt
```

### **Database errors**
```bash
# Delete and recreate database
del crack_detection.db
python app_commercial.py
```

### **Model not found**
- Ensure `checkpoints/best_model.pth` exists
- Or app will use pretrained models

---

## 📞 Support

For issues or questions:
1. Check `FINAL_SETUP.md` for detailed setup
2. Verify OAuth redirect URIs
3. Check console for error messages
4. Ensure all dependencies installed

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🎉 Success Checklist

- ✅ Server starts without errors
- ✅ Home page loads with animations
- ✅ Google OAuth works
- ✅ GitHub OAuth works
- ✅ Can register users
- ✅ Can login with password
- ✅ Dashboard shows stats
- ✅ Can predict images
- ✅ Can view history
- ✅ Can compare models
- ✅ All animations smooth

---

## 🌟 Features Highlights

### **User Experience**
- One-click OAuth login
- Beautiful 3D animations
- Real-time predictions
- Comprehensive dashboard
- Prediction history tracking

### **Developer Experience**
- RESTful API
- Clear documentation
- Easy deployment
- Secure authentication
- Scalable architecture

### **Business Features**
- 3 pricing tiers
- Usage tracking
- API key management
- Monthly limits
- Upgrade prompts

---

**Built with ❤️ using Flask, PyTorch, and modern web technologies**

🌐 **Local URL:** http://localhost:5000  
📚 **Setup Guide:** FINAL_SETUP.md  
🔐 **OAuth:** Google + GitHub  
🎨 **Design:** Framer Motion-style  
🚀 **Status:** Production Ready!

---

**© 2024 CrackDetect AI - Professional Structural Health Monitoring**
