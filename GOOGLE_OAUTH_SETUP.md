# 🔐 Google OAuth Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "CrackDetect AI" → Click "Create"

### Step 2: Enable Google+ API

1. In the left menu, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: **CrackDetect AI**
   - User support email: **Your email**
   - Developer contact: **Your email**
   - Click "Save and Continue" through all steps

4. Back to "Create OAuth client ID":
   - Application type: **Web application**
   - Name: **CrackDetect AI Web Client**
   
5. Add Authorized redirect URIs:
   ```
   http://localhost:5000/auth/google/callback
   ```
   
6. Add Authorized JavaScript origins:
   ```
   http://localhost:5000
   ```

7. Click "Create"

### Step 4: Get Your Credentials

You'll see a popup with:
- **Client ID**: Something like `1234567890-abc...xyz.apps.googleusercontent.com`
- **Client Secret**: Something like `GOCSPX-abc...xyz`

**Copy both!**

### Step 5: Configure Your App

#### Option A: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

#### Option B: Direct in Code

Edit `app_commercial.py` line ~30:

```python
GOOGLE_CLIENT_ID = 'your-client-id-here'
GOOGLE_CLIENT_SECRET = 'your-client-secret-here'
```

### Step 6: Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### Step 7: Run the App

```bash
python app_commercial.py
```

### Step 8: Test Google Login

1. Go to http://localhost:5000/login
2. Click "Continue with Google"
3. Select your Google account
4. Grant permissions
5. You'll be automatically logged in!

## 🎉 How It Works

### User Flow

1. **Click "Continue with Google"**
   - Redirects to Google account picker
   - Shows all your Google accounts

2. **Select Account**
   - Google shows permission screen
   - Asks for email and profile access

3. **Grant Permission**
   - Google redirects back to your app
   - App receives user email and name

4. **Automatic Login**
   - If email exists: Log in automatically
   - If new user: Create account and log in
   - Redirect to dashboard

### What Gets Stored

- **Email**: From Google account
- **Username**: Generated from name (e.g., "John Doe" → "john_doe")
- **Profile**: Basic info
- **No Password**: OAuth users don't need passwords

## 🔒 Security Features

✅ **State Parameter**: Prevents CSRF attacks  
✅ **Token Verification**: Validates Google tokens  
✅ **Secure Sessions**: Flask session management  
✅ **HTTPS Ready**: Works with SSL in production  
✅ **Scope Limitation**: Only requests email and profile  

## 🚀 Production Deployment

### For Production (Vercel, Heroku, etc.)

1. **Update Redirect URI** in Google Console:
   ```
   https://yourdomain.com/auth/google/callback
   ```

2. **Update JavaScript Origins**:
   ```
   https://yourdomain.com
   ```

3. **Set Environment Variables** on your hosting platform:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

4. **Remove this line** from `app_commercial.py`:
   ```python
   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Delete this
   ```

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"

**Fix**: Make sure redirect URI in Google Console exactly matches:
```
http://localhost:5000/auth/google/callback
```

### Error: "invalid_client"

**Fix**: Check your Client ID and Secret are correct

### Error: "access_denied"

**Fix**: User cancelled login. This is normal.

### Google Account Picker Not Showing

**Fix**: The code includes `prompt='select_account'` which forces account picker

### Can't See My Email

**Fix**: Make sure you enabled Google+ API in Step 2

## 📝 Testing

### Test with Multiple Accounts

1. Click "Continue with Google"
2. Google will show account picker
3. Select different account each time
4. Each creates separate user in database

### Test Existing User

1. Login with Google once
2. Logout
3. Login with Google again
4. Should recognize you and log in instantly

## 🎯 Features

✅ **Account Picker**: Shows all your Google accounts  
✅ **Auto-Registration**: Creates account if new  
✅ **Auto-Login**: Logs in if account exists  
✅ **Email Extraction**: Gets email automatically  
✅ **Name Extraction**: Gets name from Google  
✅ **Unique Usernames**: Handles duplicates  
✅ **No Password Needed**: OAuth handles authentication  

## 💡 Tips

1. **Test in Incognito**: To test with different accounts
2. **Clear Sessions**: Logout to test fresh login
3. **Check Database**: See users in `crack_detection.db`
4. **Monitor Console**: Check for error messages

## 🔗 Useful Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Python OAuth Library](https://google-auth.readthedocs.io/)

## ✅ Verification Checklist

- [ ] Google Cloud project created
- [ ] Google+ API enabled
- [ ] OAuth credentials created
- [ ] Redirect URI configured
- [ ] Client ID and Secret copied
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] App running on localhost:5000
- [ ] Google login button works
- [ ] Account picker appears
- [ ] Login successful
- [ ] Dashboard accessible

## 🎉 Success!

Once setup, users can:
- Click "Continue with Google"
- See their Google accounts
- Select account
- Get logged in automatically
- No password needed!

**Your Google OAuth is now working! 🚀**
