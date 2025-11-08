# Step-by-Step Setup Guide for Medisync Python Application

## 🎯 Complete Guide - From Zero to Running

Follow these steps **in order** to run the Medisync HIPAA-Compliant EHR Transfer System.

---

## Step 1: Verify Python Installation

**Check if Python is installed:**

```bash
python --version
```

**OR** (if the above doesn't work):

```bash
python3 --version
```

**Expected Output:**
```
Python 3.7.x or higher
```

**❌ If you get "command not found":**
- Download Python from: https://www.python.org/downloads/
- Install it, then restart your terminal
- Try the command again

---

## Step 2: Navigate to the Project Folder

**Open your terminal and go to the Medisync folder:**

```bash
cd /path/to/Medisync
```

**Example paths:**
- Mac/Linux: `cd ~/Documents/Medisync`
- Windows: `cd C:\Users\YourName\Documents\Medisync`

**Verify you're in the right folder:**

```bash
ls
```

**You should see:**
```
README.md
hipaa_compliant_ehr_transfer.py
requirements.txt
ehr_transfer_web_app.html
...
```

---

## Step 3: Install Required Dependencies

**This installs the necessary Python packages (requests and cryptography):**

```bash
pip install -r requirements.txt
```

**OR** (if pip doesn't work):

```bash
pip3 install -r requirements.txt
```

**OR** (if you want to install manually):

```bash
pip install requests cryptography
```

**Expected Output:**
```
Successfully installed requests-2.31.0 cryptography-41.0.0
```

**✅ You only need to do this ONCE** (unless you delete the packages)

---

## Step 4: Run the Python Script

**Now run the main program:**

```bash
python hipaa_compliant_ehr_transfer.py
```

**OR** (if python doesn't work):

```bash
python3 hipaa_compliant_ehr_transfer.py
```

---

## 🎉 What You'll See

The program will run through 5 steps automatically:

```
======================================================================
HIPAA-COMPLIANT EHR DATA TRANSFER SYSTEM
======================================================================

✅ Dependencies loaded successfully

📋 Session ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6

🔐 Step 1/5: Authenticating with EHR systems...
   ✅ OAuth authentication successful

📝 Step 2/5: Verifying patient consent...
   ✅ Patient consent verified

📊 Step 3/5: Retrieving patient data from Epic Systems...
   ✅ Patient data retrieved successfully

🔍 Step 4/5: Applying data minimization...
   ✅ Data minimized to 4 elements

   🔒 Data integrity checksum: abc123def456...

🚀 Step 5/5: Transmitting to Cerner PowerChart...
   ✅ Transmission successful - ID: TX-ABC12345

======================================================================
TRANSFER SUMMARY
======================================================================

👤 Patient: John Doe
📅 Date of Birth: 1980-05-15
⚕️  Medical Conditions: 3
💊 Active Medications: 3
📈 Vital Signs Records: 3

🔒 Encrypted Fields: MRN, Phone, Address, ZIP
🔐 Encryption: AES-256 (Fernet)
🔗 Protocol: HTTPS/TLS 1.2+ (simulated)

======================================================================
✅ Audit trail completed and logged to ehr_audit.log
======================================================================
```

**⏱️ Total Time:** About 5-10 seconds

---

## Step 5: View the Audit Log (Optional)

**The program creates a log file with all activity:**

```bash
cat ehr_audit.log
```

**OR open it in a text editor:**

```bash
# Mac
open ehr_audit.log

# Linux
nano ehr_audit.log

# Windows
notepad ehr_audit.log
```

**You'll see detailed logs like:**
```
2025-11-08 10:30:45 - INFO - Session abc123: Initialized secure transfer
2025-11-08 10:30:46 - INFO - Session abc123: OAuth authentication successful
2025-11-08 10:30:47 - INFO - Session abc123: Patient consent verified
...
```

---

## 🔄 Running It Again

**To run the simulation again, just repeat Step 4:**

```bash
python hipaa_compliant_ehr_transfer.py
```

- Each run creates a new session with a unique ID
- Audit entries are **appended** to `ehr_audit.log` (not overwritten)
- You can run it as many times as you want

---

## 🐛 Troubleshooting

### Problem: "No module named 'requests'"

**Solution:**
```bash
pip install requests cryptography
```

---

### Problem: "python: command not found"

**Solution:** Try using `python3` instead:
```bash
python3 hipaa_compliant_ehr_transfer.py
```

---

### Problem: "Permission denied"

**Solution:** Make the file executable:
```bash
chmod +x hipaa_compliant_ehr_transfer.py
./hipaa_compliant_ehr_transfer.py
```

---

### Problem: Script runs but shows errors

**Solution:** Make sure you're in the Medisync folder:
```bash
pwd  # Shows current directory
cd /path/to/Medisync
```

---

## 📝 Quick Reference - Commands in Order

Here's the **complete sequence** from start to finish:

```bash
# 1. Check Python
python --version

# 2. Navigate to project
cd /path/to/Medisync

# 3. Install dependencies (ONE TIME ONLY)
pip install -r requirements.txt

# 4. Run the program
python hipaa_compliant_ehr_transfer.py

# 5. (Optional) View audit log
cat ehr_audit.log
```

---

## ✅ Success Checklist

After running, you should have:

- ✅ Seen all 5 steps complete successfully
- ✅ Seen the transfer summary with patient data
- ✅ Created file: `ehr_audit.log` in the same folder
- ✅ No error messages

---

## 🎓 What's Happening Behind the Scenes

When you run the script, it:

1. **Imports libraries** - Loads requests and cryptography modules
2. **Creates encryption key** - Generates a unique Fernet key for this session
3. **Simulates OAuth** - Pretends to authenticate with EHR systems
4. **Checks consent** - Verifies patient authorization (simulated)
5. **Retrieves data** - Gets mock patient data (hardcoded in the script)
6. **Encrypts PHI** - Encrypts sensitive fields (MRN, phone, address, ZIP)
7. **Generates checksum** - Creates SHA-256 hash for data integrity
8. **Simulates transmission** - Logs the transfer (doesn't actually send data)
9. **Writes audit log** - Saves all actions to `ehr_audit.log`
10. **Displays summary** - Shows results in terminal

**Important:** This is a **simulation** - no real EHR systems are contacted!

---

## 🚀 Next Steps

After running the Python script successfully:

1. ✅ **Open the web app** - Try `ehr_transfer_web_app.html` in your browser
2. ✅ **Read the code** - Open `hipaa_compliant_ehr_transfer.py` in a text editor
3. ✅ **Modify the data** - Try changing patient information in the script
4. ✅ **Review audit logs** - Check `ehr_audit.log` after multiple runs

---

## 💡 Tips

- **Run multiple times** - Each run creates a new session ID
- **Check timestamps** - Audit log shows exact timing of each action
- **Watch for encryption** - Notice which fields show "***ENCRYPTED***"
- **Read the summary** - Shows how many conditions, medications, etc.

---

## 📞 Still Having Issues?

Make sure:
1. Python 3.7+ is installed
2. You're in the correct directory (`/path/to/Medisync`)
3. Dependencies are installed (`pip install -r requirements.txt`)
4. The file `hipaa_compliant_ehr_transfer.py` exists in the folder

---

**You're all set! Enjoy exploring HIPAA-compliant EHR data transfer! 🏥**
