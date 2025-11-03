"""
Epic FHIR Client for EHR Data Retrieval
========================================
Client for fetching patient data from Epic's FHIR API (Sandbox & Production).

Epic FHIR Sandbox: https://fhir.epic.com/
This implementation supports Epic's OAuth 2.0 flow and FHIR R4 resources.

Author: Medisync
Date: 2025
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import base64


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/epic_fhir.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EpicFHIRClient:
    """
    Client for interacting with Epic's FHIR API.

    Supports:
    - OAuth 2.0 authentication (Backend Service / Client Credentials)
    - Patient data retrieval
    - Observation, Condition, MedicationRequest, AllergyIntolerance resources
    - FHIR R4 specification
    """

    # Epic Sandbox endpoints
    EPIC_SANDBOX_FHIR_BASE = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
    EPIC_SANDBOX_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"

    def __init__(self,
                 client_id: str,
                 private_key_path: Optional[str] = None,
                 fhir_base_url: Optional[str] = None,
                 token_url: Optional[str] = None):
        """
        Initialize Epic FHIR client.

        Args:
            client_id: OAuth client ID from Epic
            private_key_path: Path to private key file (for JWT authentication)
            fhir_base_url: FHIR base URL (defaults to sandbox)
            token_url: OAuth token endpoint (defaults to sandbox)
        """
        self.client_id = client_id
        self.private_key_path = private_key_path
        self.fhir_base_url = fhir_base_url or self.EPIC_SANDBOX_FHIR_BASE
        self.token_url = token_url or self.EPIC_SANDBOX_TOKEN_URL
        self.access_token = None
        self.token_expires_at = None

        logger.info(f"Initialized Epic FHIR Client")
        logger.info(f"FHIR Base URL: {self.fhir_base_url}")

    def authenticate_backend_service(self, client_secret: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate using Backend Service (client credentials flow).

        For Epic sandbox, you can use client credentials flow with client_id and client_secret.
        For production, you'll need to use JWT-based authentication.

        Args:
            client_secret: OAuth client secret (for sandbox testing)

        Returns:
            Token response dictionary
        """
        logger.info("Authenticating with Epic FHIR API")

        try:
            # For Epic sandbox testing with client credentials
            if client_secret:
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': client_secret
                }
            else:
                # For production: Create JWT assertion
                # This requires creating a signed JWT with your private key
                logger.error("JWT-based auth not yet implemented. Use client_secret for sandbox.")
                raise NotImplementedError("JWT authentication requires private key setup")

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Authentication failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Authentication failed: {response.text}")

            token_data = response.json()
            self.access_token = token_data['access_token']

            # Calculate token expiration
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Successfully authenticated with Epic FHIR API")
            logger.info(f"Token expires at: {self.token_expires_at}")

            return token_data

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for FHIR API requests."""
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate_backend_service() first.")

        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            logger.warning("Access token expired. Need to re-authenticate.")
            raise Exception("Access token expired")

        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }

    def search_patient(self,
                      identifier: Optional[str] = None,
                      family: Optional[str] = None,
                      given: Optional[str] = None,
                      birthdate: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for patients using FHIR Patient resource.

        Args:
            identifier: Patient identifier (e.g., MRN)
            family: Family name
            given: Given name
            birthdate: Birth date (YYYY-MM-DD)

        Returns:
            FHIR Bundle with Patient resources
        """
        logger.info("Searching for patients")

        params = {}
        if identifier:
            params['identifier'] = identifier
        if family:
            params['family'] = family
        if given:
            params['given'] = given
        if birthdate:
            params['birthdate'] = birthdate

        url = f"{self.fhir_base_url}/Patient"
        if params:
            url += f"?{urlencode(params)}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Patient search failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Patient search failed: {response.text}")

            bundle = response.json()
            patient_count = bundle.get('total', 0)
            logger.info(f"Found {patient_count} patients")

            return bundle

        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            raise

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient resource by ID.

        Args:
            patient_id: FHIR Patient ID

        Returns:
            Patient resource
        """
        logger.info(f"Fetching patient: {patient_id}")

        url = f"{self.fhir_base_url}/Patient/{patient_id}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Get patient failed: {response.status_code}")
                raise Exception(f"Get patient failed: {response.text}")

            patient = response.json()
            logger.info(f"Successfully retrieved patient {patient_id}")

            return patient

        except Exception as e:
            logger.error(f"Error getting patient: {str(e)}")
            raise

    def get_patient_observations(self,
                                patient_id: str,
                                category: Optional[str] = None,
                                code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get observations (lab results, vitals) for a patient.

        Args:
            patient_id: FHIR Patient ID
            category: Observation category (e.g., 'laboratory', 'vital-signs')
            code: LOINC code for specific observation

        Returns:
            FHIR Bundle with Observation resources
        """
        logger.info(f"Fetching observations for patient {patient_id}")

        params = {'patient': patient_id}
        if category:
            params['category'] = category
        if code:
            params['code'] = code

        url = f"{self.fhir_base_url}/Observation?{urlencode(params)}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Get observations failed: {response.status_code}")
                raise Exception(f"Get observations failed: {response.text}")

            bundle = response.json()
            obs_count = bundle.get('total', 0)
            logger.info(f"Found {obs_count} observations")

            return bundle

        except Exception as e:
            logger.error(f"Error getting observations: {str(e)}")
            raise

    def get_patient_conditions(self, patient_id: str) -> Dict[str, Any]:
        """
        Get conditions (diagnoses) for a patient.

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Bundle with Condition resources
        """
        logger.info(f"Fetching conditions for patient {patient_id}")

        url = f"{self.fhir_base_url}/Condition?patient={patient_id}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Get conditions failed: {response.status_code}")
                raise Exception(f"Get conditions failed: {response.text}")

            bundle = response.json()
            condition_count = bundle.get('total', 0)
            logger.info(f"Found {condition_count} conditions")

            return bundle

        except Exception as e:
            logger.error(f"Error getting conditions: {str(e)}")
            raise

    def get_patient_medications(self, patient_id: str) -> Dict[str, Any]:
        """
        Get medication requests for a patient.

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Bundle with MedicationRequest resources
        """
        logger.info(f"Fetching medications for patient {patient_id}")

        url = f"{self.fhir_base_url}/MedicationRequest?patient={patient_id}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Get medications failed: {response.status_code}")
                raise Exception(f"Get medications failed: {response.text}")

            bundle = response.json()
            med_count = bundle.get('total', 0)
            logger.info(f"Found {med_count} medications")

            return bundle

        except Exception as e:
            logger.error(f"Error getting medications: {str(e)}")
            raise

    def get_patient_allergies(self, patient_id: str) -> Dict[str, Any]:
        """
        Get allergy intolerances for a patient.

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Bundle with AllergyIntolerance resources
        """
        logger.info(f"Fetching allergies for patient {patient_id}")

        url = f"{self.fhir_base_url}/AllergyIntolerance?patient={patient_id}"

        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Get allergies failed: {response.status_code}")
                raise Exception(f"Get allergies failed: {response.text}")

            bundle = response.json()
            allergy_count = bundle.get('total', 0)
            logger.info(f"Found {allergy_count} allergies")

            return bundle

        except Exception as e:
            logger.error(f"Error getting allergies: {str(e)}")
            raise

    def get_comprehensive_patient_record(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient record including all clinical data.

        Args:
            patient_id: FHIR Patient ID

        Returns:
            Dictionary with all patient data organized by resource type
        """
        logger.info(f"Fetching comprehensive record for patient {patient_id}")

        try:
            record = {
                'patient_id': patient_id,
                'retrieved_at': datetime.now().isoformat(),
                'patient': None,
                'conditions': [],
                'medications': [],
                'allergies': [],
                'observations': {
                    'laboratory': [],
                    'vital_signs': []
                }
            }

            # Get patient demographics
            record['patient'] = self.get_patient(patient_id)

            # Get conditions
            conditions_bundle = self.get_patient_conditions(patient_id)
            if 'entry' in conditions_bundle:
                record['conditions'] = [entry['resource'] for entry in conditions_bundle['entry']]

            # Get medications
            medications_bundle = self.get_patient_medications(patient_id)
            if 'entry' in medications_bundle:
                record['medications'] = [entry['resource'] for entry in medications_bundle['entry']]

            # Get allergies
            allergies_bundle = self.get_patient_allergies(patient_id)
            if 'entry' in allergies_bundle:
                record['allergies'] = [entry['resource'] for entry in allergies_bundle['entry']]

            # Get lab results
            lab_bundle = self.get_patient_observations(patient_id, category='laboratory')
            if 'entry' in lab_bundle:
                record['observations']['laboratory'] = [entry['resource'] for entry in lab_bundle['entry']]

            # Get vital signs
            vitals_bundle = self.get_patient_observations(patient_id, category='vital-signs')
            if 'entry' in vitals_bundle:
                record['observations']['vital_signs'] = [entry['resource'] for entry in vitals_bundle['entry']]

            logger.info(f"Successfully retrieved comprehensive record for patient {patient_id}")
            logger.info(f"  - Conditions: {len(record['conditions'])}")
            logger.info(f"  - Medications: {len(record['medications'])}")
            logger.info(f"  - Allergies: {len(record['allergies'])}")
            logger.info(f"  - Lab Results: {len(record['observations']['laboratory'])}")
            logger.info(f"  - Vital Signs: {len(record['observations']['vital_signs'])}")

            return record

        except Exception as e:
            logger.error(f"Error getting comprehensive record: {str(e)}")
            raise


def demonstrate_epic_fhir():
    """
    Demonstration of Epic FHIR client usage with sandbox.

    To use Epic sandbox:
    1. Register at https://fhir.epic.com/
    2. Get your client_id
    3. Use test patient IDs from Epic sandbox
    """
    print("\n" + "=" * 80)
    print("EPIC FHIR CLIENT DEMONSTRATION")
    print("=" * 80 + "\n")

    # Epic sandbox test patient IDs
    # These are publicly available test patients from Epic's sandbox
    TEST_PATIENT_IDS = [
        "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB",  # Derrick Lin
        "eq081-VQEgP8drUUqCWzHfw3",  # Camila Lopez
    ]

    # Initialize client (you need to replace with your actual client_id)
    print("Initializing Epic FHIR Client...")
    print("Note: You need to register at https://fhir.epic.com/ to get credentials\n")

    # For demonstration purposes - replace with actual credentials
    client_id = "YOUR_CLIENT_ID_HERE"
    client_secret = "YOUR_CLIENT_SECRET_HERE"  # Only for sandbox

    if client_id == "YOUR_CLIENT_ID_HERE":
        print("⚠️  Please update the script with your Epic sandbox credentials")
        print("   1. Register at https://fhir.epic.com/")
        print("   2. Create a non-production app")
        print("   3. Get your client_id and client_secret")
        print("   4. Update this script with your credentials\n")
        return

    try:
        # Initialize client
        client = EpicFHIRClient(client_id=client_id)

        # Authenticate
        print("Authenticating with Epic FHIR API...")
        token_data = client.authenticate_backend_service(client_secret=client_secret)
        print(f"✓ Authentication successful")
        print(f"  Access token expires in: {token_data.get('expires_in')} seconds\n")

        # Fetch patient data
        patient_id = TEST_PATIENT_IDS[0]
        print(f"Fetching data for test patient: {patient_id}\n")

        # Get comprehensive patient record
        record = client.get_comprehensive_patient_record(patient_id)

        # Display results
        print("\n" + "=" * 80)
        print("PATIENT RECORD SUMMARY")
        print("=" * 80 + "\n")

        # Patient demographics
        patient = record['patient']
        if 'name' in patient and patient['name']:
            name = patient['name'][0]
            full_name = f"{name.get('given', [''])[0]} {name.get('family', '')}"
            print(f"Patient Name: {full_name}")

        if 'birthDate' in patient:
            print(f"Birth Date: {patient['birthDate']}")

        if 'gender' in patient:
            print(f"Gender: {patient['gender']}")

        print(f"\nConditions: {len(record['conditions'])}")
        for condition in record['conditions'][:3]:  # Show first 3
            if 'code' in condition and 'text' in condition['code']:
                print(f"  - {condition['code']['text']}")

        print(f"\nMedications: {len(record['medications'])}")
        for med in record['medications'][:3]:  # Show first 3
            if 'medicationCodeableConcept' in med:
                med_code = med['medicationCodeableConcept']
                if 'text' in med_code:
                    print(f"  - {med_code['text']}")

        print(f"\nAllergies: {len(record['allergies'])}")
        for allergy in record['allergies'][:3]:  # Show first 3
            if 'code' in allergy and 'text' in allergy['code']:
                print(f"  - {allergy['code']['text']}")

        print(f"\nLab Results: {len(record['observations']['laboratory'])}")
        print(f"Vital Signs: {len(record['observations']['vital_signs'])}")

        # Save to file
        output_file = f"logs/patient_{patient_id}_record.json"
        with open(output_file, 'w') as f:
            json.dump(record, f, indent=2)
        print(f"\n✓ Full record saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify your credentials are correct")
        print("2. Check that your app is registered in Epic sandbox")
        print("3. Ensure you have internet connectivity")
        print("4. Check the logs/epic_fhir.log file for details")


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Run demonstration
    demonstrate_epic_fhir()
