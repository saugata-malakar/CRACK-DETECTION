# 🔐 GitHub OAuth Setup Guide

## Quick Setup (3 Minutes)

### Step 1: Go to GitHub Settings

1. Go to: https://github.com/settings/developers
2. Click **"OAuth Apps"** in the left sidebar
3. Click **"New OAuth App"** button

### Step 2: Fill in Application Details

- **Application name**: CrackDetect AI
- **Homepage URL**: `http://localhost:5000`
- **Application description**: AI-powered crack detection platform
- **Authorization callback URL**: `http://localhost:5000/auth/github/callback`

Click **"Register application"**

### Step 3: Get Your Credentials

You'll see:
- **Client ID**: Something like `Iv1.abc123xyz789`
- Click **"Generate a new client secret"**
- **Client Secret**: Something like `abc123xyz789...` (copy immediately!)

### Step 4: Configure Your App

Edit `app_commercial.py` and find these lines (around line 90):

```python
github_client_id = os.environ.get('GITHUB_CLIENT_ID', 'your-github-client-id')
github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET', 'your-github-client-secret')
```

Replace with your actual credentials:

```python
github_client_id = os.environ.get('GITHUB_CLIENT_ID', 'YOUR-ACTUAL-CLIENT-ID')
github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET', 'YOUR-ACTUAL-CLIENT-SECRET')
```

### Step 5: Test It

1. Run: `python app_commercial.py`
2. Go to: http://localhost:5000/login
3. Click **"GitHub"** button
4. Authorize the app
5. You'll be logged in!

## ✅ Done!

GitHub OAuth is now working! Users can login with their GitHub account.
