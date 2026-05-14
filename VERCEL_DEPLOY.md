# 🚀 Deploy to Vercel - Complete Guide

## ⚡ Quick Deploy (3 Steps)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy
```bash
vercel --prod
```

That's it! Your site will be live! 🎉

---

## 📋 Detailed Instructions

### Option 1: Using Vercel CLI (Recommended)

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Login to Vercel
```bash
vercel login
```
- Choose your login method (GitHub, GitLab, Bitbucket, or Email)
- Follow the authentication steps

#### 3. Deploy to Vercel
```bash
# Navigate to your project directory
cd C:\Users\trina\Downloads\archive

# Deploy (first time - creates project)
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? No
# - Project name? concrete-crack-detection
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

#### 4. Your Site is Live!
```
✅ Production: https://concrete-crack-detection.vercel.app
```

---

### Option 2: Using Vercel Dashboard (No CLI)

#### 1. Push to GitHub First
```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Deploy to Vercel"

# Push to GitHub
git remote add origin https://github.com/saugata-malakar/concrete-crack-detection.git
git branch -M main
git push -u origin main
```

#### 2. Import to Vercel
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repository
4. Click "Import"
5. Configure:
   - **Framework Preset:** Other
   - **Build Command:** (leave empty)
   - **Output Directory:** (leave empty)
   - **Install Command:** `pip install -r requirements_vercel.txt`
6. Click "Deploy"

#### 3. Wait for Deployment
- Vercel will build and deploy automatically
- Takes 2-5 minutes
- You'll get a live URL!

---

## ⚙️ Configuration Files Created

✅ `vercel.json` - Vercel configuration
✅ `requirements_vercel.txt` - Python dependencies
✅ `api/index.py` - Serverless function entry
✅ `.vercelignore` - Files to ignore

---

## 🎯 What Gets Deployed

**Included:**
- ✅ Flask application (`app_full.py`)
- ✅ HTML templates
- ✅ Python scripts
- ✅ Documentation

**Excluded (too large):**
- ❌ Dataset images (Decks, Pavements, Walls)
- ❌ Model checkpoints (.pth files)
- ❌ Generated visualizations

**Note:** The deployed version will use pretrained models instead of your trained checkpoints.

---

## 🔧 Environment Variables (Optional)

If you need to set environment variables:

```bash
# Using CLI
vercel env add FLASK_ENV production

# Or in Vercel Dashboard:
# Settings → Environment Variables
```

---

## 📱 Custom Domain (Optional)

### Add Custom Domain:
1. Go to your project on Vercel
2. Settings → Domains
3. Add your domain
4. Follow DNS configuration steps

---

## 🐛 Troubleshooting

### Issue: "Build Failed"
**Solution:** Check `requirements_vercel.txt` has correct versions

### Issue: "Function Too Large"
**Solution:** Models are too big for serverless. Use pretrained models only.

### Issue: "Import Error"
**Solution:** Make sure all imports are in `requirements_vercel.txt`

### Issue: "Timeout"
**Solution:** Vercel has 10s timeout for free tier. Optimize model loading.

---

## 💡 Alternative: Deploy Static Site Only

If serverless doesn't work (models too large), deploy static HTML:

### 1. Create `index.html` in root
```bash
# Copy the static website
cp index.html ./
```

### 2. Deploy as Static Site
```bash
vercel --prod
```

### 3. Your static site is live!
```
https://concrete-crack-detection.vercel.app
```

---

## 🎉 Success!

After deployment, you'll get:

```
✅ Production URL: https://concrete-crack-detection.vercel.app
✅ Preview URL: https://concrete-crack-detection-xxx.vercel.app
✅ Automatic HTTPS
✅ Global CDN
✅ Auto-scaling
```

---

## 📊 Vercel Features

- ✅ **Free Tier:** 100GB bandwidth/month
- ✅ **Automatic HTTPS**
- ✅ **Global CDN**
- ✅ **Instant Rollbacks**
- ✅ **Preview Deployments**
- ✅ **Analytics**

---

## 🔗 Useful Commands

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove deployment
vercel rm concrete-crack-detection
```

---

## 📞 Support

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Support:** https://vercel.com/support
- **Community:** https://github.com/vercel/vercel/discussions

---

## ⚡ QUICK START (Copy-Paste)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd C:\Users\trina\Downloads\archive
vercel --prod
```

**Done! Your site is live!** 🚀

---

## 🎯 Expected Result

```
🔍  Inspect: https://vercel.com/your-username/concrete-crack-detection
✅  Production: https://concrete-crack-detection.vercel.app [2s]
```

Your website will be live at:
```
https://concrete-crack-detection.vercel.app
```

or

```
https://concrete-crack-detection-saugata-malakar.vercel.app
```

---

**Ready to deploy? Run:** `vercel --prod` 🚀
