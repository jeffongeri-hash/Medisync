# Complete Setup Guide - HIPAA-Compliant EHR Transfer System

This guide will walk you through **every step** needed to get the system running on your computer, from installation to your first successful transfer.

---

## Table of Contents
1. [Prerequisites & Installation](#step-1-prerequisites--installation)
2. [Download the Code](#step-2-download-the-code)
3. [Register for Epic Sandbox](#step-3-register-for-epic-sandbox)
4. [Register for Cerner Sandbox](#step-4-register-for-cerner-sandbox)
5. [Configure Your Credentials](#step-5-configure-your-credentials)
6. [Run Your First Transfer](#step-6-run-your-first-transfer)
7. [Understanding the Results](#step-7-understanding-the-results)
8. [Troubleshooting](#troubleshooting)

---

## Step 1: Prerequisites & Installation

### 1.1 Check if Python is Installed

Open your terminal/command prompt and run:
```bash
python --version
```

**Expected output:** `Python 3.8.x` or higher (3.9, 3.10, 3.11, etc.)

**If Python is NOT installed:**

**Windows:**
1. Go to https://www.python.org/downloads/
2. Download the latest Python 3.11 installer
3. **IMPORTANT:** Check the box "Add Python to PATH" during installation
4. Click "Install Now"
5. Restart your terminal and verify: `python --version`

**Mac:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 1.2 Verify pip is Installed

```bash
pip --version
```

**If pip is not found:**
```bash
python -m ensurepip --upgrade
```

### 1.3 Install Git (for cloning the repository)

**Check if Git is installed:**
```bash
git --version
```

**If Git is NOT installed:**
- **Windows:** Download from https://git-scm.com/download/win
- **Mac:** `brew install git`
- **Linux:** `sudo apt install git`

---

## Step 2: Download the Code

### Option A: Clone with Git (Recommended)

1. **Open terminal/command prompt**

2. **Navigate to where you want the code:**
   ```bash
   # Example: Create a projects folder
   mkdir ~/projects
   cd ~/projects
   ```

3. **Clone the repository:**
   ```bash
   git clone https://github.com/jeffongeri-hash/Medisync.git
   cd Medisync
   ```

4. **Switch to the correct branch:**
   ```bash
   git checkout claude/hipaa-ehr-transfer-system-011CUkKjNn5EEtFWJoyuDMix
   ```

5. **Verify you have the files:**
   ```bash
   ls
   # You should see: backend/, logs/, transfer_epic_to_cerner.py, requirements.txt, README.md
   ```

### Option B: Download ZIP (Alternative)

1. Go to: https://github.com/jeffongeri-hash/Medisync
2. Click the **"Code"** button (green button)
3. Select **"Download ZIP"**
4. Extract the ZIP to a folder (e.g., `C:\Users\YourName\Projects\Medisync`)
5. Open terminal/command prompt in that folder

---

## Step 3: Register for Epic Sandbox

Epic provides a **free sandbox** for testing with realistic patient data.

### 3.1 Create Epic Account

1. **Visit:** https://fhir.epic.com/
2. Click **"Get Started"** or **"Build Apps"**
3. Click **"Register"** (top right)
4. Fill out the registration form:
   - Email address
   - Name
   - Organization (can be "Personal" or "Testing")
   - Click **"Create Account"**
5. **Verify your email** (check spam folder if needed)

### 3.2 Create a Backend Systems App

1. **Log in** to https://fhir.epic.com/
2. Click **"Build Apps"** → **"Create"**
3. Select application type: **"Backend Systems"**
4. Fill out the form:
   - **App Name:** `Medisync EHR Transfer Test`
   - **Application Audience:** Non-Production
   - **FHIR Version:** R4
   - **Incoming APIs:** Select these scopes:
     - `system/Patient.read`
     - `system/Observation.read`
     - `system/Condition.read`
     - `system/MedicationRequest.read`
     - `system/AllergyIntolerance.read`
5. Click **"Save"** or **"Create App"**

### 3.3 Get Your Epic Credentials

After creating the app, you'll see:
- **Client ID** (looks like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
- **Client Secret** (for sandbox testing only)

**IMPORTANT:** Copy both of these and save them somewhere safe!

**Example:**
```
EPIC_CLIENT_ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
EPIC_CLIENT_SECRET: Xy9Pq2Rm5Tn8Wp3Lk6Jh4Fg7Ds1Az0Bn
```

### 3.4 Test Patient IDs in Epic Sandbox

Epic provides test patients. You'll use these IDs:

| Patient Name | Patient ID |
|--------------|------------|
| Derrick Lin | `Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB` |
| Camila Lopez | `eq081-VQEgP8drUUqCWzHfw3` |

More test patients: https://fhir.epic.com/Documentation?docId=testpatients

---

## Step 4: Register for Cerner Sandbox

Cerner (now Oracle Health) provides a **free sandbox** for testing.

### 4.1 Create Cerner Account

1. **Visit:** https://fhir.cerner.com/
2. Click **"Developer Portal"** or **"Get Started"**
3. Click **"Sign Up"** or **"Register"**
4. Fill out the registration form:
   - Email address
   - Name
   - Organization
   - Accept terms and conditions
5. **Verify your email**

### 4.2 Create a System Account

1. **Log in** to https://fhir.cerner.com/
2. Navigate to **"My Apps"** or **"Applications"**
3. Click **"Create New App"** or **"Register"**
4. Select: **"System Account"** (for backend services)
5. Fill out the form:
   - **App Name:** `Medisync EHR Transfer Test`
   - **App Type:** System Account
   - **SMART Scopes:** Select:
     - `system/Patient.write`
     - `system/Observation.write`
     - `system/Condition.write`
     - `system/MedicationRequest.write`
     - `system/AllergyIntolerance.write`
6. Click **"Create"** or **"Register"**

### 4.3 Get Your Cerner Credentials

After creating the app, you'll receive:
- **Client ID** (looks like: `xyz123-abc456-def789`)
- **Client Secret**

**IMPORTANT:** Copy both and save them!

**Example:**
```
CERNER_CLIENT_ID: xyz123-abc456-def789
CERNER_CLIENT_SECRET: Zx8Mq4Nk2Jp6Rl9Ht5Gv3Fc1Bw7Dn0Cs
```

---

## Step 5: Configure Your Credentials

Now that you have credentials from both Epic and Cerner, let's configure the system.

### 5.1 Create Virtual Environment

In your `Medisync` folder:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows Command Prompt:
venv\Scripts\activate

# On Windows PowerShell:
venv\Scripts\Activate.ps1
```

**You should see `(venv)` at the start of your command prompt**

### 5.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:** Installation of packages like `cryptography`, `flask`, `requests`, etc.

**If you get errors:**
```bash
# Try upgrading pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 Create Logs Directory

```bash
mkdir logs
```

### 5.4 Configure Credentials (Choose ONE method)

#### Method A: Environment Variables (Most Secure)

**Mac/Linux:**
```bash
export EPIC_CLIENT_ID='your_epic_client_id_here'
export EPIC_CLIENT_SECRET='your_epic_client_secret_here'
export CERNER_CLIENT_ID='your_cerner_client_id_here'
export CERNER_CLIENT_SECRET='your_cerner_client_secret_here'
```

**Windows Command Prompt:**
```cmd
set EPIC_CLIENT_ID=your_epic_client_id_here
set EPIC_CLIENT_SECRET=your_epic_client_secret_here
set CERNER_CLIENT_ID=your_cerner_client_id_here
set CERNER_CLIENT_SECRET=your_cerner_client_secret_here
```

**Windows PowerShell:**
```powershell
$env:EPIC_CLIENT_ID='your_epic_client_id_here'
$env:EPIC_CLIENT_SECRET='your_epic_client_secret_here'
$env:CERNER_CLIENT_ID='your_cerner_client_id_here'
$env:CERNER_CLIENT_SECRET='your_cerner_client_secret_here'
```

#### Method B: Edit the Script Directly (Easier for beginners)

1. **Open `transfer_epic_to_cerner.py` in a text editor**

2. **Find lines 24-27** (near the top):
   ```python
   EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID", "YOUR_EPIC_CLIENT_ID")
   EPIC_CLIENT_SECRET = os.getenv("EPIC_CLIENT_SECRET", "YOUR_EPIC_CLIENT_SECRET")
   CERNER_CLIENT_ID = os.getenv("CERNER_CLIENT_ID", "YOUR_CERNER_CLIENT_ID")
   CERNER_CLIENT_SECRET = os.getenv("CERNER_CLIENT_SECRET", "YOUR_CERNER_CLIENT_SECRET")
   ```

3. **Replace with your actual credentials:**
   ```python
   EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID", "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
   EPIC_CLIENT_SECRET = os.getenv("EPIC_CLIENT_SECRET", "Xy9Pq2Rm5Tn8Wp3Lk6Jh4Fg7Ds1Az0Bn")
   CERNER_CLIENT_ID = os.getenv("CERNER_CLIENT_ID", "xyz123-abc456-def789")
   CERNER_CLIENT_SECRET = os.getenv("CERNER_CLIENT_SECRET", "Zx8Mq4Nk2Jp6Rl9Ht5Gv3Fc1Bw7Dn0Cs")
   ```

4. **Save the file**

---

## Step 6: Run Your First Transfer

### 6.1 Run the Transfer Script

Make sure you're in the `Medisync` folder with your virtual environment activated `(venv)`:

```bash
python transfer_epic_to_cerner.py
```

### 6.2 Follow the Interactive Prompts

You'll see:

```
================================================================================
EPIC TO CERNER EHR TRANSFER
Medisync - HIPAA-Compliant Healthcare Data Transfer System
================================================================================

Available Test Patients (Epic Sandbox):
--------------------------------------------------------------------------------
1. Derrick Lin
   ID: Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB

2. Camila Lopez
   ID: eq081-VQEgP8drUUqCWzHfw3

3. Enter custom patient ID
--------------------------------------------------------------------------------

Select patient (1-3):
```

**Type `1` and press Enter** (to select Derrick Lin)

### 6.3 Select Data Elements

```
Data Elements to Transfer:
--------------------------------------------------------------------------------
1. All data (patient, conditions, medications, allergies, observations)
2. Patient demographics only
3. Patient + Conditions + Medications
4. Custom selection
--------------------------------------------------------------------------------

Select option (1-4) [default: 1]:
```

**Press Enter** (to select option 1 - all data)

### 6.4 Confirm Transfer

```
--------------------------------------------------------------------------------
TRANSFER CONFIRMATION
--------------------------------------------------------------------------------
Patient: Derrick Lin
Epic ID: Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
Data to transfer: patient, conditions, medications, allergies, observations
--------------------------------------------------------------------------------

Proceed with transfer? (y/n):
```

**Type `y` and press Enter**

### 6.5 Watch the Transfer Progress

You'll see detailed progress:

```
================================================================================
INITIATING TRANSFER
================================================================================

Patient: Derrick Lin
Epic Patient ID: Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
Data Elements: patient, conditions, medications, allergies, observations
Transfer Time: 2025-01-04 14:30:45

--------------------------------------------------------------------------------

Step 1: Initializing transfer handler...
✓ Transfer handler initialized

Step 2: Authenticating with Epic and Cerner...
✓ Epic authentication successful
✓ Cerner authentication successful

Step 3: Transferring patient data...

Step 1: Fetching data from Epic
  - Fetching patient demographics
  - Fetching conditions
  - Fetching medications
  - Fetching allergies
  - Fetching observations (labs and vitals)
✓ Fetched Epic data:
    - Patient: Yes
    - Conditions: 15
    - Medications: 10
    - Allergies: 5
    - Observations: 42

Step 2: Transforming data for Cerner
✓ Data transformation complete

Step 3: Encrypting sensitive data
✓ Data encrypted successfully (2048 bytes)

Step 4: Generating integrity checksum
✓ Data integrity checksum: abc123def456...

Step 5: Preparing for secure transmission
✓ Data decrypted successfully

Step 6: Sending data to Cerner
✓ Data successfully sent to Cerner

Step 7: Creating audit log
✓ Audit log saved to logs/transfer_xyz789.json
```

---

## Step 7: Understanding the Results

### 7.1 Success Message

```
================================================================================
TRANSFER COMPLETED SUCCESSFULLY
================================================================================

✓ Transfer ID: abc123-def456-789xyz
✓ Status: SUCCESS

📊 Transfer Summary:
   Source: Epic (Patient ID: Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB)
   Destination: Cerner (Patient ID: 12345678)

📝 Resources Created in Cerner:
   • Conditions: 15
   • Medications: 10
   • Allergies: 5
   • Observations: 42

🔒 Security:
   • Encryption: AES-128 (Fernet)
   • Integrity: SHA-256 checksum
   • Checksum: abc123def456789x...

📄 Audit Log:
   • Transfer logged for HIPAA compliance
   • Log file: logs/transfer_abc123-def456-789xyz.json

================================================================================
```

### 7.2 Check the Logs

View detailed logs in the `logs/` directory:

```bash
# List all log files
ls logs/

# View the latest transfer log
cat logs/transfer_epic_to_cerner_*.json

# View the audit log
cat logs/epic_to_cerner_transfer.log
```

### 7.3 What Was Transferred?

The system transferred:
- ✅ Patient demographics (name, gender, birth date)
- ✅ 15 medical conditions/diagnoses
- ✅ 10 medications
- ✅ 5 allergies
- ✅ 42 observations (lab results + vital signs)

All with HIPAA-compliant security:
- OAuth 2.0 authentication
- AES-128 encryption
- SHA-256 integrity validation
- Complete audit trail

---

## Troubleshooting

### Problem 1: "Python not found"

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
- Reinstall Python and check "Add Python to PATH"
- Or use `python3` instead of `python`
- Restart your terminal

### Problem 2: "pip not found"

**Error:**
```
'pip' is not recognized
```

**Solution:**
```bash
python -m ensurepip --upgrade
python -m pip --version
```

### Problem 3: "Module not found"

**Error:**
```
ModuleNotFoundError: No module named 'cryptography'
```

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem 4: "Authentication failed: 401 Unauthorized"

**Error:**
```
Authentication failed: 401 Unauthorized
```

**Solution:**
- Double-check your Epic/Cerner credentials
- Make sure you copied the full Client ID and Client Secret
- Verify your app is registered correctly in the sandbox
- Check that you're using **sandbox** credentials (not production)

### Problem 5: "Credentials not configured"

**Error:**
```
⚠️  CREDENTIALS NOT CONFIGURED
```

**Solution:**
- Follow Step 5.4 again to set up credentials
- Make sure you replaced `YOUR_EPIC_CLIENT_ID` with actual values
- Or set environment variables correctly

### Problem 6: "Connection timeout"

**Error:**
```
Connection timeout
```

**Solution:**
- Check your internet connection
- Verify firewall isn't blocking Python
- Try again in a few minutes (API might be down temporarily)

### Problem 7: "Permission denied" on logs directory

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'logs'
```

**Solution:**
```bash
# Create logs directory manually
mkdir logs

# Or with sudo on Mac/Linux
sudo mkdir logs
sudo chmod 777 logs
```

### Problem 8: Virtual environment not activating

**Windows PowerShell Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
venv\Scripts\Activate.ps1
```

---

## Common Questions

### Q1: Do I need to pay for Epic or Cerner access?

**No!** Both Epic and Cerner provide **free sandbox environments** for testing and development.

### Q2: Can I use real patient data?

**No!** This is a sandbox system for testing only. Use only the test patient IDs provided by Epic. Never use real patient data without proper legal authorization and production credentials.

### Q3: Is this production-ready?

**No.** This is for demonstration and testing. For production use, you need:
- Production credentials from Epic and Cerner
- Business Associate Agreements (BAA)
- Security audits
- Proper HIPAA compliance procedures
- Encrypted storage
- Access controls

### Q4: How long does a transfer take?

Typically **10-30 seconds** depending on:
- Amount of data (number of conditions, medications, observations)
- Network speed
- API response times

### Q5: Can I transfer multiple patients at once?

The current script transfers one patient at a time. For bulk transfers, you'd need to modify the code or run the script multiple times.

### Q6: What if I don't have a GitHub account?

You don't need a GitHub account to download the code. Use the "Download ZIP" option mentioned in Step 2, Option B.

---

## Next Steps

### Run Additional Transfers

```bash
# Transfer another patient
python transfer_epic_to_cerner.py

# Select patient 2 (Camila Lopez) this time
```

### Test Individual Components

```bash
# Test Epic FHIR client only
cd backend
python epic_fhir_client.py

# Test Cerner FHIR client only
python cerner_fhir_client.py

# Test HIPAA compliance features
python hipaa_compliant_ehr_transfer.py
```

### Explore the Code

- `backend/epic_fhir_client.py` - Epic data retrieval
- `backend/cerner_fhir_client.py` - Cerner data writing
- `backend/epic_to_cerner_transfer.py` - Complete integration
- `backend/hipaa_compliant_ehr_transfer.py` - Security & compliance

### View Logs

```bash
# View all transfers
ls -la logs/

# View audit log
cat logs/epic_to_cerner_transfer.log

# View specific transfer details
cat logs/transfer_epic_to_cerner_<id>.json | python -m json.tool
```

---

## Getting Help

If you're still having issues:

1. **Check the log files** in `logs/` directory
2. **Review error messages** carefully
3. **Verify credentials** are correct
4. **Search Epic documentation**: https://fhir.epic.com/Documentation
5. **Search Cerner documentation**: https://fhir.cerner.com/

---

## Summary Checklist

Before running, make sure:

- [ ] Python 3.8+ installed
- [ ] pip installed
- [ ] Git installed (or ZIP downloaded)
- [ ] Code downloaded to your computer
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] logs directory created
- [ ] Epic account registered
- [ ] Epic app created (Backend Systems)
- [ ] Epic credentials saved
- [ ] Cerner account registered
- [ ] Cerner system account created
- [ ] Cerner credentials saved
- [ ] Credentials configured in code or environment variables
- [ ] Internet connection active

✅ **Ready to transfer!** Run: `python transfer_epic_to_cerner.py`

---

**⚠️ Security Reminder:** This system handles Protected Health Information (PHI). Always:
- Keep credentials secure (never share or commit to Git)
- Use sandbox/test data only
- Follow HIPAA compliance guidelines
- Never use production credentials without proper authorization

---

**Need more help?** Let me know which step you're stuck on!
