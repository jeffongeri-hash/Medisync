#!/usr/bin/env python3
"""
Quick Script: Transfer Patient Data from Epic to Cerner
========================================================
This script provides a simple interface to transfer patient data
from Epic FHIR API to Cerner FHIR API.

Usage:
    python transfer_epic_to_cerner.py

Requirements:
    - Epic sandbox credentials (client_id, client_secret)
    - Cerner sandbox credentials (client_id, client_secret)
    - Epic patient ID to transfer

Author: Medisync
Date: 2025
"""

import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.epic_to_cerner_transfer import EpicToCernerTransfer


# ============================================================================
# CONFIGURATION - Update with your credentials
# ============================================================================

# Epic Credentials (from https://fhir.epic.com/)
EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID", "YOUR_EPIC_CLIENT_ID")
EPIC_CLIENT_SECRET = os.getenv("EPIC_CLIENT_SECRET", "YOUR_EPIC_CLIENT_SECRET")

# Cerner Credentials (from https://fhir.cerner.com/)
CERNER_CLIENT_ID = os.getenv("CERNER_CLIENT_ID", "YOUR_CERNER_CLIENT_ID")
CERNER_CLIENT_SECRET = os.getenv("CERNER_CLIENT_SECRET", "YOUR_CERNER_CLIENT_SECRET")

# Epic Test Patient IDs (from Epic sandbox)
EPIC_TEST_PATIENTS = {
    "Derrick Lin": "Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB",
    "Camila Lopez": "eq081-VQEgP8drUUqCWzHfw3"
}

# ============================================================================


def print_banner():
    """Print banner."""
    print("\n" + "=" * 80)
    print("EPIC TO CERNER EHR TRANSFER")
    print("Medisync - HIPAA-Compliant Healthcare Data Transfer System")
    print("=" * 80 + "\n")


def check_credentials():
    """Check if credentials are configured."""
    if EPIC_CLIENT_ID == "YOUR_EPIC_CLIENT_ID" or CERNER_CLIENT_ID == "YOUR_CERNER_CLIENT_ID":
        print("⚠️  CREDENTIALS NOT CONFIGURED")
        print("\nPlease set up your Epic and Cerner credentials:")
        print("\nOption 1: Environment Variables (Recommended)")
        print("  export EPIC_CLIENT_ID='your_epic_client_id'")
        print("  export EPIC_CLIENT_SECRET='your_epic_client_secret'")
        print("  export CERNER_CLIENT_ID='your_cerner_client_id'")
        print("  export CERNER_CLIENT_SECRET='your_cerner_client_secret'")
        print("\nOption 2: Update this file")
        print("  Edit transfer_epic_to_cerner.py and update the CONFIGURATION section")
        print("\nHow to get credentials:")
        print("  Epic:   Register at https://fhir.epic.com/")
        print("  Cerner: Register at https://fhir.cerner.com/")
        print("\n" + "=" * 80 + "\n")
        return False
    return True


def select_patient():
    """Let user select a test patient."""
    print("Available Test Patients (Epic Sandbox):")
    print("-" * 80)

    patients = list(EPIC_TEST_PATIENTS.items())
    for i, (name, patient_id) in enumerate(patients, 1):
        print(f"{i}. {name}")
        print(f"   ID: {patient_id}\n")

    print("3. Enter custom patient ID")
    print("-" * 80)

    while True:
        try:
            choice = input("\nSelect patient (1-3): ").strip()
            choice_num = int(choice)

            if choice_num == 1:
                return patients[0][1], patients[0][0]
            elif choice_num == 2:
                return patients[1][1], patients[1][0]
            elif choice_num == 3:
                custom_id = input("Enter Epic patient ID: ").strip()
                return custom_id, "Custom Patient"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number.")


def select_data_elements():
    """Let user select which data elements to transfer."""
    print("\nData Elements to Transfer:")
    print("-" * 80)
    print("1. All data (patient, conditions, medications, allergies, observations)")
    print("2. Patient demographics only")
    print("3. Patient + Conditions + Medications")
    print("4. Custom selection")
    print("-" * 80)

    choice = input("\nSelect option (1-4) [default: 1]: ").strip() or "1"

    if choice == "1":
        return ['patient', 'conditions', 'medications', 'allergies', 'observations']
    elif choice == "2":
        return ['patient']
    elif choice == "3":
        return ['patient', 'conditions', 'medications']
    elif choice == "4":
        print("\nSelect data elements to transfer (y/n for each):")
        elements = []

        if input("  - Patient demographics (y/n): ").strip().lower() == 'y':
            elements.append('patient')
        if input("  - Conditions/Diagnoses (y/n): ").strip().lower() == 'y':
            elements.append('conditions')
        if input("  - Medications (y/n): ").strip().lower() == 'y':
            elements.append('medications')
        if input("  - Allergies (y/n): ").strip().lower() == 'y':
            elements.append('allergies')
        if input("  - Observations (Labs/Vitals) (y/n): ").strip().lower() == 'y':
            elements.append('observations')

        return elements if elements else ['patient']
    else:
        return ['patient', 'conditions', 'medications', 'allergies', 'observations']


def perform_transfer(patient_id: str, patient_name: str, data_elements: List[str]):
    """Perform the actual transfer."""
    print("\n" + "=" * 80)
    print("INITIATING TRANSFER")
    print("=" * 80)
    print(f"\nPatient: {patient_name}")
    print(f"Epic Patient ID: {patient_id}")
    print(f"Data Elements: {', '.join(data_elements)}")
    print(f"Transfer Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "-" * 80 + "\n")

    try:
        # Initialize transfer handler
        print("Step 1: Initializing transfer handler...")
        transfer = EpicToCernerTransfer(
            epic_client_id=EPIC_CLIENT_ID,
            epic_client_secret=EPIC_CLIENT_SECRET,
            cerner_client_id=CERNER_CLIENT_ID,
            cerner_client_secret=CERNER_CLIENT_SECRET
        )
        print("✓ Transfer handler initialized\n")

        # Authenticate
        print("Step 2: Authenticating with Epic and Cerner...")
        auth_results = transfer.authenticate_systems()
        print("✓ Epic authentication successful")
        print("✓ Cerner authentication successful\n")

        # Transfer data
        print("Step 3: Transferring patient data...")
        results = transfer.transfer_patient_data(
            epic_patient_id=patient_id,
            data_elements=data_elements
        )

        # Display results
        print("\n" + "=" * 80)
        print("TRANSFER COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\n✓ Transfer ID: {results['transfer_id']}")
        print(f"✓ Status: {results['status'].upper()}")
        print(f"\n📊 Transfer Summary:")
        print(f"   Source: Epic (Patient ID: {results['epic_patient_id']})")
        print(f"   Destination: Cerner (Patient ID: {results['cerner_patient_id']})")
        print(f"\n📝 Resources Created in Cerner:")
        resources = results['resources_created']
        print(f"   • Conditions: {len(resources.get('condition_ids', []))}")
        print(f"   • Medications: {len(resources.get('medication_ids', []))}")
        print(f"   • Allergies: {len(resources.get('allergy_ids', []))}")
        print(f"   • Observations: {len(resources.get('observation_ids', []))}")
        print(f"\n🔒 Security:")
        print(f"   • Encryption: AES-128 (Fernet)")
        print(f"   • Integrity: SHA-256 checksum")
        print(f"   • Checksum: {results.get('checksum', 'N/A')[:16]}...")
        print(f"\n📄 Audit Log:")
        print(f"   • Transfer logged for HIPAA compliance")
        print(f"   • Log file: logs/transfer_{results['transfer_id']}.json")
        print("\n" + "=" * 80 + "\n")

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("TRANSFER FAILED")
        print("=" * 80)
        print(f"\n❌ Error: {str(e)}")
        print("\n📋 Troubleshooting:")
        print("   1. Verify your credentials are correct")
        print("   2. Check that the patient ID exists in Epic")
        print("   3. Ensure both Epic and Cerner APIs are accessible")
        print("   4. Review logs/epic_to_cerner_transfer.log for details")
        print("\n" + "=" * 80 + "\n")
        return False


def main():
    """Main function."""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Print banner
    print_banner()

    # Check credentials
    if not check_credentials():
        return

    # Select patient
    patient_id, patient_name = select_patient()

    # Select data elements
    data_elements = select_data_elements()

    # Confirm
    print("\n" + "-" * 80)
    print("TRANSFER CONFIRMATION")
    print("-" * 80)
    print(f"Patient: {patient_name}")
    print(f"Epic ID: {patient_id}")
    print(f"Data to transfer: {', '.join(data_elements)}")
    print("-" * 80)

    confirm = input("\nProceed with transfer? (y/n): ").strip().lower()

    if confirm == 'y':
        # Perform transfer
        success = perform_transfer(patient_id, patient_name, data_elements)

        if success:
            print("✅ Transfer completed successfully!")
            print("   View detailed logs in the logs/ directory")
        else:
            print("❌ Transfer failed. Check logs for details.")
            sys.exit(1)
    else:
        print("\n❌ Transfer cancelled by user")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    from typing import List
    main()
