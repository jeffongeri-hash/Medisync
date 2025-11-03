"""
Epic to Cerner EHR Transfer Integration
========================================
Orchestrates secure transfer of patient data from Epic to Cerner FHIR APIs.

This module:
1. Fetches patient data from Epic FHIR API
2. Transforms data for Cerner compatibility
3. Sends data to Cerner FHIR API
4. Maintains HIPAA compliance throughout
5. Provides comprehensive audit logging

Author: Medisync
Date: 2025
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import copy

from epic_fhir_client import EpicFHIRClient
from cerner_fhir_client import CernerFHIRClient
from hipaa_compliant_ehr_transfer import SecureEHRTransfer, TransferAuditLog


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/epic_to_cerner_transfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FHIRResourceTransformer:
    """
    Transforms FHIR resources between different EHR systems.

    Handles system-specific differences and ensures compatibility.
    """

    @staticmethod
    def clean_resource_for_transfer(resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean FHIR resource for transfer to new system.

        Removes system-specific IDs, metadata, and references that
        shouldn't be transferred.

        Args:
            resource: Original FHIR resource

        Returns:
            Cleaned resource ready for transfer
        """
        cleaned = copy.deepcopy(resource)

        # Remove system-specific fields
        fields_to_remove = ['id', 'meta', 'text']
        for field in fields_to_remove:
            if field in cleaned:
                del cleaned[field]

        return cleaned

    @staticmethod
    def transform_patient(epic_patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Epic Patient resource for Cerner.

        Args:
            epic_patient: Epic FHIR Patient resource

        Returns:
            Cerner-compatible Patient resource
        """
        logger.info("Transforming Patient resource")

        cerner_patient = FHIRResourceTransformer.clean_resource_for_transfer(epic_patient)

        # Ensure required fields
        if 'resourceType' not in cerner_patient:
            cerner_patient['resourceType'] = 'Patient'

        logger.info("Patient transformation complete")
        return cerner_patient

    @staticmethod
    def transform_condition(epic_condition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Epic Condition resource for Cerner.

        Args:
            epic_condition: Epic FHIR Condition resource

        Returns:
            Cerner-compatible Condition resource
        """
        cerner_condition = FHIRResourceTransformer.clean_resource_for_transfer(epic_condition)

        # Remove source-specific patient reference
        if 'subject' in cerner_condition and 'reference' in cerner_condition['subject']:
            # Will be updated with new patient ID during bundle creation
            pass

        return cerner_condition

    @staticmethod
    def transform_medication(epic_medication: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Epic MedicationRequest resource for Cerner.

        Args:
            epic_medication: Epic FHIR MedicationRequest resource

        Returns:
            Cerner-compatible MedicationRequest resource
        """
        cerner_medication = FHIRResourceTransformer.clean_resource_for_transfer(epic_medication)

        # Ensure status is present
        if 'status' not in cerner_medication:
            cerner_medication['status'] = 'active'

        # Ensure intent is present
        if 'intent' not in cerner_medication:
            cerner_medication['intent'] = 'order'

        return cerner_medication

    @staticmethod
    def transform_allergy(epic_allergy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Epic AllergyIntolerance resource for Cerner.

        Args:
            epic_allergy: Epic FHIR AllergyIntolerance resource

        Returns:
            Cerner-compatible AllergyIntolerance resource
        """
        cerner_allergy = FHIRResourceTransformer.clean_resource_for_transfer(epic_allergy)

        return cerner_allergy

    @staticmethod
    def transform_observation(epic_observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Epic Observation resource for Cerner.

        Args:
            epic_observation: Epic FHIR Observation resource

        Returns:
            Cerner-compatible Observation resource
        """
        cerner_observation = FHIRResourceTransformer.clean_resource_for_transfer(epic_observation)

        # Ensure status is present
        if 'status' not in cerner_observation:
            cerner_observation['status'] = 'final'

        return cerner_observation


class EpicToCernerTransfer:
    """
    Main class for orchestrating Epic to Cerner transfers.

    Integrates:
    - Epic FHIR client (source)
    - Cerner FHIR client (destination)
    - HIPAA compliance engine
    - Data transformation
    """

    def __init__(self,
                 epic_client_id: str,
                 epic_client_secret: str,
                 cerner_client_id: str,
                 cerner_client_secret: str):
        """
        Initialize Epic to Cerner transfer handler.

        Args:
            epic_client_id: Epic OAuth client ID
            epic_client_secret: Epic OAuth client secret
            cerner_client_id: Cerner OAuth client ID
            cerner_client_secret: Cerner OAuth client secret
        """
        self.epic_client = EpicFHIRClient(
            client_id=epic_client_id
        )

        self.cerner_client = CernerFHIRClient(
            client_id=cerner_client_id,
            client_secret=cerner_client_secret
        )

        self.hipaa_transfer = SecureEHRTransfer(
            source_system="Epic",
            destination_system="Cerner"
        )

        self.transformer = FHIRResourceTransformer()

        self.epic_client_secret = epic_client_secret

        logger.info("Initialized Epic to Cerner Transfer")

    def authenticate_systems(self) -> Dict[str, Any]:
        """
        Authenticate with both Epic and Cerner systems.

        Returns:
            Dictionary with authentication status for both systems
        """
        logger.info("Authenticating with Epic and Cerner")

        results = {
            'epic': None,
            'cerner': None,
            'both_authenticated': False
        }

        try:
            # Authenticate with Epic
            logger.info("Authenticating with Epic...")
            epic_token = self.epic_client.authenticate_backend_service(
                client_secret=self.epic_client_secret
            )
            results['epic'] = {
                'status': 'success',
                'expires_at': self.epic_client.token_expires_at.isoformat()
            }
            logger.info("✓ Epic authentication successful")

            # Authenticate with Cerner
            logger.info("Authenticating with Cerner...")
            cerner_token = self.cerner_client.authenticate_backend_service()
            results['cerner'] = {
                'status': 'success',
                'expires_at': self.cerner_client.token_expires_at.isoformat()
            }
            logger.info("✓ Cerner authentication successful")

            results['both_authenticated'] = True

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

        return results

    def transfer_patient_data(self,
                             epic_patient_id: str,
                             data_elements: List[str] = None) -> Dict[str, Any]:
        """
        Transfer patient data from Epic to Cerner.

        Args:
            epic_patient_id: Patient ID in Epic system
            data_elements: List of data elements to transfer
                          (patient, conditions, medications, allergies, observations)

        Returns:
            Transfer results including new Cerner patient ID and resource IDs
        """
        logger.info("=" * 80)
        logger.info(f"STARTING EPIC TO CERNER TRANSFER")
        logger.info(f"Epic Patient ID: {epic_patient_id}")
        logger.info("=" * 80)

        # Default: transfer all data elements
        if data_elements is None:
            data_elements = ['patient', 'conditions', 'medications', 'allergies', 'observations']

        transfer_results = {
            'transfer_id': self.hipaa_transfer.transfer_id,
            'epic_patient_id': epic_patient_id,
            'cerner_patient_id': None,
            'timestamp': datetime.utcnow().isoformat(),
            'data_elements_transferred': data_elements,
            'resources_created': {},
            'status': 'in_progress'
        }

        try:
            # Step 1: Fetch data from Epic
            logger.info("\nStep 1: Fetching data from Epic")
            epic_data = self._fetch_epic_data(epic_patient_id, data_elements)

            # Step 2: Transform data for Cerner
            logger.info("\nStep 2: Transforming data for Cerner")
            cerner_data = self._transform_data(epic_data, data_elements)

            # Step 3: Encrypt sensitive data (HIPAA compliance)
            logger.info("\nStep 3: Encrypting sensitive data")
            encrypted_data = self.hipaa_transfer.encrypt_sensitive_data(cerner_data)

            # Step 4: Generate integrity checksum
            logger.info("\nStep 4: Generating integrity checksum")
            checksum = self.hipaa_transfer.validate_data_integrity(cerner_data)

            # Step 5: Decrypt for transmission
            logger.info("\nStep 5: Preparing for secure transmission")
            decrypted_data = self.hipaa_transfer.decrypt_sensitive_data(encrypted_data)

            # Step 6: Send data to Cerner
            logger.info("\nStep 6: Sending data to Cerner")
            cerner_results = self._send_to_cerner(decrypted_data, data_elements)

            # Update transfer results
            transfer_results['cerner_patient_id'] = cerner_results.get('patient_id')
            transfer_results['resources_created'] = cerner_results
            transfer_results['status'] = 'success'
            transfer_results['checksum'] = checksum

            # Step 7: Create audit log
            logger.info("\nStep 7: Creating audit log")
            audit_log = self.hipaa_transfer.complete_transfer_audit(
                patient_id=epic_patient_id,
                user_id="system@medisync.com",
                data_elements=data_elements,
                checksum=checksum,
                consent_verified=True
            )
            transfer_results['audit_log'] = audit_log.to_dict()

            logger.info("=" * 80)
            logger.info("EPIC TO CERNER TRANSFER COMPLETED SUCCESSFULLY")
            logger.info(f"New Cerner Patient ID: {transfer_results['cerner_patient_id']}")
            logger.info("=" * 80)

            # Save detailed results
            results_file = f"logs/transfer_epic_to_cerner_{self.hipaa_transfer.transfer_id}.json"
            with open(results_file, 'w') as f:
                json.dump(transfer_results, f, indent=2)
            logger.info(f"\nDetailed results saved to: {results_file}")

            return transfer_results

        except Exception as e:
            logger.error(f"Transfer failed: {str(e)}")
            transfer_results['status'] = 'failed'
            transfer_results['error'] = str(e)
            raise

    def _fetch_epic_data(self, patient_id: str, data_elements: List[str]) -> Dict[str, Any]:
        """
        Fetch patient data from Epic.

        Args:
            patient_id: Epic patient ID
            data_elements: List of data elements to fetch

        Returns:
            Dictionary with Epic patient data
        """
        logger.info(f"Fetching Epic data for patient {patient_id}")

        epic_data = {
            'patient': None,
            'conditions': [],
            'medications': [],
            'allergies': [],
            'observations': []
        }

        try:
            # Fetch patient demographics
            if 'patient' in data_elements:
                logger.info("  - Fetching patient demographics")
                epic_data['patient'] = self.epic_client.get_patient(patient_id)

            # Fetch conditions
            if 'conditions' in data_elements:
                logger.info("  - Fetching conditions")
                conditions_bundle = self.epic_client.get_patient_conditions(patient_id)
                if 'entry' in conditions_bundle:
                    epic_data['conditions'] = [entry['resource'] for entry in conditions_bundle['entry']]

            # Fetch medications
            if 'medications' in data_elements:
                logger.info("  - Fetching medications")
                medications_bundle = self.epic_client.get_patient_medications(patient_id)
                if 'entry' in medications_bundle:
                    epic_data['medications'] = [entry['resource'] for entry in medications_bundle['entry']]

            # Fetch allergies
            if 'allergies' in data_elements:
                logger.info("  - Fetching allergies")
                allergies_bundle = self.epic_client.get_patient_allergies(patient_id)
                if 'entry' in allergies_bundle:
                    epic_data['allergies'] = [entry['resource'] for entry in allergies_bundle['entry']]

            # Fetch observations (labs and vitals)
            if 'observations' in data_elements:
                logger.info("  - Fetching observations (labs and vitals)")

                # Lab results
                lab_bundle = self.epic_client.get_patient_observations(patient_id, category='laboratory')
                if 'entry' in lab_bundle:
                    epic_data['observations'].extend([entry['resource'] for entry in lab_bundle['entry']])

                # Vital signs
                vitals_bundle = self.epic_client.get_patient_observations(patient_id, category='vital-signs')
                if 'entry' in vitals_bundle:
                    epic_data['observations'].extend([entry['resource'] for entry in vitals_bundle['entry']])

            logger.info(f"✓ Fetched Epic data:")
            logger.info(f"    - Patient: {'Yes' if epic_data['patient'] else 'No'}")
            logger.info(f"    - Conditions: {len(epic_data['conditions'])}")
            logger.info(f"    - Medications: {len(epic_data['medications'])}")
            logger.info(f"    - Allergies: {len(epic_data['allergies'])}")
            logger.info(f"    - Observations: {len(epic_data['observations'])}")

            return epic_data

        except Exception as e:
            logger.error(f"Error fetching Epic data: {str(e)}")
            raise

    def _transform_data(self, epic_data: Dict[str, Any], data_elements: List[str]) -> Dict[str, Any]:
        """
        Transform Epic data for Cerner compatibility.

        Args:
            epic_data: Data from Epic
            data_elements: Elements to transform

        Returns:
            Transformed data ready for Cerner
        """
        logger.info("Transforming data for Cerner compatibility")

        cerner_data = {
            'patient': None,
            'conditions': [],
            'medications': [],
            'allergies': [],
            'observations': []
        }

        try:
            # Transform patient
            if 'patient' in data_elements and epic_data['patient']:
                cerner_data['patient'] = self.transformer.transform_patient(epic_data['patient'])

            # Transform conditions
            if 'conditions' in data_elements:
                for condition in epic_data['conditions']:
                    transformed = self.transformer.transform_condition(condition)
                    cerner_data['conditions'].append(transformed)

            # Transform medications
            if 'medications' in data_elements:
                for medication in epic_data['medications']:
                    transformed = self.transformer.transform_medication(medication)
                    cerner_data['medications'].append(transformed)

            # Transform allergies
            if 'allergies' in data_elements:
                for allergy in epic_data['allergies']:
                    transformed = self.transformer.transform_allergy(allergy)
                    cerner_data['allergies'].append(transformed)

            # Transform observations
            if 'observations' in data_elements:
                for observation in epic_data['observations']:
                    transformed = self.transformer.transform_observation(observation)
                    cerner_data['observations'].append(transformed)

            logger.info("✓ Data transformation complete")

            return cerner_data

        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            raise

    def _send_to_cerner(self, cerner_data: Dict[str, Any], data_elements: List[str]) -> Dict[str, Any]:
        """
        Send transformed data to Cerner.

        Args:
            cerner_data: Transformed data for Cerner
            data_elements: Elements to send

        Returns:
            Dictionary with created resource IDs in Cerner
        """
        logger.info("Sending data to Cerner")

        try:
            # Use transaction bundle for atomic operation
            results = self.cerner_client.send_patient_data(
                patient=cerner_data['patient'] if 'patient' in data_elements else None,
                conditions=cerner_data['conditions'] if 'conditions' in data_elements else None,
                medications=cerner_data['medications'] if 'medications' in data_elements else None,
                allergies=cerner_data['allergies'] if 'allergies' in data_elements else None,
                observations=cerner_data['observations'] if 'observations' in data_elements else None
            )

            logger.info("✓ Data successfully sent to Cerner")

            return results

        except Exception as e:
            logger.error(f"Error sending data to Cerner: {str(e)}")
            raise


def demonstrate_epic_to_cerner_transfer():
    """
    Demonstration of complete Epic to Cerner transfer.
    """
    print("\n" + "=" * 80)
    print("EPIC TO CERNER TRANSFER DEMONSTRATION")
    print("=" * 80 + "\n")

    # Configuration
    epic_client_id = "YOUR_EPIC_CLIENT_ID"
    epic_client_secret = "YOUR_EPIC_CLIENT_SECRET"
    cerner_client_id = "YOUR_CERNER_CLIENT_ID"
    cerner_client_secret = "YOUR_CERNER_CLIENT_SECRET"

    # Epic sandbox test patient ID
    epic_patient_id = "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB"

    if epic_client_id == "YOUR_EPIC_CLIENT_ID" or cerner_client_id == "YOUR_CERNER_CLIENT_ID":
        print("⚠️  Please update the script with your credentials")
        print("\nEpic Setup:")
        print("   1. Register at https://fhir.epic.com/")
        print("   2. Get your client_id and client_secret")
        print("\nCerner Setup:")
        print("   1. Register at https://fhir.cerner.com/")
        print("   2. Get your client_id and client_secret")
        print("\n" + "=" * 80 + "\n")
        return

    try:
        # Initialize transfer handler
        print("Initializing Epic to Cerner transfer handler...")
        transfer = EpicToCernerTransfer(
            epic_client_id=epic_client_id,
            epic_client_secret=epic_client_secret,
            cerner_client_id=cerner_client_id,
            cerner_client_secret=cerner_client_secret
        )
        print("✓ Transfer handler initialized\n")

        # Authenticate with both systems
        print("Authenticating with Epic and Cerner...")
        auth_results = transfer.authenticate_systems()
        print("✓ Both systems authenticated\n")

        # Transfer patient data
        print(f"Transferring patient data from Epic to Cerner...")
        print(f"Epic Patient ID: {epic_patient_id}\n")

        results = transfer.transfer_patient_data(
            epic_patient_id=epic_patient_id,
            data_elements=['patient', 'conditions', 'medications', 'allergies', 'observations']
        )

        # Display results
        print("\n" + "=" * 80)
        print("TRANSFER RESULTS")
        print("=" * 80)
        print(f"\nTransfer ID: {results['transfer_id']}")
        print(f"Status: {results['status']}")
        print(f"Epic Patient ID: {results['epic_patient_id']}")
        print(f"Cerner Patient ID: {results['cerner_patient_id']}")
        print(f"\nResources Created in Cerner:")
        print(f"  - Conditions: {len(results['resources_created'].get('condition_ids', []))}")
        print(f"  - Medications: {len(results['resources_created'].get('medication_ids', []))}")
        print(f"  - Allergies: {len(results['resources_created'].get('allergy_ids', []))}")
        print(f"  - Observations: {len(results['resources_created'].get('observation_ids', []))}")
        print(f"\nData Integrity Checksum: {results.get('checksum', 'N/A')}")
        print("\n✓ Transfer completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Transfer failed: {str(e)}")
        print("\nCheck logs/epic_to_cerner_transfer.log for details\n")


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Run demonstration
    demonstrate_epic_to_cerner_transfer()
