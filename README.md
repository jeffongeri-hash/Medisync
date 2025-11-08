# Medisync - HIPAA-Compliant EHR Transfer System

A demonstration of secure, HIPAA-compliant Electronic Health Record (EHR) data transfer between healthcare systems.

## 🏥 Overview

Medisync showcases how patient medical data can be securely transferred between different EHR systems (like Epic and Cerner) while maintaining full HIPAA compliance. This educational project includes both a Python backend simulation and an interactive web interface.

## ✨ Features

- 🔐 **OAuth 2.0 Authentication** - Secure system-to-system authentication
- 🔒 **AES-256 Encryption** - Protects sensitive PHI (Protected Health Information)
- 📝 **Comprehensive Audit Logging** - Complete compliance trail
- ✅ **Patient Consent Verification** - Ensures proper authorization
- 🎯 **Data Minimization** - Transfers only necessary information
- 🛡️ **Integrity Validation** - SHA-256 checksums prevent tampering
- 🌐 **Modern Web Interface** - Real-time transfer monitoring

## 🚀 Quick Start

### Option 1: Epic FHIR Sandbox (Real API Integration)

**NEW! Connect to Epic's actual FHIR sandbox and retrieve real patient data:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Epic FHIR client
python epic_fhir_client.py
```

This connects to Epic's public sandbox and retrieves:
- Patient demographics (name, DOB, gender)
- Vital signs (blood pressure, weight, temperature)
- Active medications with dosages
- Medical conditions/diagnoses

**See [EPIC_SANDBOX_GUIDE.md](EPIC_SANDBOX_GUIDE.md) for detailed instructions.**

---

### Option 2: Python Backend (Simulation)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the transfer simulation
python hipaa_compliant_ehr_transfer.py
```

---

### Option 3: Web Application

Simply open `ehr_transfer_web_app.html` in your web browser:

```bash
# On Mac/Linux
open ehr_transfer_web_app.html

# Or use your browser directly
firefox ehr_transfer_web_app.html
chrome ehr_transfer_web_app.html
```

## 📋 Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Python Dependencies

- `requests` - HTTP library for API calls
- `cryptography` - Encryption and security functions

## 🎯 How It Works

### Transfer Process

1. **Authentication** - OAuth 2.0 with source and destination EHR systems
2. **Consent Check** - Verify patient has authorized data sharing
3. **Data Retrieval** - Fetch patient records via FHIR API
4. **Security** - Encrypt sensitive fields and generate checksums
5. **Transmission** - Securely transfer data with integrity validation

### Supported EHR Systems

- Epic Systems
- Cerner PowerChart
- Allscripts
- MEDITECH

## 📊 Demo Data

The system includes realistic mock patient data:

- **Patient Demographics** - Name, DOB, contact information
- **Medical History** - Chronic conditions and diagnoses
- **Vital Signs** - Blood pressure, weight, glucose levels
- **Medications** - Active prescriptions with dosages
- **Surgical History** - Past procedures

## 🔒 Security Features

### HIPAA Compliance Demonstrated

✅ Access Control (§164.312(a)(1))
✅ Unique User Identification (§164.312(a)(2)(i))
✅ Audit Controls (§164.312(b))
✅ Integrity Controls (§164.312(c)(1))
✅ Authentication (§164.312(d))
✅ Transmission Security (§164.312(e)(1))
✅ Minimum Necessary Standard (§164.502(b))

### Security Layers

- **Application**: OAuth tokens, session management
- **Data**: Fernet encryption (AES-256), SHA-256 checksums
- **Transport**: HTTPS/TLS (simulated)
- **Audit**: Comprehensive logging to `ehr_audit.log`

## 📁 Project Structure

```
Medisync/
├── epic_fhir_client.py                # Epic FHIR sandbox client (NEW!)
├── hipaa_compliant_ehr_transfer.py    # Python backend simulation
├── ehr_transfer_web_app.html          # Web interface
├── requirements.txt                   # Python dependencies
├── EPIC_SANDBOX_GUIDE.md              # Epic API integration guide (NEW!)
├── SETUP_GUIDE.md                     # Step-by-step setup instructions
├── PROJECT_OVERVIEW.md                # Detailed documentation
├── README.md                          # This file
└── ehr_audit.log                      # Generated audit trail
```

## 🎓 Educational Purpose

This project is designed for **educational demonstration only**. It simulates:

- OAuth 2.0 authentication flows
- FHIR API interactions
- HIPAA-compliant data handling
- Secure healthcare data exchange

### ⚠️ Important Notes

**This is NOT production-ready code.** For real-world deployment, you would need:

- Actual OAuth 2.0 server integration
- Hardware Security Module (HSM) or KMS for key management
- Real FHIR API endpoints
- Production database for audit logs
- Valid TLS certificates
- Business Associate Agreements (BAAs)
- Comprehensive security testing
- Legal compliance review

## 🧪 Testing

### Web Application Test Scenarios

1. **Full Transfer** - Select all data elements
2. **Minimal Transfer** - Demographics only
3. **Emergency Transfer** - Critical data (vitals + medications)
4. **System Reset** - Clear and restart

### Expected Results

- All 5 transfer steps complete successfully
- Patient data displays in organized cards
- Audit log shows all actions with timestamps
- Encrypted fields marked with badges

## 📚 Learn More

For detailed technical information, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### Resources

- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)
- [FHIR Specification](https://www.hl7.org/fhir/)
- [OAuth 2.0 Documentation](https://oauth.net/2/)

## 🤝 Contributing

This is an educational demonstration project. Feel free to:

- Study the code
- Modify for learning purposes
- Use as a reference for HIPAA concepts
- Extend with additional features

## 📄 License

This project is for educational purposes. See your organization's policies regarding healthcare data handling.

## 🙏 Acknowledgments

Built to demonstrate HIPAA compliance concepts and secure healthcare data exchange practices.

---

**Status**: ✅ Complete and Functional
**Version**: 1.0
**Last Updated**: 2025
