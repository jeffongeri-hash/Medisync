"""
Cerner FHIR Client for EHR Data Writing
========================================
Client for sending patient data to Cerner's FHIR API (Sandbox & Production).

Cerner FHIR Sandbox: https://fhir.cerner.com/
This implementation supports Cerner's OAuth 2.0 flow and FHIR R4 resources.

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
import uuid


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cerner_fhir.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CernerFHIRClient:
    """
    Client for interacting with Cerner's FHIR API.

    Supports:
    - OAuth 2.0 authentication (Backend Service / Client Credentials)
    - Patient data creation and updates
    - Writing Observation, Condition, MedicationRequest, AllergyIntolerance resources
    - FHIR R4 specification
    """

    # Cerner Sandbox endpoints
    CERNER_SANDBOX_FHIR_BASE = "https://fhir-myrecord.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
    CERNER_SANDBOX_TOKEN_URL = "https://authorization.cerner.com/tenants/ec2458f2-1e24-41c8-b71b-0e701af7583d/protocols/oauth2/profiles/smart-v1/token"

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 fhir_base_url: Optional[str] = None,
                 token_url: Optional[str] = None):
        """
        Initialize Cerner FHIR client.

        Args:
            client_id: OAuth client ID from Cerner
            client_secret: OAuth client secret from Cerner
            fhir_base_url: FHIR base URL (defaults to sandbox)
            token_url: OAuth token endpoint (defaults to sandbox)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.fhir_base_url = fhir_base_url or self.CERNER_SANDBOX_FHIR_BASE
        self.token_url = token_url or self.CERNER_SANDBOX_TOKEN_URL
        self.access_token = None
        self.token_expires_at = None

        logger.info(f"Initialized Cerner FHIR Client")
        logger.info(f"FHIR Base URL: {self.fhir_base_url}")

    def authenticate_backend_service(self) -> Dict[str, Any]:
        """
        Authenticate using Backend Service (client credentials flow).

        Returns:
            Token response dictionary
        """
        logger.info("Authenticating with Cerner FHIR API")

        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'system/Patient.write system/Observation.write system/Condition.write system/MedicationRequest.write system/AllergyIntolerance.write'
            }

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

            logger.info("Successfully authenticated with Cerner FHIR API")
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

    def create_patient(self, patient_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a patient in Cerner.

        Args:
            patient_resource: FHIR Patient resource

        Returns:
            Created patient resource with ID
        """
        logger.info("Creating patient in Cerner")

        url = f"{self.fhir_base_url}/Patient"

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=patient_resource,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Create patient failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Create patient failed: {response.text}")

            patient = response.json()
            patient_id = patient.get('id')
            logger.info(f"Successfully created patient: {patient_id}")

            return patient

        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise

    def update_patient(self, patient_id: str, patient_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing patient in Cerner.

        Args:
            patient_id: FHIR Patient ID
            patient_resource: FHIR Patient resource

        Returns:
            Updated patient resource
        """
        logger.info(f"Updating patient in Cerner: {patient_id}")

        url = f"{self.fhir_base_url}/Patient/{patient_id}"

        try:
            response = requests.put(
                url,
                headers=self._get_headers(),
                json=patient_resource,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Update patient failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Update patient failed: {response.text}")

            patient = response.json()
            logger.info(f"Successfully updated patient: {patient_id}")

            return patient

        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            raise

    def create_observation(self, observation_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an observation (lab result, vital sign) in Cerner.

        Args:
            observation_resource: FHIR Observation resource

        Returns:
            Created observation resource with ID
        """
        logger.info("Creating observation in Cerner")

        url = f"{self.fhir_base_url}/Observation"

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=observation_resource,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Create observation failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Create observation failed: {response.text}")

            observation = response.json()
            observation_id = observation.get('id')
            logger.info(f"Successfully created observation: {observation_id}")

            return observation

        except Exception as e:
            logger.error(f"Error creating observation: {str(e)}")
            raise

    def create_condition(self, condition_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a condition (diagnosis) in Cerner.

        Args:
            condition_resource: FHIR Condition resource

        Returns:
            Created condition resource with ID
        """
        logger.info("Creating condition in Cerner")

        url = f"{self.fhir_base_url}/Condition"

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=condition_resource,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Create condition failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Create condition failed: {response.text}")

            condition = response.json()
            condition_id = condition.get('id')
            logger.info(f"Successfully created condition: {condition_id}")

            return condition

        except Exception as e:
            logger.error(f"Error creating condition: {str(e)}")
            raise

    def create_medication_request(self, medication_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a medication request in Cerner.

        Args:
            medication_resource: FHIR MedicationRequest resource

        Returns:
            Created medication request resource with ID
        """
        logger.info("Creating medication request in Cerner")

        url = f"{self.fhir_base_url}/MedicationRequest"

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=medication_resource,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Create medication request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Create medication request failed: {response.text}")

            medication = response.json()
            medication_id = medication.get('id')
            logger.info(f"Successfully created medication request: {medication_id}")

            return medication

        except Exception as e:
            logger.error(f"Error creating medication request: {str(e)}")
            raise

    def create_allergy_intolerance(self, allergy_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an allergy intolerance in Cerner.

        Args:
            allergy_resource: FHIR AllergyIntolerance resource

        Returns:
            Created allergy intolerance resource with ID
        """
        logger.info("Creating allergy intolerance in Cerner")

        url = f"{self.fhir_base_url}/AllergyIntolerance"

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=allergy_resource,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Create allergy intolerance failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Create allergy intolerance failed: {response.text}")

            allergy = response.json()
            allergy_id = allergy.get('id')
            logger.info(f"Successfully created allergy intolerance: {allergy_id}")

            return allergy

        except Exception as e:
            logger.error(f"Error creating allergy intolerance: {str(e)}")
            raise

    def create_bundle(self, bundle_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a transaction bundle (multiple resources at once).

        Args:
            bundle_resource: FHIR Bundle resource with transaction type

        Returns:
            Transaction response bundle
        """
        logger.info("Creating transaction bundle in Cerner")

        url = self.fhir_base_url

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=bundle_resource,
                timeout=60
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Create bundle failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Create bundle failed: {response.text}")

            bundle = response.json()
            entry_count = len(bundle.get('entry', []))
            logger.info(f"Successfully created bundle with {entry_count} entries")

            return bundle

        except Exception as e:
            logger.error(f"Error creating bundle: {str(e)}")
            raise

    def send_patient_data(self,
                         patient: Dict[str, Any],
                         conditions: List[Dict[str, Any]] = None,
                         medications: List[Dict[str, Any]] = None,
                         allergies: List[Dict[str, Any]] = None,
                         observations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send complete patient data to Cerner using a transaction bundle.

        Args:
            patient: FHIR Patient resource
            conditions: List of FHIR Condition resources
            medications: List of FHIR MedicationRequest resources
            allergies: List of FHIR AllergyIntolerance resources
            observations: List of FHIR Observation resources

        Returns:
            Transaction response with all created resource IDs
        """
        logger.info("Sending complete patient data to Cerner")

        # Build transaction bundle
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }

        # Add patient
        patient_id = str(uuid.uuid4())
        bundle["entry"].append({
            "fullUrl": f"urn:uuid:{patient_id}",
            "resource": patient,
            "request": {
                "method": "POST",
                "url": "Patient"
            }
        })

        # Add conditions
        if conditions:
            for condition in conditions:
                # Update patient reference to use temporary ID
                if 'subject' in condition:
                    condition['subject']['reference'] = f"urn:uuid:{patient_id}"

                bundle["entry"].append({
                    "resource": condition,
                    "request": {
                        "method": "POST",
                        "url": "Condition"
                    }
                })

        # Add medications
        if medications:
            for medication in medications:
                # Update patient reference
                if 'subject' in medication:
                    medication['subject']['reference'] = f"urn:uuid:{patient_id}"

                bundle["entry"].append({
                    "resource": medication,
                    "request": {
                        "method": "POST",
                        "url": "MedicationRequest"
                    }
                })

        # Add allergies
        if allergies:
            for allergy in allergies:
                # Update patient reference
                if 'patient' in allergy:
                    allergy['patient']['reference'] = f"urn:uuid:{patient_id}"

                bundle["entry"].append({
                    "resource": allergy,
                    "request": {
                        "method": "POST",
                        "url": "AllergyIntolerance"
                    }
                })

        # Add observations
        if observations:
            for observation in observations:
                # Update patient reference
                if 'subject' in observation:
                    observation['subject']['reference'] = f"urn:uuid:{patient_id}"

                bundle["entry"].append({
                    "resource": observation,
                    "request": {
                        "method": "POST",
                        "url": "Observation"
                    }
                })

        logger.info(f"Bundle contains {len(bundle['entry'])} resources")

        # Send bundle
        result = self.create_bundle(bundle)

        # Extract created IDs
        created_resources = {
            'patient_id': None,
            'condition_ids': [],
            'medication_ids': [],
            'allergy_ids': [],
            'observation_ids': []
        }

        if 'entry' in result:
            for i, entry in enumerate(result['entry']):
                if 'response' in entry and entry['response'].get('status', '').startswith('201'):
                    location = entry['response'].get('location', '')
                    resource_id = location.split('/')[-1].split('/_history')[0]

                    if i == 0:  # First entry is patient
                        created_resources['patient_id'] = resource_id
                    elif 'Condition' in location:
                        created_resources['condition_ids'].append(resource_id)
                    elif 'MedicationRequest' in location:
                        created_resources['medication_ids'].append(resource_id)
                    elif 'AllergyIntolerance' in location:
                        created_resources['allergy_ids'].append(resource_id)
                    elif 'Observation' in location:
                        created_resources['observation_ids'].append(resource_id)

        logger.info("Successfully sent patient data to Cerner")
        logger.info(f"Created Patient ID: {created_resources['patient_id']}")
        logger.info(f"Created {len(created_resources['condition_ids'])} conditions")
        logger.info(f"Created {len(created_resources['medication_ids'])} medications")
        logger.info(f"Created {len(created_resources['allergy_ids'])} allergies")
        logger.info(f"Created {len(created_resources['observation_ids'])} observations")

        return created_resources


def demonstrate_cerner_fhir():
    """
    Demonstration of Cerner FHIR client usage with sandbox.

    To use Cerner sandbox:
    1. Register at https://fhir.cerner.com/
    2. Get your client_id and client_secret
    3. Create test resources
    """
    print("\n" + "=" * 80)
    print("CERNER FHIR CLIENT DEMONSTRATION")
    print("=" * 80 + "\n")

    # For demonstration purposes - replace with actual credentials
    client_id = "YOUR_CERNER_CLIENT_ID"
    client_secret = "YOUR_CERNER_CLIENT_SECRET"

    if client_id == "YOUR_CERNER_CLIENT_ID":
        print("⚠️  Please update the script with your Cerner sandbox credentials")
        print("   1. Register at https://fhir.cerner.com/")
        print("   2. Create a system account")
        print("   3. Get your client_id and client_secret")
        print("   4. Update this script with your credentials\n")
        return

    try:
        # Initialize client
        client = CernerFHIRClient(
            client_id=client_id,
            client_secret=client_secret
        )

        # Authenticate
        print("Authenticating with Cerner FHIR API...")
        token_data = client.authenticate_backend_service()
        print(f"✓ Authentication successful\n")

        # Create sample patient
        patient = {
            "resourceType": "Patient",
            "identifier": [
                {
                    "system": "http://hospital.org/mrn",
                    "value": "MRN123456"
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": "Smith",
                    "given": ["John"]
                }
            ],
            "gender": "male",
            "birthDate": "1980-05-15"
        }

        print("Creating patient in Cerner...")
        created_patient = client.create_patient(patient)
        patient_id = created_patient['id']
        print(f"✓ Patient created with ID: {patient_id}\n")

        # Create sample observation
        observation = {
            "resourceType": "Observation",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "valueQuantity": {
                "value": 120,
                "unit": "mmHg"
            }
        }

        print("Creating observation in Cerner...")
        created_observation = client.create_observation(observation)
        print(f"✓ Observation created with ID: {created_observation['id']}\n")

        print("=" * 80)
        print("CERNER TRANSFER COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nCheck logs/cerner_fhir.log for details")


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Run demonstration
    demonstrate_cerner_fhir()
