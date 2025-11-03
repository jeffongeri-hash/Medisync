"""
HIPAA-Compliant EHR Transfer System
====================================
This module provides secure, HIPAA-compliant transfer of Electronic Health Records (EHR)
between different healthcare systems (e.g., Epic, Cerner).

Key Features:
- OAuth 2.0 Authentication
- End-to-end encryption using Fernet
- Comprehensive audit logging
- Patient consent verification
- Data minimization principle
- Data integrity validation (SHA-256)
- Secure transmission with TLS simulation

Author: Medisync
Date: 2025
"""

import os
import json
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import base64


# Configure logging for HIPAA audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hipaa_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HIPAAComplianceError(Exception):
    """Custom exception for HIPAA compliance violations."""

    def __init__(self, message: str, violation_type: str = "UNKNOWN"):
        self.message = message
        self.violation_type = violation_type
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)

        # Log compliance violation
        logger.error(f"HIPAA COMPLIANCE VIOLATION: {violation_type} - {message}")


@dataclass
class PatientData:
    """Represents patient health record data."""
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    ssn: str  # Highly sensitive PHI
    medical_record_number: str
    diagnoses: List[str]
    medications: List[str]
    allergies: List[str]
    lab_results: List[Dict[str, Any]]
    visit_history: List[Dict[str, Any]]
    insurance_info: Dict[str, str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class TransferAuditLog:
    """Audit log entry for EHR transfer."""
    transfer_id: str
    timestamp: str
    source_system: str
    destination_system: str
    patient_id: str
    user_id: str
    action: str
    status: str
    data_elements: List[str]
    checksum: str
    consent_verified: bool
    encryption_used: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging."""
        return asdict(self)


class SecureEHRTransfer:
    """
    Main class for handling secure, HIPAA-compliant EHR transfers.

    This class implements all necessary security controls and compliance measures
    for transferring Protected Health Information (PHI) between EHR systems.
    """

    def __init__(self, source_system: str, destination_system: str):
        """
        Initialize the secure EHR transfer handler.

        Args:
            source_system: Name of the source EHR system (e.g., "Epic")
            destination_system: Name of the destination EHR system (e.g., "Cerner")
        """
        self.source_system = source_system
        self.destination_system = destination_system
        self.transfer_id = str(uuid.uuid4())
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.audit_logs: List[TransferAuditLog] = []

        logger.info(f"Initialized SecureEHRTransfer: {source_system} -> {destination_system}")
        logger.info(f"Transfer ID: {self.transfer_id}")

    def authenticate_oauth(self, client_id: str, client_secret: str,
                          token_endpoint: str) -> Dict[str, str]:
        """
        Authenticate with EHR system using OAuth 2.0 client credentials flow.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            token_endpoint: OAuth token endpoint URL

        Returns:
            Dictionary containing access token and metadata

        Raises:
            HIPAAComplianceError: If authentication fails
        """
        logger.info(f"Starting OAuth 2.0 authentication with {self.source_system}")

        try:
            # Simulate OAuth 2.0 client credentials flow
            # In production, this would make actual HTTP requests to the token endpoint

            # Validate inputs
            if not client_id or not client_secret:
                raise HIPAAComplianceError(
                    "Missing OAuth credentials",
                    violation_type="AUTHENTICATION_FAILURE"
                )

            # Simulate token generation
            access_token = base64.b64encode(
                f"{client_id}:{client_secret}:{datetime.utcnow().isoformat()}".encode()
            ).decode()

            token_data = {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "patient/*.read patient/*.write",
                "issued_at": datetime.utcnow().isoformat()
            }

            logger.info(f"OAuth authentication successful for {self.source_system}")

            # Audit log
            self._log_action("OAUTH_AUTHENTICATION", "SUCCESS", {
                "system": self.source_system,
                "scope": token_data["scope"]
            })

            return token_data

        except Exception as e:
            logger.error(f"OAuth authentication failed: {str(e)}")
            raise HIPAAComplianceError(
                f"Authentication failed: {str(e)}",
                violation_type="AUTHENTICATION_FAILURE"
            )

    def verify_patient_consent(self, patient_id: str,
                              consent_database: Dict[str, Dict]) -> bool:
        """
        Verify that patient has provided consent for data sharing.

        Args:
            patient_id: Unique patient identifier
            consent_database: Database of patient consent records

        Returns:
            True if consent is valid, False otherwise

        Raises:
            HIPAAComplianceError: If consent is not found or expired
        """
        logger.info(f"Verifying patient consent for patient {patient_id}")

        # Check if consent record exists
        if patient_id not in consent_database:
            raise HIPAAComplianceError(
                f"No consent record found for patient {patient_id}",
                violation_type="CONSENT_NOT_FOUND"
            )

        consent_record = consent_database[patient_id]

        # Verify consent is active
        if not consent_record.get("consent_given", False):
            raise HIPAAComplianceError(
                f"Patient {patient_id} has not provided consent",
                violation_type="CONSENT_DENIED"
            )

        # Check consent expiration
        consent_date = datetime.fromisoformat(consent_record.get("consent_date"))
        expiration_date = datetime.fromisoformat(consent_record.get("expiration_date"))

        if datetime.utcnow() > expiration_date:
            raise HIPAAComplianceError(
                f"Consent expired for patient {patient_id}",
                violation_type="CONSENT_EXPIRED"
            )

        # Verify specific purpose
        if self.destination_system not in consent_record.get("authorized_recipients", []):
            raise HIPAAComplianceError(
                f"Patient {patient_id} has not authorized data sharing with {self.destination_system}",
                violation_type="CONSENT_SCOPE_VIOLATION"
            )

        logger.info(f"Patient consent verified successfully for {patient_id}")

        # Audit log
        self._log_action("CONSENT_VERIFICATION", "SUCCESS", {
            "patient_id": patient_id,
            "consent_date": consent_record.get("consent_date"),
            "authorized_recipients": consent_record.get("authorized_recipients")
        })

        return True

    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt sensitive PHI using Fernet (symmetric encryption).

        Args:
            data: Dictionary containing patient data

        Returns:
            Encrypted data as bytes
        """
        logger.info("Encrypting sensitive PHI data")

        try:
            # Convert data to JSON string
            json_data = json.dumps(data)

            # Encrypt using Fernet
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())

            logger.info(f"Data encrypted successfully ({len(encrypted_data)} bytes)")

            # Audit log
            self._log_action("DATA_ENCRYPTION", "SUCCESS", {
                "encryption_algorithm": "Fernet (AES-128)",
                "data_size_bytes": len(encrypted_data)
            })

            return encrypted_data

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise HIPAAComplianceError(
                f"Data encryption failed: {str(e)}",
                violation_type="ENCRYPTION_FAILURE"
            )

    def decrypt_sensitive_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt encrypted PHI data.

        Args:
            encrypted_data: Encrypted data bytes

        Returns:
            Decrypted data as dictionary
        """
        logger.info("Decrypting PHI data")

        try:
            # Decrypt using Fernet
            decrypted_json = self.cipher_suite.decrypt(encrypted_data).decode()

            # Parse JSON
            data = json.loads(decrypted_json)

            logger.info("Data decrypted successfully")

            # Audit log
            self._log_action("DATA_DECRYPTION", "SUCCESS", {
                "decryption_algorithm": "Fernet (AES-128)"
            })

            return data

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise HIPAAComplianceError(
                f"Data decryption failed: {str(e)}",
                violation_type="DECRYPTION_FAILURE"
            )

    def retrieve_patient_data(self, patient_id: str, access_token: str) -> PatientData:
        """
        Retrieve patient data from source EHR system.

        Args:
            patient_id: Unique patient identifier
            access_token: OAuth access token

        Returns:
            PatientData object containing patient information
        """
        logger.info(f"Retrieving patient data for {patient_id} from {self.source_system}")

        try:
            # In production, this would make actual API calls to the EHR system
            # For demonstration, we'll create sample data

            sample_data = PatientData(
                patient_id=patient_id,
                first_name="John",
                last_name="Doe",
                date_of_birth="1980-05-15",
                ssn="123-45-6789",
                medical_record_number=f"MRN{patient_id}",
                diagnoses=[
                    "Hypertension (I10)",
                    "Type 2 Diabetes Mellitus (E11.9)"
                ],
                medications=[
                    "Lisinopril 10mg daily",
                    "Metformin 500mg twice daily"
                ],
                allergies=["Penicillin", "Sulfa drugs"],
                lab_results=[
                    {
                        "test": "HbA1c",
                        "value": "7.2",
                        "unit": "%",
                        "date": "2025-10-15",
                        "status": "final"
                    },
                    {
                        "test": "Blood Pressure",
                        "value": "135/85",
                        "unit": "mmHg",
                        "date": "2025-10-15",
                        "status": "final"
                    }
                ],
                visit_history=[
                    {
                        "date": "2025-10-15",
                        "type": "Office Visit",
                        "provider": "Dr. Smith",
                        "reason": "Follow-up for diabetes management"
                    }
                ],
                insurance_info={
                    "provider": "Blue Cross Blue Shield",
                    "policy_number": "BCBS123456",
                    "group_number": "GRP789"
                }
            )

            logger.info(f"Successfully retrieved data for patient {patient_id}")

            # Audit log
            self._log_action("DATA_RETRIEVAL", "SUCCESS", {
                "patient_id": patient_id,
                "source_system": self.source_system,
                "record_count": 1
            })

            return sample_data

        except Exception as e:
            logger.error(f"Data retrieval failed: {str(e)}")
            raise HIPAAComplianceError(
                f"Failed to retrieve patient data: {str(e)}",
                violation_type="DATA_RETRIEVAL_FAILURE"
            )

    def apply_data_minimization(self, patient_data: PatientData,
                               requested_elements: List[str]) -> Dict[str, Any]:
        """
        Apply data minimization principle - only transfer requested data elements.

        Args:
            patient_data: Complete patient data
            requested_elements: List of requested data fields

        Returns:
            Minimized data dictionary containing only requested elements
        """
        logger.info("Applying data minimization principle")

        full_data = patient_data.to_dict()
        minimized_data = {}

        # Always include patient identifier
        minimized_data["patient_id"] = full_data["patient_id"]

        # Add only requested elements
        for element in requested_elements:
            if element in full_data:
                minimized_data[element] = full_data[element]
            else:
                logger.warning(f"Requested element '{element}' not found in patient data")

        logger.info(f"Data minimization applied: {len(minimized_data)}/{len(full_data)} fields included")

        # Audit log
        self._log_action("DATA_MINIMIZATION", "SUCCESS", {
            "requested_elements": requested_elements,
            "included_fields": list(minimized_data.keys()),
            "total_fields": len(full_data),
            "minimized_fields": len(minimized_data)
        })

        return minimized_data

    def validate_data_integrity(self, data: Dict[str, Any]) -> str:
        """
        Create SHA-256 checksum for data integrity validation.

        Args:
            data: Data dictionary to validate

        Returns:
            SHA-256 checksum as hexadecimal string
        """
        logger.info("Generating data integrity checksum")

        try:
            # Convert data to consistent JSON string
            json_data = json.dumps(data, sort_keys=True)

            # Generate SHA-256 hash
            checksum = hashlib.sha256(json_data.encode()).hexdigest()

            logger.info(f"Data integrity checksum: {checksum}")

            # Audit log
            self._log_action("INTEGRITY_CHECK", "SUCCESS", {
                "checksum_algorithm": "SHA-256",
                "checksum": checksum
            })

            return checksum

        except Exception as e:
            logger.error(f"Integrity check failed: {str(e)}")
            raise HIPAAComplianceError(
                f"Data integrity validation failed: {str(e)}",
                violation_type="INTEGRITY_CHECK_FAILURE"
            )

    def verify_checksum(self, data: Dict[str, Any], expected_checksum: str) -> bool:
        """
        Verify data integrity by comparing checksums.

        Args:
            data: Data dictionary to verify
            expected_checksum: Expected SHA-256 checksum

        Returns:
            True if checksums match, raises exception otherwise
        """
        logger.info("Verifying data integrity checksum")

        actual_checksum = self.validate_data_integrity(data)

        if actual_checksum != expected_checksum:
            raise HIPAAComplianceError(
                f"Data integrity check failed: checksum mismatch",
                violation_type="INTEGRITY_VIOLATION"
            )

        logger.info("Data integrity verified successfully")
        return True

    def transmit_to_destination_ehr(self, encrypted_data: bytes,
                                   checksum: str,
                                   destination_endpoint: str,
                                   access_token: str) -> Dict[str, Any]:
        """
        Transmit encrypted data to destination EHR system with security headers.

        Args:
            encrypted_data: Encrypted patient data
            checksum: Data integrity checksum
            destination_endpoint: API endpoint of destination system
            access_token: OAuth access token for destination system

        Returns:
            Transmission response dictionary
        """
        logger.info(f"Transmitting data to {self.destination_system}")

        try:
            # Simulate HTTPS transmission with security headers
            # In production, this would use requests library with TLS/SSL

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/octet-stream",
                "X-Checksum": checksum,
                "X-Transfer-ID": self.transfer_id,
                "X-Encryption": "Fernet-AES128",
                "X-HIPAA-Compliant": "true",
                "Strict-Transport-Security": "max-age=31536000",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }

            # Simulate transmission
            response = {
                "status": "success",
                "transfer_id": self.transfer_id,
                "destination_system": self.destination_system,
                "received_at": datetime.utcnow().isoformat(),
                "data_size_bytes": len(encrypted_data),
                "checksum_verified": True,
                "message": "Data received and stored securely"
            }

            logger.info(f"Data transmitted successfully to {self.destination_system}")

            # Audit log
            self._log_action("DATA_TRANSMISSION", "SUCCESS", {
                "destination_system": self.destination_system,
                "endpoint": destination_endpoint,
                "data_size_bytes": len(encrypted_data),
                "transfer_id": self.transfer_id,
                "tls_version": "TLS 1.3 (simulated)"
            })

            return response

        except Exception as e:
            logger.error(f"Data transmission failed: {str(e)}")
            raise HIPAAComplianceError(
                f"Data transmission failed: {str(e)}",
                violation_type="TRANSMISSION_FAILURE"
            )

    def complete_transfer_audit(self, patient_id: str, user_id: str,
                               data_elements: List[str], checksum: str,
                               consent_verified: bool) -> TransferAuditLog:
        """
        Create comprehensive audit log entry for the entire transfer.

        Args:
            patient_id: Patient identifier
            user_id: User who initiated the transfer
            data_elements: List of data elements transferred
            checksum: Data integrity checksum
            consent_verified: Whether consent was verified

        Returns:
            TransferAuditLog object
        """
        logger.info("Creating comprehensive audit log")

        audit_entry = TransferAuditLog(
            transfer_id=self.transfer_id,
            timestamp=datetime.utcnow().isoformat(),
            source_system=self.source_system,
            destination_system=self.destination_system,
            patient_id=patient_id,
            user_id=user_id,
            action="EHR_TRANSFER_COMPLETE",
            status="SUCCESS",
            data_elements=data_elements,
            checksum=checksum,
            consent_verified=consent_verified,
            encryption_used=True
        )

        self.audit_logs.append(audit_entry)

        # Write to audit log file
        audit_file = f"logs/transfer_{self.transfer_id}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit_entry.to_dict(), f, indent=2)

        logger.info(f"Audit log saved to {audit_file}")
        logger.info(f"Transfer {self.transfer_id} completed successfully")

        return audit_entry

    def execute_secure_transfer(self, patient_id: str, user_id: str,
                               requested_elements: List[str],
                               consent_database: Dict[str, Dict],
                               source_credentials: Dict[str, str],
                               destination_credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute complete secure EHR transfer workflow.

        This is the main method that orchestrates the entire transfer process:
        1. OAuth authentication
        2. Patient consent verification
        3. Data retrieval
        4. Data minimization
        5. Encryption
        6. Integrity validation
        7. Secure transmission
        8. Audit logging

        Args:
            patient_id: Patient identifier
            user_id: User initiating the transfer
            requested_elements: List of data fields to transfer
            consent_database: Patient consent records
            source_credentials: OAuth credentials for source system
            destination_credentials: OAuth credentials for destination system

        Returns:
            Dictionary containing transfer results and metadata
        """
        logger.info("=" * 80)
        logger.info(f"STARTING SECURE EHR TRANSFER - Transfer ID: {self.transfer_id}")
        logger.info("=" * 80)

        try:
            # Step 1: Authenticate with source system
            logger.info("Step 1: Authenticating with source system")
            source_token = self.authenticate_oauth(
                source_credentials["client_id"],
                source_credentials["client_secret"],
                source_credentials["token_endpoint"]
            )

            # Step 2: Verify patient consent
            logger.info("Step 2: Verifying patient consent")
            self.verify_patient_consent(patient_id, consent_database)

            # Step 3: Retrieve patient data
            logger.info("Step 3: Retrieving patient data")
            patient_data = self.retrieve_patient_data(
                patient_id,
                source_token["access_token"]
            )

            # Step 4: Apply data minimization
            logger.info("Step 4: Applying data minimization")
            minimized_data = self.apply_data_minimization(
                patient_data,
                requested_elements
            )

            # Step 5: Generate integrity checksum
            logger.info("Step 5: Generating data integrity checksum")
            checksum = self.validate_data_integrity(minimized_data)

            # Step 6: Encrypt data
            logger.info("Step 6: Encrypting sensitive data")
            encrypted_data = self.encrypt_sensitive_data(minimized_data)

            # Step 7: Authenticate with destination system
            logger.info("Step 7: Authenticating with destination system")
            dest_token = self.authenticate_oauth(
                destination_credentials["client_id"],
                destination_credentials["client_secret"],
                destination_credentials["token_endpoint"]
            )

            # Step 8: Transmit to destination
            logger.info("Step 8: Transmitting data to destination")
            transmission_result = self.transmit_to_destination_ehr(
                encrypted_data,
                checksum,
                destination_credentials["endpoint"],
                dest_token["access_token"]
            )

            # Step 9: Complete audit trail
            logger.info("Step 9: Completing audit trail")
            audit_log = self.complete_transfer_audit(
                patient_id,
                user_id,
                requested_elements,
                checksum,
                consent_verified=True
            )

            # Compile results
            results = {
                "transfer_id": self.transfer_id,
                "status": "SUCCESS",
                "patient_id": patient_id,
                "source_system": self.source_system,
                "destination_system": self.destination_system,
                "data_elements_transferred": requested_elements,
                "checksum": checksum,
                "transmission_result": transmission_result,
                "audit_log": audit_log.to_dict(),
                "completed_at": datetime.utcnow().isoformat()
            }

            logger.info("=" * 80)
            logger.info("SECURE EHR TRANSFER COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)

            return results

        except HIPAAComplianceError as e:
            logger.error(f"HIPAA Compliance Error: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during transfer: {str(e)}")
            raise HIPAAComplianceError(
                f"Transfer failed: {str(e)}",
                violation_type="TRANSFER_FAILURE"
            )

    def _log_action(self, action: str, status: str, details: Dict[str, Any]):
        """Internal method to log actions for audit trail."""
        log_entry = {
            "transfer_id": self.transfer_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        logger.info(f"AUDIT: {json.dumps(log_entry)}")


def demonstrate_ehr_transfer():
    """
    Demonstration function showing complete EHR transfer workflow.
    """
    print("\n" + "=" * 80)
    print("HIPAA-COMPLIANT EHR TRANSFER SYSTEM - DEMONSTRATION")
    print("=" * 80 + "\n")

    # Sample consent database
    consent_database = {
        "PAT123456": {
            "consent_given": True,
            "consent_date": "2025-01-01T00:00:00",
            "expiration_date": "2026-01-01T00:00:00",
            "authorized_recipients": ["Cerner", "AllScripts", "Meditech"]
        }
    }

    # OAuth credentials (in production, these would be stored securely)
    source_credentials = {
        "client_id": "epic_client_12345",
        "client_secret": "epic_secret_xyz789",
        "token_endpoint": "https://epic-ehr.example.com/oauth/token"
    }

    destination_credentials = {
        "client_id": "cerner_client_67890",
        "client_secret": "cerner_secret_abc123",
        "token_endpoint": "https://cerner-ehr.example.com/oauth/token",
        "endpoint": "https://cerner-ehr.example.com/api/patient-data"
    }

    # Initialize secure transfer
    transfer = SecureEHRTransfer(
        source_system="Epic",
        destination_system="Cerner"
    )

    # Define requested data elements (minimum necessary)
    requested_elements = [
        "first_name",
        "last_name",
        "date_of_birth",
        "diagnoses",
        "medications",
        "allergies",
        "lab_results"
    ]

    # Execute transfer
    try:
        results = transfer.execute_secure_transfer(
            patient_id="PAT123456",
            user_id="Dr.Smith@hospital.org",
            requested_elements=requested_elements,
            consent_database=consent_database,
            source_credentials=source_credentials,
            destination_credentials=destination_credentials
        )

        print("\n" + "=" * 80)
        print("TRANSFER RESULTS")
        print("=" * 80)
        print(json.dumps(results, indent=2, default=str))

    except HIPAAComplianceError as e:
        print(f"\n❌ HIPAA Compliance Error: {e.message}")
        print(f"   Violation Type: {e.violation_type}")
        print(f"   Timestamp: {e.timestamp}")


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Run demonstration
    demonstrate_ehr_transfer()
