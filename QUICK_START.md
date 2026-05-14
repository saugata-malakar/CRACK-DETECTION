# ⚡ Quick Start Guide - CrackDetect AI

## 🎯 You're Almost Ready!

Everything is configured and ready to go. Just follow these 3 simple steps:

---

## Step 1: Configure OAuth (5 minutes)

### 🔵 Google OAuth

1. Open: https://console.cloud.google.com/
2. Go to: **APIs & Services** → **Credentials**
3. Find your OAuth Client ID: `685487767318-mug18aoiddj00r2bbn6n28c0qfe6lehd.apps.googleusercontent.com`
4. Click on it to edit
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:5000/auth/google/callback
   ```
6. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:5000
   ```
7. Click **SAVE**

### ⚫ GitHub OAuth

1. Open: https://github.com/settings/developers
2. Find your OAuth App: **Crack AI**
3. Click on it to edit
4. Update **Authorization callback URL** to:
   ```
   http://localhost:5000/auth/github/callback
   ```
5. Update **Homepage URL** to:
   ```
   http://localhost:5000
   ```
6. Click **Update application**

---

## Step 2: Start the Application

### Option A: Double-click the batch file
```
START_APP.bat
```

### Option B: Run from command line
```bash
python app_commercial.py
```

---

## Step 3: Open in Browser

```
http://localhost:5000
```

---

## ✅ What You'll See

### 🏠 **Home Page**
- Beautiful animated gradient background
- 3D card effects with mouse tracking
- Floating particles
- Stats: 97% accuracy, 50ms speed, 56K+ images, 4 models

### 🔐 **Login/Register**
- Traditional username/password
- **Continue with Google** button (with account picker)
- **Continue with GitHub** button
- Beautiful glassmorphism design

### 📊 **Dashboard** (after login)
- Total predictions count
- Monthly usage
- Recent predictions history
- Your plan details
- API key

### 🔮 **Predict Page**
- Upload concrete images
- Select AI model
- Get instant predictions
- View confidence scores

### 📜 **History Page**
- View all past predictions
- Filter by model
- See timestamps and confidence

### ⚖️ **Compare Page**
- Upload one image
- Compare all available models
- See which model performs best

---

## 🎨 Features You'll Love

### **Animations**
- ✅ 4-color gradient background (shifts smoothly)
- ✅ 3D card tilt on mouse move (Framer Motion style)
- ✅ 50 floating particles in hero section
- ✅ Smooth fade-in animations
- ✅ Parallax scrolling effects
- ✅ Glow effects on hover
- ✅ Scale and rotate transforms

### **OAuth Login**
- ✅ Google account picker (shows all your accounts)
- ✅ GitHub authorization
- ✅ Auto-login for existing users
- ✅ Auto-register for new users
- ✅ Extracts email and name automatically

### **AI Models**
- ✅ ResNet-18 (96-98% accuracy, Fast) - FREE
- ✅ EfficientNet-B0 (95-97% accuracy, Very Fast) - FREE
- ✅ ResNet-50 (97-99% accuracy, Medium) - PRO
- ✅ VGG-16 (96-98% accuracy, Slow) - PRO

---

## 🧪 Test It Out

### Test 1: Regular Login
1. Click **Get Started** or **Register**
2. Fill in username, email, password
3. Click **Create Account**
4. Login with your credentials
5. You're in! 🎉

### Test 2: Google OAuth
1. Click **Login**
2. Click **Continue with Google**
3. Select your Google account
4. Automatically logged in! 🎉

### Test 3: GitHub OAuth
1. Click **Login**
2. Click **Continue with GitHub**
3. Authorize the app
4. Automatically logged in! 🎉

### Test 4: Predict Cracks
1. Login to your account
2. Go to **Predict** page
3. Upload a concrete image
4. Select a model (ResNet-18 or EfficientNet-B0 for free users)
5. Click **Analyze Image**
6. See results with confidence score! 🎉

### Test 5: Compare Models
1. Login to your account
2. Go to **Compare** page
3. Upload an image
4. Click **Compare All Models**
5. See how all models perform! 🎉

---

## 💳 Pricing Plans

### 🆓 Free Plan
- 50 predictions/month
- 2 models (ResNet-18, EfficientNet-B0)
- Web interface
- 7-day history

### 💼 Pro Plan - $29/month
- 1,000 predictions/month
- All 4 models
- API access
- 90-day history
- Batch processing

### 🏢 Enterprise - $199/month
- Unlimited predictions
- All models
- API access
- Unlimited history
- Custom models
- Dedicated support

---

## 🐛 Troubleshooting

### Problem: "redirect_uri_mismatch" error

**Solution:** You need to add the redirect URI in OAuth console

**For Google:**
1. Go to Google Cloud Console
2. Add: `http://localhost:5000/auth/google/callback`

**For GitHub:**
1. Go to GitHub Developer Settings
2. Add: `http://localhost:5000/auth/github/callback`

### Problem: "Module not found" error

**Solution:** Install dependencies
```bash
pip install -r requirements_commercial.txt
```

### Problem: Database error

**Solution:** Delete and recreate database
```bash
del crack_detection.db
python app_commercial.py
```

---

## 📚 Documentation

- **Complete Setup:** `FINAL_SETUP.md`
- **Full README:** `README_COMMERCIAL.md`
- **This Guide:** `QUICK_START.md`

---

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Server starts without errors
- ✅ Home page loads with smooth animations
- ✅ Cards tilt when you move your mouse
- ✅ Particles float in the background
- ✅ Google OAuth shows account picker
- ✅ GitHub OAuth redirects properly
- ✅ Can register new users
- ✅ Can login with username/password
- ✅ Dashboard shows your stats
- ✅ Can upload and predict images
- ✅ Can view prediction history
- ✅ Can compare models

---

## 🚀 You're Ready!

Your commercial crack detection platform is fully configured with:

- ✅ Beautiful UI with 3D animations
- ✅ Google OAuth (with account picker)
- ✅ GitHub OAuth
- ✅ 4 AI models
- ✅ User dashboard
- ✅ Prediction history
- ✅ Model comparison
- ✅ 3 pricing tiers
- ✅ API access
- ✅ Usage tracking

**Just configure the OAuth redirect URIs and you're good to go!**

---

## 📞 Need Help?

1. Check `FINAL_SETUP.md` for detailed instructions
2. Run `python verify_setup.py` to check configuration
3. Check console for error messages
4. Verify OAuth redirect URIs are correct

---

**Built with ❤️ for professional structural health monitoring**

🌐 **URL:** http://localhost:5000  
🔐 **OAuth:** Google + GitHub  
🎨 **Design:** Framer Motion-style  
🤖 **AI:** 4 CNN models  
📊 **Accuracy:** 97%  
⚡ **Speed:** 50ms  

**Let's detect some cracks! 🚀**
