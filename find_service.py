#!/usr/bin/env python3
"""
Quick Service Finder
Helps you find the Service ID for a specific service by name or keyword
"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient
import sys

load_dotenv()

def find_service(search_term):
    """Find services matching the search term"""

    client = GSMFusionClient()

    print(f"\nSearching for services matching: '{search_term}'")
    print("=" * 80)

    services = client.get_imei_services()

    # Filter services by search term
    matching_services = [
        s for s in services
        if search_term.lower() in s.title.lower() or
           search_term.lower() in s.category.lower()
    ]

    if not matching_services:
        print(f"No services found matching '{search_term}'")
        client.close()
        return

    print(f"\nFound {len(matching_services)} matching service(s):\n")

    for i, service in enumerate(matching_services, 1):
        print(f"{i}. Service ID: {service.package_id}")
        print(f"   Name: {service.title}")
        print(f"   Price: ${service.price}")
        print(f"   Delivery: {service.delivery_time}")
        print(f"   Category: {service.category}")
        print()
        print(f"   ➜ To submit: python3 gsm_cli.py submit <IMEI> {service.package_id}")
        print("-" * 80)

    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 find_service.py <search_term>")
        print("\nExamples:")
        print("  python3 find_service.py checker")
        print("  python3 find_service.py 'AT&T'")
        print("  python3 find_service.py 'T-Mobile'")
        print("  python3 find_service.py unlock")
        sys.exit(1)

    search_term = " ".join(sys.argv[1:])
    find_service(search_term)
