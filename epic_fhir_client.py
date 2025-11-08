#!/usr/bin/env python3
"""
Epic FHIR Sandbox Client
Connects to Epic's real FHIR sandbox and extracts patient data
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Epic FHIR Sandbox Configuration
EPIC_FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"

# Epic's public sandbox test patient IDs
# These are real test patients in Epic's sandbox
TEST_PATIENT_IDS = {
    'Derrick Lin': 'eqBqGJ4BxFL.84mz3p93QiQB',
    'Camilla Lopez': 'erXuFYUfU6B3BKuMKq9T0SQB',
    'Desiree Powell': 'eCRk28CcQU9LYgwE.OUVqXAB',
    'Amy Shaw': 'egqBHIZQfVZQpJARGdlD.3QB',
}


class EpicFHIRClient:
    """
    Client for Epic FHIR Sandbox API
    Uses non-authenticated public sandbox endpoints
    """

    def __init__(self, base_url: str = EPIC_FHIR_BASE_URL):
        """
        Initialize Epic FHIR client

        Args:
            base_url: Epic FHIR base URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        })

    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Get patient demographics

        Args:
            patient_id: Epic patient ID

        Returns:
            Patient resource or None
        """
        try:
            url = f"{self.base_url}/Patient/{patient_id}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching patient: {e}")
            return None

    def get_observations(self, patient_id: str, category: str = "vital-signs") -> List[Dict]:
        """
        Get patient observations (vital signs, lab results, etc.)

        Args:
            patient_id: Epic patient ID
            category: Observation category (vital-signs, laboratory, etc.)

        Returns:
            List of observation resources
        """
        try:
            url = f"{self.base_url}/Observation"
            params = {
                'patient': patient_id,
                'category': category,
                '_count': 100
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                return [entry['resource'] for entry in data['entry']]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching observations: {e}")
            return []

    def get_medications(self, patient_id: str) -> List[Dict]:
        """
        Get patient medication requests

        Args:
            patient_id: Epic patient ID

        Returns:
            List of medication request resources
        """
        try:
            url = f"{self.base_url}/MedicationRequest"
            params = {
                'patient': patient_id,
                'status': 'active',
                '_count': 100
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                return [entry['resource'] for entry in data['entry']]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching medications: {e}")
            return []

    def get_conditions(self, patient_id: str) -> List[Dict]:
        """
        Get patient conditions/problems

        Args:
            patient_id: Epic patient ID

        Returns:
            List of condition resources
        """
        try:
            url = f"{self.base_url}/Condition"
            params = {
                'patient': patient_id,
                '_count': 100
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                return [entry['resource'] for entry in data['entry']]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching conditions: {e}")
            return []


class PatientDataExtractor:
    """
    Extracts and formats patient data from FHIR resources
    """

    @staticmethod
    def extract_patient_info(patient_resource: Dict) -> Dict:
        """
        Extract patient demographics

        Args:
            patient_resource: FHIR Patient resource

        Returns:
            Formatted patient information
        """
        if not patient_resource:
            return {}

        # Extract name
        name = "Unknown"
        if 'name' in patient_resource and len(patient_resource['name']) > 0:
            name_obj = patient_resource['name'][0]
            given = ' '.join(name_obj.get('given', []))
            family = name_obj.get('family', '')
            name = f"{given} {family}".strip()

        # Extract birth date
        birth_date = patient_resource.get('birthDate', 'Unknown')

        # Extract gender
        gender = patient_resource.get('gender', 'Unknown')

        # Extract ID
        patient_id = patient_resource.get('id', 'Unknown')

        # Extract contact
        contact = {}
        if 'telecom' in patient_resource:
            for telecom in patient_resource['telecom']:
                system = telecom.get('system', '')
                value = telecom.get('value', '')
                if system == 'phone':
                    contact['phone'] = value
                elif system == 'email':
                    contact['email'] = value

        # Extract address
        address_info = {}
        if 'address' in patient_resource and len(patient_resource['address']) > 0:
            addr = patient_resource['address'][0]
            address_info = {
                'line': addr.get('line', []),
                'city': addr.get('city', ''),
                'state': addr.get('state', ''),
                'postalCode': addr.get('postalCode', ''),
                'country': addr.get('country', '')
            }

        return {
            'id': patient_id,
            'name': name,
            'birthDate': birth_date,
            'gender': gender,
            'contact': contact,
            'address': address_info
        }

    @staticmethod
    def extract_vital_signs(observations: List[Dict]) -> List[Dict]:
        """
        Extract vital signs from observations

        Args:
            observations: List of FHIR Observation resources

        Returns:
            List of formatted vital signs
        """
        vitals = []

        for obs in observations:
            vital = {}

            # Get type/code
            if 'code' in obs and 'text' in obs['code']:
                vital['type'] = obs['code']['text']
            elif 'code' in obs and 'coding' in obs['code']:
                if len(obs['code']['coding']) > 0:
                    vital['type'] = obs['code']['coding'][0].get('display', 'Unknown')

            # Get value
            if 'valueQuantity' in obs:
                vital['value'] = obs['valueQuantity'].get('value', 'N/A')
                vital['unit'] = obs['valueQuantity'].get('unit', '')
            elif 'component' in obs:
                # For blood pressure with components
                components = []
                for comp in obs['component']:
                    if 'valueQuantity' in comp:
                        comp_name = comp['code']['coding'][0].get('display', '')
                        comp_value = comp['valueQuantity'].get('value', '')
                        comp_unit = comp['valueQuantity'].get('unit', '')
                        components.append(f"{comp_name}: {comp_value} {comp_unit}")
                vital['value'] = ', '.join(components)
                vital['unit'] = ''

            # Get date
            if 'effectiveDateTime' in obs:
                vital['date'] = obs['effectiveDateTime']
            elif 'issued' in obs:
                vital['date'] = obs['issued']

            if vital:
                vitals.append(vital)

        return vitals

    @staticmethod
    def extract_medications(medication_requests: List[Dict]) -> List[Dict]:
        """
        Extract medications from medication requests

        Args:
            medication_requests: List of FHIR MedicationRequest resources

        Returns:
            List of formatted medications
        """
        medications = []

        for med_req in medication_requests:
            medication = {}

            # Get medication name
            if 'medicationCodeableConcept' in med_req:
                if 'text' in med_req['medicationCodeableConcept']:
                    medication['name'] = med_req['medicationCodeableConcept']['text']
                elif 'coding' in med_req['medicationCodeableConcept']:
                    if len(med_req['medicationCodeableConcept']['coding']) > 0:
                        medication['name'] = med_req['medicationCodeableConcept']['coding'][0].get('display', 'Unknown')

            # Get dosage instructions
            if 'dosageInstruction' in med_req and len(med_req['dosageInstruction']) > 0:
                dosage = med_req['dosageInstruction'][0]
                if 'text' in dosage:
                    medication['dosage'] = dosage['text']
                elif 'doseAndRate' in dosage and len(dosage['doseAndRate']) > 0:
                    dose_info = dosage['doseAndRate'][0]
                    if 'doseQuantity' in dose_info:
                        value = dose_info['doseQuantity'].get('value', '')
                        unit = dose_info['doseQuantity'].get('unit', '')
                        medication['dosage'] = f"{value} {unit}"

            # Get status
            medication['status'] = med_req.get('status', 'unknown')

            # Get authored date
            if 'authoredOn' in med_req:
                medication['authoredOn'] = med_req['authoredOn']

            if medication:
                medications.append(medication)

        return medications

    @staticmethod
    def extract_conditions(conditions: List[Dict]) -> List[Dict]:
        """
        Extract conditions/problems

        Args:
            conditions: List of FHIR Condition resources

        Returns:
            List of formatted conditions
        """
        formatted_conditions = []

        for cond in conditions:
            condition = {}

            # Get condition name
            if 'code' in cond:
                if 'text' in cond['code']:
                    condition['name'] = cond['code']['text']
                elif 'coding' in cond['code'] and len(cond['code']['coding']) > 0:
                    condition['name'] = cond['code']['coding'][0].get('display', 'Unknown')

            # Get clinical status
            if 'clinicalStatus' in cond and 'coding' in cond['clinicalStatus']:
                if len(cond['clinicalStatus']['coding']) > 0:
                    condition['status'] = cond['clinicalStatus']['coding'][0].get('code', 'unknown')

            # Get onset date
            if 'onsetDateTime' in cond:
                condition['onsetDate'] = cond['onsetDateTime']

            # Get recorded date
            if 'recordedDate' in cond:
                condition['recordedDate'] = cond['recordedDate']

            if condition:
                formatted_conditions.append(condition)

        return formatted_conditions


def display_patient_data(patient_info: Dict, vitals: List[Dict], medications: List[Dict], conditions: List[Dict]):
    """
    Display patient data in a formatted way

    Args:
        patient_info: Patient demographics
        vitals: List of vital signs
        medications: List of medications
        conditions: List of conditions
    """
    print("\n" + "=" * 80)
    print("PATIENT INFORMATION FROM EPIC FHIR SANDBOX")
    print("=" * 80)

    # Patient Demographics
    print("\n👤 PATIENT DEMOGRAPHICS")
    print("-" * 80)
    print(f"Name:              {patient_info.get('name', 'N/A')}")
    print(f"Patient ID:        {patient_info.get('id', 'N/A')}")
    print(f"Date of Birth:     {patient_info.get('birthDate', 'N/A')}")
    print(f"Gender:            {patient_info.get('gender', 'N/A').capitalize()}")

    if patient_info.get('contact'):
        print(f"Phone:             {patient_info['contact'].get('phone', 'N/A')}")
        print(f"Email:             {patient_info['contact'].get('email', 'N/A')}")

    if patient_info.get('address'):
        addr = patient_info['address']
        if addr.get('line'):
            print(f"Address:           {', '.join(addr['line'])}")
        print(f"City, State:       {addr.get('city', 'N/A')}, {addr.get('state', 'N/A')} {addr.get('postalCode', '')}")

    # Vital Signs
    print("\n📈 VITAL SIGNS")
    print("-" * 80)
    if vitals:
        for i, vital in enumerate(vitals[:10], 1):  # Show first 10
            print(f"{i}. {vital.get('type', 'Unknown')}")
            print(f"   Value: {vital.get('value', 'N/A')} {vital.get('unit', '')}")
            print(f"   Date:  {vital.get('date', 'N/A')[:10] if vital.get('date') else 'N/A'}")
            print()
    else:
        print("No vital signs found in sandbox")

    # Medications
    print("\n💊 MEDICATIONS")
    print("-" * 80)
    if medications:
        for i, med in enumerate(medications, 1):
            print(f"{i}. {med.get('name', 'Unknown')}")
            print(f"   Dosage: {med.get('dosage', 'N/A')}")
            print(f"   Status: {med.get('status', 'N/A')}")
            if med.get('authoredOn'):
                print(f"   Date:   {med['authoredOn'][:10]}")
            print()
    else:
        print("No medications found in sandbox")

    # Conditions
    print("\n⚕️  MEDICAL CONDITIONS")
    print("-" * 80)
    if conditions:
        for i, cond in enumerate(conditions, 1):
            print(f"{i}. {cond.get('name', 'Unknown')}")
            print(f"   Status: {cond.get('status', 'N/A')}")
            if cond.get('onsetDate'):
                print(f"   Onset:  {cond['onsetDate'][:10]}")
            print()
    else:
        print("No conditions found in sandbox")

    print("=" * 80)
    print(f"\n✅ Data retrieved from Epic FHIR Sandbox at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


def main():
    """
    Main function - retrieve and display patient data from Epic sandbox
    """
    print("=" * 80)
    print("EPIC FHIR SANDBOX - PATIENT DATA EXTRACTOR")
    print("=" * 80)
    print("\nConnecting to Epic's public FHIR sandbox...")
    print(f"Base URL: {EPIC_FHIR_BASE_URL}\n")

    # Show available test patients
    print("Available Test Patients:")
    for i, (name, patient_id) in enumerate(TEST_PATIENT_IDS.items(), 1):
        print(f"{i}. {name} (ID: {patient_id})")

    # Let user select a patient or use default
    print("\nPress Enter to use default patient (Derrick Lin) or enter patient number (1-4):")
    try:
        choice = input("> ").strip()
        if choice and choice.isdigit() and 1 <= int(choice) <= len(TEST_PATIENT_IDS):
            selected_patient = list(TEST_PATIENT_IDS.items())[int(choice) - 1]
            patient_name, patient_id = selected_patient
        else:
            patient_name, patient_id = list(TEST_PATIENT_IDS.items())[0]  # Default to first

        print(f"\n✅ Selected: {patient_name} (ID: {patient_id})")
    except (EOFError, KeyboardInterrupt):
        print("\n\n❌ Cancelled by user")
        sys.exit(0)

    # Initialize client
    client = EpicFHIRClient()
    extractor = PatientDataExtractor()

    # Fetch patient data
    print("\n🔄 Fetching patient demographics...")
    patient_resource = client.get_patient(patient_id)

    if not patient_resource:
        print("❌ Failed to retrieve patient data. Check your internet connection.")
        sys.exit(1)

    patient_info = extractor.extract_patient_info(patient_resource)
    print("✅ Patient demographics retrieved")

    # Fetch vital signs
    print("🔄 Fetching vital signs...")
    observations = client.get_observations(patient_id, category="vital-signs")
    vitals = extractor.extract_vital_signs(observations)
    print(f"✅ Found {len(vitals)} vital sign records")

    # Fetch medications
    print("🔄 Fetching medications...")
    medication_requests = client.get_medications(patient_id)
    medications = extractor.extract_medications(medication_requests)
    print(f"✅ Found {len(medications)} medication records")

    # Fetch conditions
    print("🔄 Fetching medical conditions...")
    conditions_resources = client.get_conditions(patient_id)
    conditions = extractor.extract_conditions(conditions_resources)
    print(f"✅ Found {len(conditions)} condition records")

    # Display all data
    display_patient_data(patient_info, vitals, medications, conditions)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
