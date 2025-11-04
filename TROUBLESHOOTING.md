# Troubleshooting Guide

Common issues and solutions for the HIPAA-Compliant EHR Transfer System.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication Issues](#authentication-issues)
3. [Transfer Issues](#transfer-issues)
4. [Network Issues](#network-issues)
5. [Permission Issues](#permission-issues)
6. [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Issue 1: "Python not found" or "python: command not found"

**Symptoms:**
```
'python' is not recognized as an internal or external command
python: command not found
```

**Causes:**
- Python is not installed
- Python is not in system PATH
- Using wrong Python command

**Solutions:**

1. **Check if Python 3 is installed:**
   ```bash
   python3 --version
   # or
   py --version  # Windows
   ```

2. **Install Python:**
   - **Windows:** https://www.python.org/downloads/ (check "Add Python to PATH")
   - **Mac:** `brew install python@3.11`
   - **Linux:** `sudo apt install python3.11 python3-pip`

3. **Use correct command:**
   - Try `python3` instead of `python`
   - Try `py` on Windows

4. **Restart terminal** after installation

---

### Issue 2: "pip not found" or "No module named pip"

**Symptoms:**
```
'pip' is not recognized
pip: command not found
No module named pip
```

**Solutions:**

1. **Install pip:**
   ```bash
   python -m ensurepip --upgrade
   # or
   python3 -m ensurepip --upgrade
   ```

2. **Use python -m pip:**
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Install pip manually (Linux):**
   ```bash
   sudo apt install python3-pip
   ```

---

### Issue 3: "ModuleNotFoundError: No module named 'cryptography'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'cryptography'
ModuleNotFoundError: No module named 'requests'
```

**Causes:**
- Virtual environment not activated
- Dependencies not installed
- Wrong Python interpreter

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   # Make sure you see (venv) in your prompt
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check you're using venv Python:**
   ```bash
   which python  # Mac/Linux
   where python  # Windows
   # Should show path with 'venv' in it
   ```

4. **Recreate virtual environment:**
   ```bash
   deactivate
   rm -rf venv  # or rmdir /s venv on Windows
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

### Issue 4: "error: Microsoft Visual C++ 14.0 or greater is required" (Windows)

**Symptoms:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Cause:**
- Missing C++ build tools (needed for cryptography package on Windows)

**Solution:**

1. **Install Microsoft C++ Build Tools:**
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Run installer
   - Select "Desktop development with C++"
   - Install

2. **Or use pre-built wheels:**
   ```bash
   pip install --upgrade pip
   pip install cryptography --only-binary cryptography
   ```

---

## Authentication Issues

### Issue 5: "Authentication failed: 401 Unauthorized"

**Symptoms:**
```
Authentication failed: 401 Unauthorized
Epic authentication failed
Cerner authentication failed
```

**Causes:**
- Wrong Client ID or Client Secret
- Credentials not configured
- App not registered properly

**Solutions:**

1. **Verify credentials are correct:**
   ```bash
   # Check your credentials
   echo $EPIC_CLIENT_ID
   echo $CERNER_CLIENT_ID
   ```

2. **Re-check Epic/Cerner portal:**
   - Log in to Epic sandbox: https://fhir.epic.com/
   - Go to "My Apps"
   - Verify Client ID matches
   - Regenerate Client Secret if needed

3. **Check credentials in script:**
   - Open `transfer_epic_to_cerner.py`
   - Verify lines 24-27 have correct values
   - No extra spaces or quotes

4. **Try re-setting environment variables:**
   ```bash
   # Unset first
   unset EPIC_CLIENT_ID EPIC_CLIENT_SECRET
   unset CERNER_CLIENT_ID CERNER_CLIENT_SECRET

   # Set again with correct values
   export EPIC_CLIENT_ID='your_correct_id'
   ```

---

### Issue 6: "CREDENTIALS NOT CONFIGURED"

**Symptoms:**
```
⚠️  CREDENTIALS NOT CONFIGURED
Please set up your Epic and Cerner credentials
```

**Cause:**
- Credentials not set or still showing placeholder values

**Solutions:**

1. **Check if placeholders are still there:**
   ```python
   # In transfer_epic_to_cerner.py, check if you see:
   EPIC_CLIENT_ID = "YOUR_EPIC_CLIENT_ID"  # ❌ WRONG

   # Should be:
   EPIC_CLIENT_ID = "a1b2c3d4-e5f6-..."    # ✅ CORRECT
   ```

2. **Set environment variables:**
   ```bash
   export EPIC_CLIENT_ID='actual_id_here'
   export EPIC_CLIENT_SECRET='actual_secret_here'
   export CERNER_CLIENT_ID='actual_id_here'
   export CERNER_CLIENT_SECRET='actual_secret_here'
   ```

3. **Edit the script directly:**
   - Open `transfer_epic_to_cerner.py` in a text editor
   - Replace placeholder values on lines 24-27
   - Save file

---

### Issue 7: "403 Forbidden" or "Access Denied"

**Symptoms:**
```
403 Forbidden
Access Denied
Insufficient scopes
```

**Causes:**
- App doesn't have required scopes/permissions
- Using production credentials in sandbox

**Solutions:**

1. **Check app scopes in Epic:**
   - Go to https://fhir.epic.com/
   - Edit your app
   - Ensure these scopes are selected:
     - `system/Patient.read`
     - `system/Observation.read`
     - `system/Condition.read`
     - `system/MedicationRequest.read`
     - `system/AllergyIntolerance.read`

2. **Check app scopes in Cerner:**
   - Go to https://fhir.cerner.com/
   - Edit your app
   - Ensure these scopes are selected:
     - `system/Patient.write`
     - `system/Observation.write`
     - `system/Condition.write`
     - `system/MedicationRequest.write`
     - `system/AllergyIntolerance.write`

3. **Recreate the app** if scopes can't be changed

---

## Transfer Issues

### Issue 8: "Patient not found" or "Invalid patient ID"

**Symptoms:**
```
Patient not found
Invalid patient ID
404 Not Found
```

**Causes:**
- Wrong patient ID format
- Patient doesn't exist in sandbox
- Extra spaces in patient ID

**Solutions:**

1. **Use Epic test patient IDs:**
   ```python
   # Correct IDs (copy-paste exactly):
   "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB"
   "eq081-VQEgP8drUUqCWzHfw3"
   ```

2. **Check for extra spaces:**
   ```python
   # Wrong (has space):
   "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB "

   # Correct (no space):
   "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB"
   ```

3. **Find more test patients:**
   - Visit: https://fhir.epic.com/Documentation?docId=testpatients
   - Copy patient IDs exactly as shown

---

### Issue 9: "Transfer failed: No data to transfer"

**Symptoms:**
```
Transfer failed
No data elements selected
Empty data set
```

**Cause:**
- No data elements selected
- Patient has no data in Epic sandbox

**Solutions:**

1. **Select at least one data element:**
   - When prompted, choose option 1 (all data)
   - Or select specific elements when using option 4

2. **Try a different patient:**
   - Some test patients have more data than others
   - Use Derrick Lin (usually has the most data)

3. **Check programmatic usage:**
   ```python
   # Make sure data_elements is not empty
   results = transfer.transfer_patient_data(
       epic_patient_id="...",
       data_elements=['patient']  # At least one element
   )
   ```

---

### Issue 10: "Encryption failed" or "Decryption failed"

**Symptoms:**
```
HIPAA Compliance Error: Data encryption failed
HIPAA Compliance Error: Data decryption failed
```

**Causes:**
- cryptography package not installed properly
- Corrupted encryption key

**Solutions:**

1. **Reinstall cryptography:**
   ```bash
   pip uninstall cryptography
   pip install cryptography
   ```

2. **Check Python version:**
   ```bash
   python --version
   # Must be 3.8 or higher
   ```

3. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} +
   rm -rf backend/__pycache__
   ```

---

## Network Issues

### Issue 11: "Connection timeout" or "Cannot connect to server"

**Symptoms:**
```
Connection timeout
requests.exceptions.ConnectionError
Cannot connect to fhir.epic.com
Cannot connect to fhir.cerner.com
```

**Causes:**
- No internet connection
- Firewall blocking Python
- Epic/Cerner API temporarily down
- VPN interfering

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping google.com
   curl https://fhir.epic.com
   ```

2. **Check firewall:**
   - Windows: Allow Python through Windows Firewall
   - Mac: System Preferences → Security & Privacy → Firewall
   - Corporate network: May need IT to whitelist Epic/Cerner domains

3. **Disable VPN temporarily** (if using one)

4. **Check API status:**
   - Epic: Try opening https://fhir.epic.com/ in browser
   - Cerner: Try opening https://fhir.cerner.com/ in browser

5. **Try again later:**
   - APIs may be temporarily down for maintenance

---

### Issue 12: "SSL Certificate verification failed"

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
requests.exceptions.SSLError
```

**Causes:**
- Corporate proxy/firewall
- Antivirus interfering
- Outdated certifi package

**Solutions:**

1. **Update certifi:**
   ```bash
   pip install --upgrade certifi
   ```

2. **Reinstall requests:**
   ```bash
   pip uninstall requests
   pip install requests
   ```

3. **Check system time:**
   - Make sure your computer's date/time is correct

4. **Corporate network:**
   - May need to install corporate SSL certificates
   - Contact IT for help

---

## Permission Issues

### Issue 13: "Permission denied" when creating logs directory

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'logs'
```

**Cause:**
- No write permission in current directory

**Solutions:**

1. **Create with proper permissions:**
   ```bash
   # Mac/Linux
   mkdir -p logs
   chmod 755 logs

   # Windows (as Administrator)
   mkdir logs
   ```

2. **Run with sudo (Mac/Linux):**
   ```bash
   sudo mkdir logs
   sudo chmod 777 logs
   ```

3. **Change to different directory:**
   ```bash
   cd ~/Documents
   git clone ...
   ```

---

### Issue 14: "Cannot write to log file"

**Symptoms:**
```
PermissionError: 'logs/hipaa_audit.log'
FileNotFoundError: 'logs/transfer_xyz.json'
```

**Solutions:**

1. **Check logs directory exists:**
   ```bash
   ls -la logs/
   # Should show directory with write permissions
   ```

2. **Fix permissions:**
   ```bash
   # Mac/Linux
   chmod 777 logs/

   # Windows (as Administrator)
   icacls logs /grant Everyone:F
   ```

3. **Use different logs location:**
   Edit Python files to use absolute path:
   ```python
   import os
   logs_dir = os.path.expanduser('~/medisync_logs')
   os.makedirs(logs_dir, exist_ok=True)
   ```

---

## Platform-Specific Issues

### Windows: "cannot be loaded because running scripts is disabled"

**Symptoms (PowerShell):**
```
venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solution:**

1. **Run PowerShell as Administrator**

2. **Change execution policy:**
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Activate again:**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. **Or use Command Prompt instead:**
   ```cmd
   venv\Scripts\activate
   ```

---

### Mac: "Operation not permitted"

**Symptoms:**
```
OSError: [Errno 1] Operation not permitted
```

**Cause:**
- macOS System Integrity Protection (SIP)

**Solutions:**

1. **Don't install in system directories:**
   ```bash
   # Bad:
   cd /usr/local/

   # Good:
   cd ~/projects/
   ```

2. **Use user directory:**
   ```bash
   cd ~/Documents/Medisync
   ```

---

### Linux: "bash: venv/bin/activate: No such file or directory"

**Symptoms:**
```
bash: venv/bin/activate: No such file or directory
```

**Cause:**
- Virtual environment not created properly
- python3-venv not installed

**Solutions:**

1. **Install venv module:**
   ```bash
   sudo apt install python3-venv python3-pip
   ```

2. **Recreate virtual environment:**
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   ```

---

## Getting More Help

### Check Log Files

Always check log files for detailed error information:

```bash
# View all logs
ls -la logs/

# View transfer log (most recent errors)
tail -50 logs/epic_to_cerner_transfer.log

# View audit log
tail -50 logs/hipaa_audit.log

# View Epic FHIR log
tail -50 logs/epic_fhir.log

# View Cerner FHIR log
tail -50 logs/cerner_fhir.log
```

### Enable Debug Logging

Edit Python files to show more details:

```python
# At the top of the file, change:
logging.basicConfig(level=logging.INFO)

# To:
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

Isolate the problem:

```bash
# Test Python installation
python --version
pip --version

# Test Epic client only
cd backend
python epic_fhir_client.py

# Test Cerner client only
python cerner_fhir_client.py

# Test HIPAA compliance only
python hipaa_compliant_ehr_transfer.py
```

### Verify Dependencies

```bash
# List installed packages
pip list

# Check specific package
pip show cryptography
pip show requests

# Reinstall all dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

---

## Still Having Issues?

1. **Read the full error message** - it often tells you exactly what's wrong
2. **Check the SETUP_GUIDE.md** for detailed setup instructions
3. **Review your credentials** - most issues are authentication-related
4. **Try with a fresh virtual environment**
5. **Search Epic/Cerner documentation** for API-specific errors
6. **Check system requirements:**
   - Python 3.8+
   - Internet connection
   - Valid Epic/Cerner sandbox credentials

---

## Error Message Reference

| Error | Most Common Cause | Quick Fix |
|-------|------------------|-----------|
| `Python not found` | Python not installed | Install Python, add to PATH |
| `pip not found` | pip not installed | `python -m ensurepip` |
| `ModuleNotFoundError` | Venv not activated | `source venv/bin/activate` |
| `401 Unauthorized` | Wrong credentials | Check Client ID/Secret |
| `403 Forbidden` | Missing scopes | Add scopes in app settings |
| `404 Not Found` | Wrong patient ID | Use Epic test patient IDs |
| `Connection timeout` | Network issue | Check internet, firewall |
| `Permission denied` | File permissions | `chmod 777 logs/` |
| `SSL Error` | Certificate issue | `pip install --upgrade certifi` |

---

**For step-by-step setup, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

**For quick commands, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
