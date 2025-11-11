# Epic OAuth Setup Guide

## 🔑 Getting Your Epic Client Secret

You have Epic Client IDs but need the **Client Secret** to authenticate. Here's how to get it:

---

## Step 1: Go to Epic's Developer Portal

Visit: **https://fhir.epic.com/Developer/Apps**

---

## Step 2: Sign In

- Log in with your Epic account
- If you don't have an account, you may need to create one or contact your Epic representative

---

## Step 3: Find Your Registered App

You should see your application listed. It will show:
- **App Name**: (Whatever you named it)
- **Client ID**: `975449d0-070d-439e-ac6a-168a89ea59ed` or `41767c4f-8948-402b-97e8-2c6010899539`

---

## Step 4: View Credentials

- Click on your app name or "View Details"
- Look for **"Manage Keys"**, **"View Credentials"**, or **"Client Secret"**
- Click to reveal your **Client Secret**

The client secret will look like:
- Another UUID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- Or a longer string: `abc123xyz456def789ghi012jkl345mno678`

---

## Step 5: Add Secret to Code

Open `transfer_epic_to_cerner.py` and find **Line 25**:

```python
EPIC_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"  # ← REPLACE THIS
```

Replace with your actual secret:

```python
EPIC_CLIENT_SECRET = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"  # ← Your real secret
```

**IMPORTANT**: Keep this secret secure! Don't share it publicly or commit it to GitHub.

---

## Line 36 Explanation (What You Asked About)

**Line 36** is actually around where the OAuth authentication happens. Here's what it looks like:

```python
# Lines 35-41 in the authenticate() method:
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': self.client_id,           # ← Your Client ID
    'client_secret': self.client_secret,   # ← Your Client Secret (from line 25)
}
```

This creates the OAuth 2.0 request that Epic needs to give you an access token.

---

## Complete Configuration Example

Here's what your configuration should look like when complete:

```python
# Your Epic Client IDs (already filled in)
EPIC_CLIENT_ID_1 = "975449d0-070d-439e-ac6a-168a89ea59ed"
EPIC_CLIENT_ID_2 = "41767c4f-8948-402b-97e8-2c6010899539"  # Non-Production

# Add your client secret here (Line 25)
EPIC_CLIENT_SECRET = "abc123-your-actual-secret-here-xyz789"  # ← REPLACE THIS
```

---

## Testing After Configuration

Once you add your client secret:

```bash
# Run the transfer script
python transfer_epic_to_cerner.py
```

You should see:
```
🔐 Authenticating with Epic OAuth 2.0...
✅ Authentication successful!
   Access Token: eyJhbGciOiJSUzI1NiI...
```

---

## If You Don't Have a Client Secret

### Option 1: Register a New App

1. Go to: https://fhir.epic.com/Developer/Apps
2. Click **"Create New App"** or **"Register Application"**
3. Fill in the application details:
   - **App Name**: "Medisync Transfer Tool"
   - **App Type**: "Backend Service" or "Confidential Client"
   - **FHIR Version**: R4
   - **Scopes**: Select what data you need
     - `system/Patient.read`
     - `system/Observation.read`
     - `system/MedicationRequest.read`
     - `system/Condition.read`
4. Submit and wait for approval
5. Once approved, you'll get both Client ID and Client Secret

### Option 2: Use Public Sandbox (No Auth)

If you can't get a client secret, use the **public sandbox** instead:

```bash
# This script works without authentication
python epic_fhir_client.py
```

This uses Epic's open endpoints that don't require OAuth.

---

## Security Best Practices

### ⚠️ DO NOT:
- Commit your client secret to GitHub
- Share your client secret publicly
- Hard-code secrets in production code

### ✅ DO:
- Store secrets in environment variables
- Use a secrets manager (like AWS Secrets Manager, Azure Key Vault)
- Add `.env` to `.gitignore`
- Rotate secrets regularly

### Using Environment Variables (Recommended)

Instead of hard-coding, use environment variables:

```python
import os

EPIC_CLIENT_SECRET = os.getenv('EPIC_CLIENT_SECRET', 'YOUR_CLIENT_SECRET_HERE')
```

Then set the environment variable:

```bash
# On Mac/Linux
export EPIC_CLIENT_SECRET="your-secret-here"
python transfer_epic_to_cerner.py

# On Windows
set EPIC_CLIENT_SECRET=your-secret-here
python transfer_epic_to_cerner.py
```

Or use a `.env` file:

```bash
# Create .env file
echo "EPIC_CLIENT_SECRET=your-secret-here" > .env

# Install python-dotenv
pip install python-dotenv

# Load in your script
from dotenv import load_dotenv
load_dotenv()
```

---

## Troubleshooting

### Error: "Invalid client credentials"

**Problem**: Client ID or secret is incorrect

**Solution**:
1. Double-check you copied the correct secret
2. Make sure there are no extra spaces
3. Verify you're using the right client ID
4. Check if your app is still active in Epic's portal

---

### Error: "Insufficient scopes"

**Problem**: Your app doesn't have permission to access requested data

**Solution**:
1. Go back to Epic Developer Portal
2. Edit your app
3. Add required scopes:
   - `system/Patient.read`
   - `system/Observation.read`
   - `system/MedicationRequest.read`
   - `system/Condition.read`
4. Save and retry

---

### Error: "Token expired"

**Problem**: Access token expired (usually after 1 hour)

**Solution**: The script automatically gets a new token, but if needed:
```python
epic_client.authenticate()  # Get new token
```

---

## OAuth 2.0 Flow Diagram

```
Your Script                 Epic OAuth Server              Epic FHIR API
    |                              |                              |
    |  1. POST /oauth2/token       |                              |
    |  (client_id + secret)        |                              |
    |----------------------------->|                              |
    |                              |                              |
    |  2. Return access_token      |                              |
    |<-----------------------------|                              |
    |                              |                              |
    |  3. GET /Patient/123                                        |
    |  (Authorization: Bearer <token>)                            |
    |---------------------------------------------------------------->|
    |                              |                              |
    |  4. Return patient data      |                              |
    |<----------------------------------------------------------------|
```

---

## What Happens After Authentication

Once authenticated, your script can:

1. **Retrieve patient data** from Epic
   - Demographics (name, DOB, gender)
   - Vital signs (BP, weight, temperature)
   - Medications (prescriptions, dosages)
   - Conditions (diagnoses, problems)

2. **Transfer to Cerner** (currently simulated)
   - The script shows what data would be transferred
   - Real Cerner integration requires Cerner credentials

---

## Next Steps

1. ✅ Get your Epic client secret
2. ✅ Add it to line 25 of `transfer_epic_to_cerner.py`
3. ✅ Run the script: `python transfer_epic_to_cerner.py`
4. ✅ Select a test patient
5. ✅ Watch the data transfer

For Cerner integration:
- Register at Cerner's developer portal
- Get Cerner client credentials
- Update the `CernerClient` class with real API calls

---

## Resources

- **Epic FHIR Documentation**: https://fhir.epic.com/
- **Epic App Orchard**: https://apporchard.epic.com/
- **OAuth 2.0 Spec**: https://oauth.net/2/
- **Epic Developer Portal**: https://fhir.epic.com/Developer/Apps

---

**Need help? Check the error messages in the script - they provide detailed guidance!**
