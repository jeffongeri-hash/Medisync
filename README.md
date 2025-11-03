# HIPAA-Compliant EHR Transfer System

A secure, HIPAA-compliant system for transferring Electronic Health Records (EHR) between healthcare systems, with support for Epic's FHIR API.

## Features

- **OAuth 2.0 Authentication**: Secure authentication with EHR systems
- **End-to-End Encryption**: Fernet (AES-128) encryption for sensitive PHI
- **Patient Consent Verification**: Ensures patients have consented to data sharing
- **Data Minimization**: Transfers only necessary data elements
- **Data Integrity**: SHA-256 checksums to verify data hasn't been tampered with
- **Comprehensive Audit Logging**: Full audit trail for HIPAA compliance
- **Epic FHIR Support**: Direct integration with Epic's FHIR API

## Project Structure

```
Medisync/
├── backend/
│   ├── hipaa_compliant_ehr_transfer.py  # Core HIPAA-compliant transfer logic
│   └── epic_fhir_client.py              # Epic FHIR API client
├── logs/                                 # Audit logs and transfer records
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Epic sandbox account (for testing with Epic FHIR)

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

### 2. Generic HIPAA-Compliant Transfer System

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

All operations are logged to `logs/` directory:

- `hipaa_audit.log`: General audit trail
- `epic_fhir.log`: Epic API interactions
- `transfer_<id>.json`: Individual transfer records

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
EPIC_CLIENT_ID=your_production_client_id
EPIC_PRIVATE_KEY_PATH=/path/to/private/key.pem
EPIC_FHIR_BASE_URL=https://your-epic-instance/api/FHIR/R4
EPIC_TOKEN_URL=https://your-epic-instance/oauth2/token
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

- [Epic FHIR Documentation](https://fhir.epic.com/)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)
- [OAuth 2.0 Specification](https://oauth.net/2/)

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
