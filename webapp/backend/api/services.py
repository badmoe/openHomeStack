"""
Service Discovery
Scans docker-compose files and parses openHomeStack labels
"""

import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages service discovery and metadata parsing"""

    def __init__(self, services_dir=None):
        """
        Initialize service manager

        Args:
            services_dir: Path to services directory (default: ../../services)
        """
        if services_dir is None:
            # Get path relative to this file
            backend_dir = Path(__file__).parent.parent
            repo_root = backend_dir.parent.parent
            services_dir = repo_root / 'services'

        self.services_dir = Path(services_dir)
        logger.info(f"ServiceManager initialized with services_dir: {self.services_dir}")

    def discover_services(self):
        """
        Discover all available services by scanning docker-compose files

        Returns:
            list: List of service metadata dictionaries
        """
        services = []

        if not self.services_dir.exists():
            logger.warning(f"Services directory not found: {self.services_dir}")
            return services

        # Scan each subdirectory for docker-compose.yml
        for service_dir in self.services_dir.iterdir():
            if not service_dir.is_dir():
                continue

            compose_file = service_dir / 'docker-compose.yml'
            if not compose_file.exists():
                logger.debug(f"No docker-compose.yml found in {service_dir.name}")
                continue

            try:
                service_metadata = self._parse_service(service_dir.name, compose_file)
                if service_metadata:
                    services.append(service_metadata)
                    logger.info(f"Discovered service: {service_metadata['id']}")
            except Exception as e:
                logger.error(f"Error parsing service {service_dir.name}: {e}")

        return sorted(services, key=lambda s: s.get('name', ''))

    def get_service(self, service_id):
        """
        Get detailed information about a specific service

        Args:
            service_id: Service identifier (directory name)

        Returns:
            dict: Service metadata or None if not found
        """
        service_dir = self.services_dir / service_id
        compose_file = service_dir / 'docker-compose.yml'

        if not compose_file.exists():
            logger.warning(f"Service not found: {service_id}")
            return None

        return self._parse_service(service_id, compose_file)

    def _parse_service(self, service_id, compose_file):
        """
        Parse docker-compose.yml and extract openHomeStack labels

        Args:
            service_id: Service identifier
            compose_file: Path to docker-compose.yml

        Returns:
            dict: Service metadata
        """
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)

            # Get the first service definition (most services have one container)
            services = compose_data.get('services', {})
            if not services:
                logger.warning(f"No services defined in {compose_file}")
                return None

            # Get the first service's labels
            first_service = list(services.values())[0]
            labels = first_service.get('labels', [])

            # Parse labels into metadata
            metadata = self._parse_labels(labels)
            metadata['id'] = service_id
            metadata['compose_file'] = str(compose_file)
            metadata['service_dir'] = str(compose_file.parent)

            # Add README content if available
            readme_file = compose_file.parent / 'README.md'
            if readme_file.exists():
                try:
                    with open(readme_file, 'r', encoding='utf-8') as f:
                        metadata['readme'] = f.read()
                except Exception as e:
                    logger.warning(f"Could not read README for {service_id}: {e}")

            return metadata

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {compose_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing {compose_file}: {e}")
            return None

    def _parse_labels(self, labels):
        """
        Parse openHomeStack labels into structured metadata

        Labels format:
            openhomestack.service=plex
            openhomestack.name=Plex Media Server
            openhomestack.description=Stream your media
            openhomestack.icon=film
            openhomestack.category=media
            openhomestack.url=http://localhost:32400/web
            openhomestack.install.prompt.claim_token=Plex Claim Token (optional)

        Args:
            labels: List of label strings or dict

        Returns:
            dict: Parsed metadata
        """
        metadata = {
            'name': '',
            'description': '',
            'icon': 'box',  # default icon
            'category': 'other',
            'url': None,
            'install_prompts': []
        }

        # Handle both list and dict formats
        if isinstance(labels, list):
            label_dict = {}
            for label in labels:
                if '=' in label:
                    key, value = label.split('=', 1)
                    label_dict[key] = value
        else:
            label_dict = labels

        # Parse standard labels
        for key, value in label_dict.items():
            if not key.startswith('openhomestack.'):
                continue

            parts = key.split('.')

            if len(parts) == 2:
                # Simple labels: openhomestack.name
                field = parts[1]
                metadata[field] = value

            elif len(parts) >= 4 and parts[1] == 'install' and parts[2] == 'prompt':
                # Installation prompts: openhomestack.install.prompt.claim_token
                prompt_key = '.'.join(parts[3:])
                metadata['install_prompts'].append({
                    'key': prompt_key,
                    'label': value,
                    'env_var': prompt_key.upper()
                })

        return metadata

    def get_compose_file_path(self, service_id):
        """
        Get the path to a service's docker-compose.yml file

        Args:
            service_id: Service identifier

        Returns:
            Path: Path to docker-compose.yml or None
        """
        compose_file = self.services_dir / service_id / 'docker-compose.yml'
        return compose_file if compose_file.exists() else None

    def get_service_dir(self, service_id):
        """
        Get the directory path for a service

        Args:
            service_id: Service identifier

        Returns:
            Path: Path to service directory
        """
        return self.services_dir / service_id
