# Quick Reference Guide

Quick commands and reminders for the HIPAA-Compliant EHR Transfer System.

---

## Setup Commands (First Time Only)

```bash
# Clone repository
git clone https://github.com/jeffongeri-hash/Medisync.git
cd Medisync
git checkout claude/hipaa-ehr-transfer-system-011CUkKjNn5EEtFWJoyuDMix

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate              # Windows CMD
venv\Scripts\Activate.ps1          # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir logs
```

---

## Set Credentials (Every Session)

### Mac/Linux
```bash
export EPIC_CLIENT_ID='your_epic_client_id'
export EPIC_CLIENT_SECRET='your_epic_secret'
export CERNER_CLIENT_ID='your_cerner_client_id'
export CERNER_CLIENT_SECRET='your_cerner_secret'
```

### Windows CMD
```cmd
set EPIC_CLIENT_ID=your_epic_client_id
set EPIC_CLIENT_SECRET=your_epic_secret
set CERNER_CLIENT_ID=your_cerner_client_id
set CERNER_CLIENT_SECRET=your_cerner_secret
```

### Windows PowerShell
```powershell
$env:EPIC_CLIENT_ID='your_epic_client_id'
$env:EPIC_CLIENT_SECRET='your_epic_secret'
$env:CERNER_CLIENT_ID='your_cerner_client_id'
$env:CERNER_CLIENT_SECRET='your_cerner_secret'
```

---

## Run Transfer

```bash
# Activate virtual environment first!
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run transfer
python transfer_epic_to_cerner.py
```

---

## Epic Test Patient IDs

```python
# Derrick Lin
"Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB"

# Camila Lopez
"eq081-VQEgP8drUUqCWzHfw3"
```

More: https://fhir.epic.com/Documentation?docId=testpatients

---

## Test Individual Components

```bash
# Epic FHIR client (read data from Epic)
cd backend
python epic_fhir_client.py

# Cerner FHIR client (write data to Cerner)
python cerner_fhir_client.py

# HIPAA compliance features
python hipaa_compliant_ehr_transfer.py

# Complete Epic-to-Cerner integration
python epic_to_cerner_transfer.py
```

---

## View Logs

```bash
# List all logs
ls -la logs/

# View transfer log
cat logs/epic_to_cerner_transfer.log

# View audit log
cat logs/hipaa_audit.log

# View specific transfer details (pretty print)
cat logs/transfer_epic_to_cerner_*.json | python -m json.tool

# View latest transfer
ls -t logs/transfer_epic_to_cerner_*.json | head -1 | xargs cat
```

---

## Common Issues & Fixes

### Virtual environment not activated
**Symptom:** ModuleNotFoundError

**Fix:**
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Dependencies not installed
**Symptom:** "No module named 'cryptography'"

**Fix:**
```bash
pip install -r requirements.txt
```

### Credentials not set
**Symptom:** "CREDENTIALS NOT CONFIGURED"

**Fix:** Set environment variables or edit `transfer_epic_to_cerner.py` lines 24-27

### Authentication fails
**Symptom:** "401 Unauthorized"

**Fix:**
- Verify credentials are correct
- Check app registration in Epic/Cerner sandbox
- Try re-creating the app

---

## Register for Sandbox Access

### Epic Sandbox
1. Go to: https://fhir.epic.com/
2. Click "Build Apps" → "Register"
3. Create "Backend Systems" app
4. Save Client ID and Client Secret

### Cerner Sandbox
1. Go to: https://fhir.cerner.com/
2. Create "System Account"
3. Save Client ID and Client Secret

---

## Project Structure

```
Medisync/
├── backend/
│   ├── epic_fhir_client.py           # Epic API client
│   ├── cerner_fhir_client.py         # Cerner API client
│   ├── epic_to_cerner_transfer.py    # Complete integration
│   └── hipaa_compliant_ehr_transfer.py  # HIPAA compliance
├── logs/                              # Audit logs
├── transfer_epic_to_cerner.py        # Main script
├── requirements.txt                   # Dependencies
├── README.md                          # Full documentation
├── SETUP_GUIDE.md                    # Step-by-step setup
└── QUICK_REFERENCE.md                # This file
```

---

## Programmatic Usage

```python
from backend.epic_to_cerner_transfer import EpicToCernerTransfer

# Initialize
transfer = EpicToCernerTransfer(
    epic_client_id="your_epic_id",
    epic_client_secret="your_epic_secret",
    cerner_client_id="your_cerner_id",
    cerner_client_secret="your_cerner_secret"
)

# Authenticate
transfer.authenticate_systems()

# Transfer patient
results = transfer.transfer_patient_data(
    epic_patient_id="Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB",
    data_elements=['patient', 'conditions', 'medications', 'allergies', 'observations']
)

# View results
print(f"Cerner Patient ID: {results['cerner_patient_id']}")
print(f"Resources created: {results['resources_created']}")
```

---

## Data Elements Available

- `patient` - Demographics (name, gender, birth date)
- `conditions` - Diagnoses and health conditions
- `medications` - Medication requests
- `allergies` - Allergy intolerances
- `observations` - Lab results and vital signs

---

## Important URLs

- **Epic Sandbox:** https://fhir.epic.com/
- **Cerner Sandbox:** https://fhir.cerner.com/
- **FHIR R4 Spec:** https://hl7.org/fhir/R4/
- **HIPAA Info:** https://www.hhs.gov/hipaa/

---

## Security Checklist

Every transfer includes:
- ✅ OAuth 2.0 authentication
- ✅ AES-128 encryption
- ✅ SHA-256 integrity checksums
- ✅ Complete audit logging
- ✅ Patient consent verification
- ✅ Data minimization

---

## Deactivate Virtual Environment

```bash
deactivate
```

---

## Update Code from Git

```bash
git pull origin claude/hipaa-ehr-transfer-system-011CUkKjNn5EEtFWJoyuDMix
pip install -r requirements.txt  # In case dependencies changed
```

---

**For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

**For full documentation, see [README.md](README.md)**
