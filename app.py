"""
HIPAA-Compliant EHR Transfer System - Web Application
======================================================
Flask web application providing REST API for secure EHR transfers.

Endpoints:
- GET /: Main dashboard
- POST /api/transfer: Initiate EHR transfer
- GET /api/transfer/<transfer_id>: Get transfer status
- GET /api/audit-logs: Get audit logs
- POST /api/verify-consent: Verify patient consent

Author: Medisync
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.hipaa_compliant_ehr_transfer import (
    SecureEHRTransfer,
    HIPAAComplianceError
)

# Initialize Flask app
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Enable CORS with security headers
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# Sample data for demonstration
CONSENT_DATABASE = {
    "PAT123456": {
        "patient_name": "John Doe",
        "consent_given": True,
        "consent_date": "2025-01-01T00:00:00",
        "expiration_date": "2026-01-01T00:00:00",
        "authorized_recipients": ["Cerner", "AllScripts", "Meditech", "Epic"]
    },
    "PAT789012": {
        "patient_name": "Jane Smith",
        "consent_given": True,
        "consent_date": "2025-02-15T00:00:00",
        "expiration_date": "2026-02-15T00:00:00",
        "authorized_recipients": ["Epic", "Cerner"]
    },
    "PAT345678": {
        "patient_name": "Robert Johnson",
        "consent_given": False,
        "consent_date": "2024-06-01T00:00:00",
        "expiration_date": "2025-06-01T00:00:00",
        "authorized_recipients": []
    }
}

# Store active transfers (in production, use a database)
active_transfers = {}


@app.route('/')
def index():
    """Render main dashboard."""
    return render_template('index.html')


@app.route('/api/systems', methods=['GET'])
def get_ehr_systems():
    """Get list of available EHR systems."""
    systems = [
        {"id": "epic", "name": "Epic", "description": "Epic Systems EHR"},
        {"id": "cerner", "name": "Cerner", "description": "Oracle Cerner EHR"},
        {"id": "allscripts", "name": "AllScripts", "description": "AllScripts EHR"},
        {"id": "meditech", "name": "Meditech", "description": "Meditech EHR"},
        {"id": "athenahealth", "name": "athenahealth", "description": "athenahealth EHR"}
    ]
    return jsonify(systems)


@app.route('/api/data-elements', methods=['GET'])
def get_data_elements():
    """Get list of available data elements for transfer."""
    elements = [
        {"id": "first_name", "name": "First Name", "category": "Demographics"},
        {"id": "last_name", "name": "Last Name", "category": "Demographics"},
        {"id": "date_of_birth", "name": "Date of Birth", "category": "Demographics"},
        {"id": "ssn", "name": "Social Security Number", "category": "Demographics", "sensitive": True},
        {"id": "medical_record_number", "name": "Medical Record Number", "category": "Identifiers"},
        {"id": "diagnoses", "name": "Diagnoses", "category": "Clinical"},
        {"id": "medications", "name": "Medications", "category": "Clinical"},
        {"id": "allergies", "name": "Allergies", "category": "Clinical"},
        {"id": "lab_results", "name": "Lab Results", "category": "Clinical"},
        {"id": "visit_history", "name": "Visit History", "category": "Clinical"},
        {"id": "insurance_info", "name": "Insurance Information", "category": "Administrative"}
    ]
    return jsonify(elements)


@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get list of patients with consent status."""
    patients = []
    for patient_id, consent_info in CONSENT_DATABASE.items():
        patients.append({
            "patient_id": patient_id,
            "name": consent_info["patient_name"],
            "consent_given": consent_info["consent_given"],
            "consent_date": consent_info["consent_date"],
            "expiration_date": consent_info["expiration_date"],
            "authorized_recipients": consent_info["authorized_recipients"]
        })
    return jsonify(patients)


@app.route('/api/verify-consent', methods=['POST'])
def verify_consent():
    """Verify patient consent for data transfer."""
    data = request.get_json()

    patient_id = data.get('patient_id')
    destination_system = data.get('destination_system')

    if not patient_id or not destination_system:
        return jsonify({
            "error": "Missing required fields"
        }), 400

    # Check consent
    if patient_id not in CONSENT_DATABASE:
        return jsonify({
            "consent_valid": False,
            "reason": "No consent record found",
            "violation_type": "CONSENT_NOT_FOUND"
        }), 404

    consent_record = CONSENT_DATABASE[patient_id]

    # Check if consent is given
    if not consent_record["consent_given"]:
        return jsonify({
            "consent_valid": False,
            "reason": "Patient has not provided consent",
            "violation_type": "CONSENT_DENIED"
        }), 403

    # Check expiration
    expiration_date = datetime.fromisoformat(consent_record["expiration_date"])
    if datetime.utcnow() > expiration_date:
        return jsonify({
            "consent_valid": False,
            "reason": "Consent has expired",
            "violation_type": "CONSENT_EXPIRED"
        }), 403

    # Check authorized recipients
    if destination_system not in consent_record["authorized_recipients"]:
        return jsonify({
            "consent_valid": False,
            "reason": f"Patient has not authorized {destination_system}",
            "violation_type": "CONSENT_SCOPE_VIOLATION"
        }), 403

    return jsonify({
        "consent_valid": True,
        "patient_name": consent_record["patient_name"],
        "consent_date": consent_record["consent_date"],
        "expiration_date": consent_record["expiration_date"]
    })


@app.route('/api/transfer', methods=['POST'])
def initiate_transfer():
    """Initiate a secure EHR transfer."""
    data = request.get_json()

    # Validate required fields
    required_fields = ['patient_id', 'source_system', 'destination_system',
                      'user_id', 'requested_elements']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    try:
        # Create transfer instance
        transfer = SecureEHRTransfer(
            source_system=data['source_system'],
            destination_system=data['destination_system']
        )

        # Prepare credentials (in production, fetch from secure storage)
        source_credentials = {
            "client_id": f"{data['source_system'].lower()}_client_id",
            "client_secret": f"{data['source_system'].lower()}_secret",
            "token_endpoint": f"https://{data['source_system'].lower()}.example.com/oauth/token"
        }

        destination_credentials = {
            "client_id": f"{data['destination_system'].lower()}_client_id",
            "client_secret": f"{data['destination_system'].lower()}_secret",
            "token_endpoint": f"https://{data['destination_system'].lower()}.example.com/oauth/token",
            "endpoint": f"https://{data['destination_system'].lower()}.example.com/api/patient-data"
        }

        # Execute transfer
        results = transfer.execute_secure_transfer(
            patient_id=data['patient_id'],
            user_id=data['user_id'],
            requested_elements=data['requested_elements'],
            consent_database=CONSENT_DATABASE,
            source_credentials=source_credentials,
            destination_credentials=destination_credentials
        )

        # Store transfer info
        active_transfers[results['transfer_id']] = results

        return jsonify({
            "success": True,
            "transfer_id": results['transfer_id'],
            "status": results['status'],
            "message": "Transfer completed successfully",
            "results": results
        })

    except HIPAAComplianceError as e:
        app.logger.error(f"HIPAA Compliance Error: {e.message}")
        return jsonify({
            "success": False,
            "error": e.message,
            "violation_type": e.violation_type,
            "timestamp": e.timestamp
        }), 400

    except Exception as e:
        app.logger.error(f"Transfer error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/transfer/<transfer_id>', methods=['GET'])
def get_transfer_status(transfer_id):
    """Get status of a specific transfer."""
    if transfer_id not in active_transfers:
        return jsonify({
            "error": "Transfer not found"
        }), 404

    return jsonify(active_transfers[transfer_id])


@app.route('/api/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs from the logs directory."""
    logs_dir = 'logs'

    if not os.path.exists(logs_dir):
        return jsonify([])

    audit_logs = []

    # Read all transfer log files
    for filename in os.listdir(logs_dir):
        if filename.startswith('transfer_') and filename.endswith('.json'):
            filepath = os.path.join(logs_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    log_data = json.load(f)
                    audit_logs.append(log_data)
            except Exception as e:
                app.logger.error(f"Error reading log file {filename}: {str(e)}")

    # Sort by timestamp (newest first)
    audit_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return jsonify(audit_logs)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics."""
    total_transfers = len(active_transfers)
    successful_transfers = sum(1 for t in active_transfers.values()
                              if t.get('status') == 'SUCCESS')

    stats = {
        "total_transfers": total_transfers,
        "successful_transfers": successful_transfers,
        "failed_transfers": total_transfers - successful_transfers,
        "total_patients": len(CONSENT_DATABASE),
        "patients_with_consent": sum(1 for c in CONSENT_DATABASE.values()
                                    if c.get('consent_given')),
        "ehr_systems_connected": 5
    }

    return jsonify(stats)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "HIPAA-Compliant EHR Transfer System"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Resource not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    # Run Flask app
    print("\n" + "=" * 80)
    print("HIPAA-COMPLIANT EHR TRANSFER SYSTEM")
    print("=" * 80)
    print("\nStarting web server...")
    print("Dashboard: http://localhost:5000")
    print("API Documentation: http://localhost:5000/api/")
    print("\n" + "=" * 80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
