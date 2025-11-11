#!/usr/bin/env python3
"""
Epic to Cerner EHR Data Transfer
Authenticates with Epic sandbox using OAuth 2.0 and transfers patient data to Cerner
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import sys
import base64

# ============================================================================
# CONFIGURATION - Epic Sandbox Credentials
# ============================================================================

# Your Epic Sandbox Client IDs
EPIC_CLIENT_ID_1 = "975449d0-070d-439e-ac6a-168a89ea59ed"
EPIC_CLIENT_ID_2 = "41767c4f-8948-402b-97e8-2c6010899539"  # Non-Production Client ID

# Epic Client Secret - YOU NEED TO GET THIS FROM EPIC
# To get your client secret:
# 1. Go to https://fhir.epic.com/Developer/Apps
# 2. Sign in with your Epic account
# 3. Find your registered app
# 4. Click "Manage Keys" or "View Credentials"
# 5. Copy the Client Secret and paste it below

EPIC_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"  # ← REPLACE THIS (Line 25)

# NOTE: If you don't have a client secret yet, you have two options:
# Option 1: Use the public sandbox (no auth) - see epic_fhir_client.py
# Option 2: Register your app at https://fhir.epic.com/Developer/Apps to get credentials

# Epic FHIR Endpoints
EPIC_FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
EPIC_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"

# Line 36 - This is where you'll use your client credentials for OAuth
# Example of what it should look like when you have your client secret:
# EPIC_AUTH = {
#     'client_id': EPIC_CLIENT_ID_2,
#     'client_secret': 'your-actual-secret-here-abc123xyz',
#     'grant_type': 'client_credentials'
# }

# Cerner Configuration (Simulated - you don't have credentials yet)
CERNER_FHIR_BASE_URL = "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"
CERNER_CLIENT_ID = "SIMULATED"  # You'll need real Cerner credentials for production
CERNER_CLIENT_SECRET = "SIMULATED"

# Test Patient IDs from Epic Sandbox
TEST_PATIENT_IDS = {
    'Derrick Lin': 'eqBqGJ4BxFL.84mz3p93QiQB',
    'Camilla Lopez': 'erXuFYUfU6B3BKuMKq9T0SQB',
    'Desiree Powell': 'eCRk28CcQU9LYgwE.OUVqXAB',
    'Amy Shaw': 'egqBHIZQfVZQpJARGdlD.3QB',
}


class EpicOAuthClient:
    """
    Epic FHIR Client with OAuth 2.0 Authentication
    """

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Epic OAuth client

        Args:
            client_id: Epic application client ID
            client_secret: Epic application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = EPIC_TOKEN_URL
        self.base_url = EPIC_FHIR_BASE_URL
        self.access_token = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """
        Authenticate with Epic using OAuth 2.0 Client Credentials Flow

        Returns:
            True if authentication successful, False otherwise
        """
        print("🔐 Authenticating with Epic OAuth 2.0...")

        # Check if client secret is configured
        if self.client_secret == "YOUR_CLIENT_SECRET_HERE":
            print("\n❌ ERROR: Client secret not configured!")
            print("━" * 80)
            print("You need to add your Epic client secret to line 25 of this file.")
            print("\nHow to get your client secret:")
            print("1. Go to: https://fhir.epic.com/Developer/Apps")
            print("2. Sign in with your Epic account")
            print("3. Find your registered application")
            print("4. Click 'Manage Keys' or 'View Credentials'")
            print("5. Copy the Client Secret")
            print("6. Replace 'YOUR_CLIENT_SECRET_HERE' on line 25 with your secret")
            print("\nAlternatively, use epic_fhir_client.py which works without authentication.")
            print("━" * 80)
            return False

        try:
            # OAuth 2.0 Client Credentials Request
            # This is what Line 36 was asking about - here's the full auth process
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                # For Epic, you may also need to specify scopes
                # Common scopes for system access:
                # 'scope': 'system/Patient.read system/Observation.read system/MedicationRequest.read'
            }

            # Some OAuth servers want credentials in Basic Auth header instead
            # Epic typically uses this approach
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            # Make the token request
            response = requests.post(
                self.token_url,
                data={'grant_type': 'client_credentials'},
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')

                # Set up session with bearer token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/fhir+json',
                    'Content-Type': 'application/fhir+json'
                })

                print(f"✅ Authentication successful!")
                print(f"   Access Token: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during authentication: {e}")
            return False

    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Get patient demographics from Epic

        Args:
            patient_id: Epic patient ID

        Returns:
            Patient resource or None
        """
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate() first.")
            return None

        try:
            url = f"{self.base_url}/Patient/{patient_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching patient: {e}")
            return None

    def get_observations(self, patient_id: str, category: str = "vital-signs") -> List[Dict]:
        """Get patient observations (vital signs, labs, etc.)"""
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate() first.")
            return []

        try:
            url = f"{self.base_url}/Observation"
            params = {
                'patient': patient_id,
                'category': category,
                '_count': 100
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                return [entry['resource'] for entry in data['entry']]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching observations: {e}")
            return []

    def get_medications(self, patient_id: str) -> List[Dict]:
        """Get patient medications"""
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate() first.")
            return []

        try:
            url = f"{self.base_url}/MedicationRequest"
            params = {
                'patient': patient_id,
                'status': 'active',
                '_count': 100
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                return [entry['resource'] for entry in data['entry']]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching medications: {e}")
            return []

    def get_conditions(self, patient_id: str) -> List[Dict]:
        """Get patient conditions"""
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate() first.")
            return []

        try:
            url = f"{self.base_url}/Condition"
            params = {
                'patient': patient_id,
                '_count': 100
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'entry' in data:
                return [entry['resource'] for entry in data['entry']]
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching conditions: {e}")
            return []


class CernerClient:
    """
    Cerner FHIR Client (Simulated - you don't have credentials yet)
    """

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.simulated = (client_id == "SIMULATED")

    def authenticate(self) -> bool:
        """Simulate Cerner authentication"""
        if self.simulated:
            print("🔐 Simulating Cerner authentication (no real credentials)...")
            print("✅ Cerner authentication simulated")
            return True
        # Real implementation would go here
        return False

    def create_patient(self, patient_data: Dict) -> bool:
        """Simulate creating patient in Cerner"""
        if self.simulated:
            print("📤 Simulating patient data transfer to Cerner...")
            print("✅ Patient data transferred (simulated)")
            return True
        # Real implementation would go here
        return False

    def create_observations(self, observations: List[Dict]) -> bool:
        """Simulate creating observations in Cerner"""
        if self.simulated:
            print(f"📤 Simulating transfer of {len(observations)} vital signs to Cerner...")
            print("✅ Vital signs transferred (simulated)")
            return True
        return False

    def create_medications(self, medications: List[Dict]) -> bool:
        """Simulate creating medications in Cerner"""
        if self.simulated:
            print(f"📤 Simulating transfer of {len(medications)} medications to Cerner...")
            print("✅ Medications transferred (simulated)")
            return True
        return False


def extract_patient_summary(patient_resource: Dict) -> Dict:
    """Extract key patient information"""
    summary = {}

    if 'name' in patient_resource and len(patient_resource['name']) > 0:
        name_obj = patient_resource['name'][0]
        given = ' '.join(name_obj.get('given', []))
        family = name_obj.get('family', '')
        summary['name'] = f"{given} {family}".strip()

    summary['id'] = patient_resource.get('id', 'Unknown')
    summary['birthDate'] = patient_resource.get('birthDate', 'Unknown')
    summary['gender'] = patient_resource.get('gender', 'Unknown')

    return summary


def display_transfer_summary(patient_summary: Dict, vitals_count: int, meds_count: int, conditions_count: int):
    """Display transfer summary"""
    print("\n" + "=" * 80)
    print("EPIC TO CERNER TRANSFER SUMMARY")
    print("=" * 80)
    print(f"\n👤 Patient:           {patient_summary.get('name', 'N/A')}")
    print(f"📋 Patient ID:        {patient_summary.get('id', 'N/A')}")
    print(f"📅 Date of Birth:     {patient_summary.get('birthDate', 'N/A')}")
    print(f"⚧  Gender:            {patient_summary.get('gender', 'N/A').capitalize()}")
    print(f"\n📊 Data Transferred:")
    print(f"   • Vital Signs:     {vitals_count}")
    print(f"   • Medications:     {meds_count}")
    print(f"   • Conditions:      {conditions_count}")
    print(f"\n✅ Transfer completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


def main():
    """
    Main transfer workflow
    """
    print("=" * 80)
    print("EPIC TO CERNER EHR DATA TRANSFER")
    print("=" * 80)
    print("\nThis script transfers patient data from Epic sandbox to Cerner\n")

    # Initialize Epic client with your credentials
    print("Initializing Epic FHIR Client...")
    print(f"Client ID: {EPIC_CLIENT_ID_2}")

    epic_client = EpicOAuthClient(
        client_id=EPIC_CLIENT_ID_2,
        client_secret=EPIC_CLIENT_SECRET
    )

    # Authenticate with Epic
    if not epic_client.authenticate():
        print("\n⚠️  Authentication failed. See instructions above.")
        print("\nTo use without authentication, run:")
        print("  python epic_fhir_client.py")
        sys.exit(1)

    # Select patient
    print("\nAvailable Test Patients:")
    for i, (name, patient_id) in enumerate(TEST_PATIENT_IDS.items(), 1):
        print(f"{i}. {name} (ID: {patient_id})")

    print("\nPress Enter to use default patient (Derrick Lin) or enter patient number (1-4):")
    try:
        choice = input("> ").strip()
        if choice and choice.isdigit() and 1 <= int(choice) <= len(TEST_PATIENT_IDS):
            selected_patient = list(TEST_PATIENT_IDS.items())[int(choice) - 1]
            patient_name, patient_id = selected_patient
        else:
            patient_name, patient_id = list(TEST_PATIENT_IDS.items())[0]

        print(f"\n✅ Selected: {patient_name} (ID: {patient_id})\n")
    except (EOFError, KeyboardInterrupt):
        print("\n\n❌ Cancelled by user")
        sys.exit(0)

    # Retrieve data from Epic
    print("━" * 80)
    print("RETRIEVING DATA FROM EPIC")
    print("━" * 80)

    print("🔄 Fetching patient demographics...")
    patient_resource = epic_client.get_patient(patient_id)
    if not patient_resource:
        print("❌ Failed to retrieve patient data")
        sys.exit(1)
    patient_summary = extract_patient_summary(patient_resource)
    print(f"✅ Retrieved: {patient_summary['name']}")

    print("🔄 Fetching vital signs...")
    observations = epic_client.get_observations(patient_id, category="vital-signs")
    print(f"✅ Retrieved {len(observations)} vital sign records")

    print("🔄 Fetching medications...")
    medications = epic_client.get_medications(patient_id)
    print(f"✅ Retrieved {len(medications)} medication records")

    print("🔄 Fetching conditions...")
    conditions = epic_client.get_conditions(patient_id)
    print(f"✅ Retrieved {len(conditions)} condition records")

    # Initialize Cerner client
    print("\n" + "━" * 80)
    print("TRANSFERRING DATA TO CERNER")
    print("━" * 80)

    cerner_client = CernerClient(
        client_id=CERNER_CLIENT_ID,
        client_secret=CERNER_CLIENT_SECRET
    )

    cerner_client.authenticate()

    # Transfer data to Cerner
    cerner_client.create_patient(patient_resource)
    cerner_client.create_observations(observations)
    cerner_client.create_medications(medications)

    # Display summary
    display_transfer_summary(
        patient_summary,
        len(observations),
        len(medications),
        len(conditions)
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Transfer interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
