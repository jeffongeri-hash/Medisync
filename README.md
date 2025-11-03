# HIPAA-Compliant EHR Transfer System

A secure, HIPAA-compliant system for transferring Electronic Health Records (EHR) between healthcare systems, with full support for Epic and Cerner FHIR APIs.

## Features

- **Bi-Directional EHR Integration**: Read from Epic, write to Cerner
- **OAuth 2.0 Authentication**: Secure authentication with both EHR systems
- **End-to-End Encryption**: Fernet (AES-128) encryption for sensitive PHI
- **Patient Consent Verification**: Ensures patients have consented to data sharing
- **Data Minimization**: Transfers only necessary data elements
- **Data Integrity**: SHA-256 checksums to verify data hasn't been tampered with
- **Comprehensive Audit Logging**: Full audit trail for HIPAA compliance
- **Epic FHIR Support**: Read patient data from Epic's FHIR API
- **Cerner FHIR Support**: Write patient data to Cerner's FHIR API
- **FHIR Resource Transformation**: Automatic data mapping between systems

## Project Structure

```
Medisync/
├── backend/
│   ├── hipaa_compliant_ehr_transfer.py   # Core HIPAA-compliant transfer logic
│   ├── epic_fhir_client.py               # Epic FHIR API client (read)
│   ├── cerner_fhir_client.py             # Cerner FHIR API client (write)
│   └── epic_to_cerner_transfer.py        # Complete Epic→Cerner integration
├── logs/                                  # Audit logs and transfer records
├── transfer_epic_to_cerner.py            # Quick start transfer script
├── requirements.txt                       # Python dependencies
├── .env.example                          # Configuration template
└── README.md                             # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Epic sandbox account (for reading EHR data)
- Cerner sandbox account (for writing EHR data)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Medisync
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create logs directory**
   ```bash
   mkdir -p logs
   ```

5. **Configure credentials** (choose one):

   **Option A: Environment Variables (Recommended)**
   ```bash
   export EPIC_CLIENT_ID='your_epic_client_id'
   export EPIC_CLIENT_SECRET='your_epic_client_secret'
   export CERNER_CLIENT_ID='your_cerner_client_id'
   export CERNER_CLIENT_SECRET='your_cerner_client_secret'
   ```

   **Option B: Edit the script**
   Edit `transfer_epic_to_cerner.py` and update the CONFIGURATION section.

## Quick Start: Transfer Patient Data from Epic to Cerner

The easiest way to transfer patient data from Epic to Cerner:

```bash
python transfer_epic_to_cerner.py
```

This interactive script will guide you through:
1. Selecting a test patient (or entering a custom patient ID)
2. Choosing which data elements to transfer
3. Authenticating with both Epic and Cerner
4. Performing the secure transfer with full HIPAA compliance
5. Displaying detailed transfer results

### Example Output

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

Select patient (1-2): 1

Data Elements to Transfer:
1. All data (patient, conditions, medications, allergies, observations)
Select option (1-4) [default: 1]: 1

✓ Transfer completed successfully!
   Epic Patient ID: Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
   Cerner Patient ID: 12345
   Resources Created: 42 (15 conditions, 10 medications, 5 allergies, 12 observations)
```

## Usage

### 1. Epic FHIR Client (Recommended for Production)

#### Register with Epic Sandbox

1. Visit [https://fhir.epic.com/](https://fhir.epic.com/)
2. Click "Build Apps" → "Register"
3. Create a **non-production app**
4. Select app type: **Backend Systems**
5. Note your **Client ID**
6. For sandbox testing, you'll get a **Client Secret**

#### Update Credentials

Edit `backend/epic_fhir_client.py` and update:

```python
client_id = "YOUR_CLIENT_ID_HERE"
client_secret = "YOUR_CLIENT_SECRET_HERE"
```

#### Run Epic FHIR Client

```bash
cd backend
python epic_fhir_client.py
```

#### Use in Your Code

```python
from backend.epic_fhir_client import EpicFHIRClient

# Initialize client
client = EpicFHIRClient(client_id="your_client_id")

# Authenticate
client.authenticate_backend_service(client_secret="your_secret")

# Get patient data
patient_data = client.get_patient("patient_id")

# Get comprehensive record
comprehensive_record = client.get_comprehensive_patient_record("patient_id")

# Access specific data types
conditions = client.get_patient_conditions("patient_id")
medications = client.get_patient_medications("patient_id")
allergies = client.get_patient_allergies("patient_id")
observations = client.get_patient_observations("patient_id")
```

### 2. Cerner FHIR Client (Write Data to Cerner)

#### Register with Cerner Sandbox

1. Visit [https://fhir.cerner.com/](https://fhir.cerner.com/)
2. Click "Register" → "Create System Account"
3. Create a **system account** for backend services
4. Note your **Client ID** and **Client Secret**

#### Use Cerner Client in Your Code

```python
from backend.cerner_fhir_client import CernerFHIRClient

# Initialize client
client = CernerFHIRClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Authenticate
client.authenticate_backend_service()

# Create patient
patient_resource = {
    "resourceType": "Patient",
    "name": [{"family": "Doe", "given": ["John"]}],
    "gender": "male",
    "birthDate": "1980-01-01"
}
created_patient = client.create_patient(patient_resource)

# Create observation (lab result, vital sign)
observation = {
    "resourceType": "Observation",
    "status": "final",
    "subject": {"reference": f"Patient/{created_patient['id']}"},
    "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9"}]},
    "valueQuantity": {"value": 120, "unit": "mmHg"}
}
client.create_observation(observation)
```

### 3. Complete Epic to Cerner Transfer

Transfer complete patient records from Epic to Cerner using the integration module:

#### Programmatic Usage

```python
from backend.epic_to_cerner_transfer import EpicToCernerTransfer

# Initialize transfer handler
transfer = EpicToCernerTransfer(
    epic_client_id="your_epic_client_id",
    epic_client_secret="your_epic_secret",
    cerner_client_id="your_cerner_client_id",
    cerner_client_secret="your_cerner_secret"
)

# Authenticate with both systems
transfer.authenticate_systems()

# Transfer patient data
results = transfer.transfer_patient_data(
    epic_patient_id="Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB",
    data_elements=['patient', 'conditions', 'medications', 'allergies', 'observations']
)

print(f"Transfer completed!")
print(f"Epic Patient ID: {results['epic_patient_id']}")
print(f"Cerner Patient ID: {results['cerner_patient_id']}")
print(f"Resources created: {results['resources_created']}")
```

#### What Gets Transferred

The system transfers the following data from Epic to Cerner:

- **Patient Demographics**: Name, gender, birth date, identifiers
- **Conditions**: All diagnoses and health conditions
- **Medications**: Current and past medication requests
- **Allergies**: Allergy intolerances
- **Observations**:
  - Laboratory results (e.g., HbA1c, CBC, metabolic panels)
  - Vital signs (e.g., blood pressure, temperature, heart rate)

#### Security During Transfer

1. **Authentication**: OAuth 2.0 with both Epic and Cerner
2. **Encryption**: AES-128 encryption of PHI during transfer
3. **Integrity**: SHA-256 checksums to verify data hasn't been modified
4. **Audit Logging**: Complete audit trail for HIPAA compliance
5. **Data Minimization**: Only requested elements are transferred
6. **Consent Verification**: Patient consent checked before transfer

### 4. Generic HIPAA-Compliant Transfer System

For demonstrating HIPAA-compliant transfer principles:

```bash
cd backend
python hipaa_compliant_ehr_transfer.py
```

This demonstrates:
- OAuth 2.0 authentication flow
- Patient consent verification
- Data encryption and decryption
- Data minimization
- Integrity validation
- Audit logging

## Epic Sandbox Test Patients

Epic provides test patient IDs for sandbox testing:

| Patient Name | Patient ID |
|--------------|------------|
| Derrick Lin | `Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB` |
| Camila Lopez | `eq081-VQEgP8drUUqCWzHfw3` |

More test patients available at: [Epic FHIR Sandbox](https://fhir.epic.com/)

## FHIR Resources Supported

The Epic FHIR client supports the following FHIR R4 resources:

- **Patient**: Demographics and identifiers
- **Condition**: Diagnoses and health conditions
- **MedicationRequest**: Current and past medications
- **AllergyIntolerance**: Allergies and intolerances
- **Observation**: Lab results and vital signs
  - Laboratory results
  - Vital signs (BP, temp, etc.)

## Example: Fetch Patient Data from Epic

```python
from backend.epic_fhir_client import EpicFHIRClient
import json

# Initialize and authenticate
client = EpicFHIRClient(client_id="your_client_id")
client.authenticate_backend_service(client_secret="your_secret")

# Get comprehensive patient record
patient_id = "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB"
record = client.get_comprehensive_patient_record(patient_id)

# Access data
print(f"Patient: {record['patient']['name'][0]['given'][0]} {record['patient']['name'][0]['family']}")
print(f"Conditions: {len(record['conditions'])}")
print(f"Medications: {len(record['medications'])}")
print(f"Allergies: {len(record['allergies'])}")
print(f"Lab Results: {len(record['observations']['laboratory'])}")

# Save to file
with open(f'patient_{patient_id}.json', 'w') as f:
    json.dump(record, f, indent=2)
```

## HIPAA Compliance Features

### Security Controls

1. **Access Control**
   - OAuth 2.0 authentication
   - Token-based authorization
   - Session management

2. **Data Protection**
   - AES-128 encryption (Fernet)
   - TLS/HTTPS for data in transit
   - Encryption at rest

3. **Data Integrity**
   - SHA-256 checksums
   - Tamper detection
   - Version control

4. **Audit & Accountability**
   - Comprehensive logging
   - Transfer tracking
   - User action logging

### Compliance Requirements Met

- ✅ **164.308(a)(3)**: Workforce security
- ✅ **164.308(a)(4)**: Information access management
- ✅ **164.312(a)(1)**: Access control
- ✅ **164.312(a)(2)(i)**: Unique user identification
- ✅ **164.312(c)(1)**: Integrity controls
- ✅ **164.312(d)**: Person or entity authentication
- ✅ **164.312(e)(1)**: Transmission security
- ✅ **164.312(e)(2)(i)**: Integrity controls
- ✅ **164.312(e)(2)(ii)**: Encryption

## Audit Logs

All operations are logged to `logs/` directory for HIPAA compliance:

- `hipaa_audit.log`: General audit trail
- `epic_fhir.log`: Epic API interactions
- `cerner_fhir.log`: Cerner API interactions
- `epic_to_cerner_transfer.log`: Epic→Cerner transfer operations
- `transfer_<id>.json`: Individual transfer records with complete metadata
- `transfer_epic_to_cerner_<id>.json`: Detailed Epic→Cerner transfer results

Each log entry includes:
- Timestamp (UTC)
- Action performed
- User/system identifier
- Patient identifier (de-identified where appropriate)
- Data elements accessed/transferred
- Authentication events
- Success/failure status
- Error details (if applicable)

## Production Deployment

### Security Checklist

- [ ] Use JWT-based authentication instead of client_secret
- [ ] Store credentials in secure vault (e.g., AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable HTTPS/TLS for all connections
- [ ] Implement proper access controls and RBAC
- [ ] Set up database for consent management
- [ ] Configure log rotation and retention
- [ ] Enable intrusion detection
- [ ] Perform security audit and penetration testing
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting

### Environment Variables

Create a `.env` file:

```bash
# Epic Configuration
EPIC_CLIENT_ID=your_epic_client_id
EPIC_CLIENT_SECRET=your_epic_client_secret
EPIC_FHIR_BASE_URL=https://your-epic-instance/api/FHIR/R4
EPIC_TOKEN_URL=https://your-epic-instance/oauth2/token
EPIC_PRIVATE_KEY_PATH=/path/to/private/key.pem  # For production JWT auth

# Cerner Configuration
CERNER_CLIENT_ID=your_cerner_client_id
CERNER_CLIENT_SECRET=your_cerner_client_secret
CERNER_FHIR_BASE_URL=https://your-cerner-instance/r4/tenant-id
CERNER_TOKEN_URL=https://your-cerner-instance/oauth2/token

# Security
LOG_LEVEL=INFO
ENCRYPTION_KEY_PATH=keys/encryption.key
```

## Troubleshooting

### Authentication Issues

**Problem**: "Authentication failed: 401 Unauthorized"

**Solutions**:
- Verify your client_id and client_secret
- Ensure your app is registered in Epic sandbox
- Check token endpoint URL is correct

### API Access Issues

**Problem**: "Patient search failed: 403 Forbidden"

**Solutions**:
- Verify your OAuth token is valid
- Check your app has the correct scopes
- Ensure you're using a valid patient ID

### Network Issues

**Problem**: "Connection timeout"

**Solutions**:
- Check internet connectivity
- Verify firewall settings
- Ensure API endpoints are accessible

## Resources

### EHR System Documentation
- [Epic FHIR Documentation](https://fhir.epic.com/)
- [Cerner FHIR Documentation](https://fhir.cerner.com/)
- [Epic App Orchard](https://apporchard.epic.com/) - Production app registration
- [Cerner Code Console](https://code.cerner.com/) - Developer resources

### Standards & Compliance
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)
- [HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [SMART on FHIR](https://smarthealthit.org/)

## License

This project is for educational and demonstration purposes. Ensure proper security audits and compliance reviews before production use.

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review Epic FHIR documentation
3. Verify credentials and configuration

## Contributing

Contributions welcome! Please ensure:
- Code follows HIPAA compliance best practices
- All security features are maintained
- Proper error handling and logging
- Documentation is updated

---

**⚠️ Important**: This system handles Protected Health Information (PHI). Ensure all deployments comply with HIPAA, HITECH, and relevant healthcare data protection regulations.
