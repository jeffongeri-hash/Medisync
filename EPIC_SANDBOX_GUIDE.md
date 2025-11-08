# Epic FHIR Sandbox Integration Guide

## 🎯 Overview

This script connects to **Epic's real FHIR sandbox** and retrieves actual patient data including:
- ✅ Patient demographics (name, date of birth, gender, contact info)
- ✅ Vital signs (blood pressure, weight, temperature, etc.)
- ✅ Medications (active prescriptions with dosages)
- ✅ Medical conditions (diagnoses and problems)

**Important:** This uses Epic's **public sandbox** which requires no authentication. It's perfect for testing and development!

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the `requests` library needed for API calls.

### Step 2: Run the Script

```bash
python epic_fhir_client.py
```

### Step 3: Select a Patient

When prompted, press Enter to use the default patient, or enter 1-4 to select a different test patient:

```
Available Test Patients:
1. Derrick Lin
2. Camilla Lopez
3. Desiree Powell
4. Amy Shaw

Press Enter to use default patient (Derrick Lin) or enter patient number (1-4):
>
```

### Step 4: View the Results

The script will display:
- Patient information
- Vital signs
- Current medications
- Medical conditions

---

## 📋 Available Test Patients

Epic's sandbox provides these test patients with real FHIR data:

| # | Patient Name | Patient ID | Description |
|---|--------------|------------|-------------|
| 1 | Derrick Lin | `eqBqGJ4BxFL.84mz3p93QiQB` | Default test patient |
| 2 | Camilla Lopez | `erXuFYUfU6B3BKuMKq9T0SQB` | Alternative test patient |
| 3 | Desiree Powell | `eCRk28CcQU9LYgwE.OUVqXAB` | Alternative test patient |
| 4 | Amy Shaw | `egqBHIZQfVZQpJARGdlD.3QB` | Alternative test patient |

**Note:** These are Epic's official test patient IDs for their public sandbox environment.

---

## 🔧 How It Works

### 1. FHIR API Connection

```python
# Epic's public FHIR R4 endpoint
BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
```

### 2. Data Extraction Process

```
1. Connect to Epic FHIR Sandbox
2. GET /Patient/{id}           → Demographics
3. GET /Observation?patient=   → Vital Signs
4. GET /MedicationRequest?     → Medications
5. GET /Condition?patient=     → Medical Conditions
6. Parse and display results
```

### 3. FHIR Resources Retrieved

- **Patient Resource**: Name, DOB, gender, contact info, address
- **Observation Resource**: Vital signs (BP, weight, temperature, etc.)
- **MedicationRequest Resource**: Active medications and dosages
- **Condition Resource**: Medical diagnoses and problems

---

## 📊 Example Output

```
================================================================================
PATIENT INFORMATION FROM EPIC FHIR SANDBOX
================================================================================

👤 PATIENT DEMOGRAPHICS
--------------------------------------------------------------------------------
Name:              Derrick Lin
Patient ID:        eqBqGJ4BxFL.84mz3p93QiQB
Date of Birth:     1990-05-15
Gender:            Male
Phone:             555-0123
Address:           123 Main Street
City, State:       Madison, WI 53703

📈 VITAL SIGNS
--------------------------------------------------------------------------------
1. Blood Pressure
   Value: Systolic: 120 mmHg, Diastolic: 80 mmHg
   Date:  2024-10-15

2. Body Weight
   Value: 185.0 lbs
   Date:  2024-10-15

3. Body Temperature
   Value: 98.6 F
   Date:  2024-10-15

💊 MEDICATIONS
--------------------------------------------------------------------------------
1. Lisinopril 10 MG Oral Tablet
   Dosage: Take 1 tablet by mouth once daily
   Status: active
   Date:   2024-01-15

2. Metformin 500 MG Oral Tablet
   Dosage: Take 1 tablet by mouth twice daily with meals
   Status: active
   Date:   2024-02-20

⚕️  MEDICAL CONDITIONS
--------------------------------------------------------------------------------
1. Essential Hypertension
   Status: active
   Onset:  2023-06-10

2. Type 2 Diabetes Mellitus
   Status: active
   Onset:  2023-08-15

================================================================================
✅ Data retrieved from Epic FHIR Sandbox at 2025-11-08 10:30:45
================================================================================
```

---

## 🔑 Key Features

### ✅ No Authentication Required
- Uses Epic's **public sandbox** endpoints
- No OAuth tokens needed for testing
- Perfect for learning and development

### ✅ Real FHIR Data
- Actual FHIR R4 resources from Epic
- Standard healthcare data formats
- Realistic clinical data

### ✅ Multiple Patients
- 4 different test patients available
- Each with unique medical history
- Switch between patients easily

### ✅ Comprehensive Data
- Demographics
- Vital signs
- Medications
- Medical conditions

---

## 🛠️ Customization

### Use Your Own Patient ID

Edit the script or modify the `patient_id` variable:

```python
# In epic_fhir_client.py
patient_id = "your-patient-id-here"
```

### Add More Data Types

The script can be extended to retrieve:
- **Allergies**: `AllergyIntolerance` resource
- **Immunizations**: `Immunization` resource
- **Lab Results**: `Observation` with category "laboratory"
- **Procedures**: `Procedure` resource
- **Encounters**: `Encounter` resource

Example to add allergies:

```python
def get_allergies(self, patient_id: str) -> List[Dict]:
    """Get patient allergies"""
    try:
        url = f"{self.base_url}/AllergyIntolerance"
        params = {'patient': patient_id}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'entry' in data:
            return [entry['resource'] for entry in data['entry']]
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching allergies: {e}")
        return []
```

---

## 🐛 Troubleshooting

### Error: "Connection refused" or "Network error"

**Problem:** Cannot connect to Epic's sandbox

**Solution:**
1. Check your internet connection
2. Verify the URL is correct: `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4`
3. Epic's sandbox may be temporarily down - try again later

---

### Error: "No module named 'requests'"

**Problem:** Missing dependencies

**Solution:**
```bash
pip install requests
# or
pip install -r requirements.txt
```

---

### Error: "Patient not found" or 404

**Problem:** Invalid patient ID

**Solution:** Use one of the provided test patient IDs:
- `eqBqGJ4BxFL.84mz3p93QiQB` (Derrick Lin)
- `erXuFYUfU6B3BKuMKq9T0SQB` (Camilla Lopez)
- `eCRk28CcQU9LYgwE.OUVqXAB` (Desiree Powell)
- `egqBHIZQfVZQpJARGdlD.3QB` (Amy Shaw)

---

### No data returned for some resources

**Problem:** Patient may not have data for that resource type

**Solution:** This is normal - not all test patients have complete data. Try different test patients to see various data types.

---

## 📚 Understanding FHIR Resources

### Patient Resource
Contains demographics:
```json
{
  "resourceType": "Patient",
  "id": "eqBqGJ4BxFL.84mz3p93QiQB",
  "name": [{"given": ["Derrick"], "family": "Lin"}],
  "birthDate": "1990-05-15",
  "gender": "male"
}
```

### Observation Resource (Vital Signs)
Contains measurements:
```json
{
  "resourceType": "Observation",
  "code": {"text": "Blood Pressure"},
  "valueQuantity": {"value": 120, "unit": "mmHg"},
  "effectiveDateTime": "2024-10-15"
}
```

### MedicationRequest Resource
Contains prescriptions:
```json
{
  "resourceType": "MedicationRequest",
  "medicationCodeableConcept": {"text": "Lisinopril 10 MG"},
  "dosageInstruction": [{"text": "Take 1 tablet daily"}],
  "status": "active"
}
```

---

## 🔗 API Endpoints Used

| Resource Type | Endpoint | Purpose |
|---------------|----------|---------|
| Patient | `GET /Patient/{id}` | Get patient demographics |
| Observation | `GET /Observation?patient={id}&category=vital-signs` | Get vital signs |
| MedicationRequest | `GET /MedicationRequest?patient={id}&status=active` | Get medications |
| Condition | `GET /Condition?patient={id}` | Get medical conditions |

---

## 🎓 Next Steps

### For Production Use

To use this with a **real Epic production system**, you'll need:

1. **OAuth 2.0 Authentication**
   - Register your app with Epic
   - Get client ID and client secret
   - Implement OAuth 2.0 authorization code flow
   - Handle token refresh

2. **Epic App Orchard Registration**
   - Register at https://apporchard.epic.com/
   - Submit your application for review
   - Get production credentials

3. **HIPAA Compliance**
   - Implement encryption for PHI
   - Add comprehensive audit logging
   - Secure credential storage
   - Get Business Associate Agreement (BAA)

4. **Error Handling**
   - Retry logic for failed requests
   - Rate limiting
   - Proper error messages

### Example OAuth Implementation

```python
def get_oauth_token(client_id: str, client_secret: str) -> str:
    """Get OAuth token from Epic"""
    token_url = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, data=data)
    return response.json()['access_token']
```

---

## 📖 Resources

- **Epic FHIR Documentation**: https://fhir.epic.com/
- **Epic App Orchard**: https://apporchard.epic.com/
- **FHIR Specification**: https://www.hl7.org/fhir/
- **Epic Sandbox Patients**: https://fhir.epic.com/Documentation?docId=testpatients

---

## ⚠️ Important Notes

1. **Sandbox Data Only**: This script uses Epic's test sandbox. Data is not real patient information.

2. **No Authentication**: The public sandbox doesn't require OAuth. Production systems do.

3. **Rate Limiting**: Epic may rate-limit requests. Add delays if making many requests.

4. **Data Availability**: Not all test patients have complete data for all resource types.

5. **HIPAA**: This sandbox is for testing only. Never use it for real patient data.

---

## ✅ Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default patient
python epic_fhir_client.py

# Run and select patient interactively
python epic_fhir_client.py
# Then enter 1-4 when prompted
```

---

**Enjoy exploring Epic's FHIR API! 🎉**
