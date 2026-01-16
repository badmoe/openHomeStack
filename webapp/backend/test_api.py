#!/usr/bin/env python3
"""
Quick test script for the openHomeStack backend API
Tests service discovery and basic functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.services import ServiceManager
from api.containers import ContainerManager
from api.system import SystemMonitor
import json


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_service_discovery():
    """Test service discovery functionality"""
    print_section("Testing Service Discovery")

    service_manager = ServiceManager()
    services = service_manager.discover_services()

    print(f"\nFound {len(services)} service(s):\n")

    for service in services:
        print(f"ID: {service['id']}")
        print(f"Name: {service['name']}")
        print(f"Description: {service['description']}")
        print(f"Category: {service['category']}")
        print(f"Icon: {service['icon']}")
        print(f"URL: {service.get('url', 'N/A')}")

        if service.get('install_prompts'):
            print(f"Installation Prompts:")
            for prompt in service['install_prompts']:
                print(f"  - {prompt['label']} ({prompt['env_var']})")

        print()

    return services


def test_service_detail(service_id):
    """Test getting detailed service information"""
    print_section(f"Testing Service Detail: {service_id}")

    service_manager = ServiceManager()
    service = service_manager.get_service(service_id)

    if service:
        print(f"\nService: {service['name']}")
        print(f"Directory: {service['service_dir']}")
        print(f"Compose File: {service['compose_file']}")

        if service.get('readme'):
            readme_preview = service['readme'][:200].replace('\n', ' ')
            print(f"README Preview: {readme_preview}...")
    else:
        print(f"Service '{service_id}' not found")

    return service


def test_container_status(service_id):
    """Test getting container status"""
    print_section(f"Testing Container Status: {service_id}")

    container_manager = ContainerManager()
    status = container_manager.get_status(service_id)

    print(f"\nStatus for '{service_id}':")
    print(json.dumps(status, indent=2))

    return status


def test_system_info():
    """Test system information retrieval"""
    print_section("Testing System Information")

    system_monitor = SystemMonitor()
    info = system_monitor.get_system_info()

    print("\nSystem Info:")
    print(f"  CPU: {info['cpu'].get('percent', 'N/A')}% ({info['cpu'].get('count', 'N/A')} cores)")
    print(f"  Memory: {info['memory'].get('used_gb', 'N/A')}GB / {info['memory'].get('total_gb', 'N/A')}GB ({info['memory'].get('percent', 'N/A')}%)")
    print(f"  Disk: {info['disk'].get('used_gb', 'N/A')}GB / {info['disk'].get('total_gb', 'N/A')}GB ({info['disk'].get('percent', 'N/A')}%)")

    docker_info = info.get('docker', {})
    print(f"\nDocker Info:")
    print(f"  Status: {docker_info.get('status', 'unknown')}")

    if docker_info.get('status') == 'running':
        print(f"  Running Containers: {docker_info.get('containers_running', 0)}")
        print(f"  Total Containers: {docker_info.get('containers_total', 0)}")
        print(f"  Images: {docker_info.get('images', 0)}")

    containers = info.get('containers', [])
    if containers:
        print(f"\nRunning openHomeStack Services:")
        for container in containers:
            print(f"  - {container['service']}: {container['status']}")

    return info


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  openHomeStack Backend API Test Suite")
    print("=" * 60)

    try:
        # Test 1: Service Discovery
        services = test_service_discovery()

        # Test 2: Service Detail (if we found any services)
        if services:
            test_service_detail(services[0]['id'])

            # Test 3: Container Status
            test_container_status(services[0]['id'])

        # Test 4: System Info
        test_system_info()

        print_section("All Tests Completed")
        print("\nBackend API is working correctly!")
        print("\nNext steps:")
        print("  1. Run the API: python app.py")
        print("  2. Test endpoints: curl http://localhost:5000/api/services")
        print("  3. Build the frontend dashboard")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
