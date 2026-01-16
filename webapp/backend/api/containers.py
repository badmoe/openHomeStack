"""
Container Management
Handles docker-compose operations for service lifecycle
"""

import os
import subprocess
import logging
from pathlib import Path
import docker
from api.services import ServiceManager

logger = logging.getLogger(__name__)


class ContainerManager:
    """Manages container lifecycle using docker-compose and docker SDK"""

    def __init__(self):
        """Initialize container manager"""
        self.service_manager = ServiceManager()
        self._docker_client = None

    @property
    def docker_client(self):
        """Lazy initialization of Docker client"""
        if self._docker_client is None:
            try:
                self._docker_client = docker.from_env()
                logger.info("Docker client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Docker client: {e}")
                self._docker_client = None
        return self._docker_client

    def install(self, service_id, env_vars=None):
        """
        Install a service with optional environment variables

        Args:
            service_id: Service identifier
            env_vars: Dict of environment variables for the service

        Returns:
            dict: Result with success status and message
        """
        env_vars = env_vars or {}

        try:
            service_dir = self.service_manager.get_service_dir(service_id)
            compose_file = self.service_manager.get_compose_file_path(service_id)

            if not compose_file:
                return {
                    "success": False,
                    "error": f"Service '{service_id}' not found"
                }

            # Create container data directories
            self._create_data_directories(service_id)

            # Create .env file if environment variables provided
            if env_vars:
                self._create_env_file(service_dir, env_vars)

            # Run docker-compose up -d
            result = self._run_compose_command(
                service_dir,
                ['up', '-d'],
                f"Installing {service_id}"
            )

            if result['success']:
                return {
                    "success": True,
                    "message": f"Service '{service_id}' installed successfully",
                    "service_id": service_id
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error installing service {service_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def start(self, service_id):
        """Start a stopped service"""
        try:
            service_dir = self.service_manager.get_service_dir(service_id)

            result = self._run_compose_command(
                service_dir,
                ['start'],
                f"Starting {service_id}"
            )

            if result['success']:
                return {
                    "success": True,
                    "message": f"Service '{service_id}' started successfully",
                    "service_id": service_id
                }
            return result

        except Exception as e:
            logger.error(f"Error starting service {service_id}: {e}")
            return {"success": False, "error": str(e)}

    def stop(self, service_id):
        """Stop a running service"""
        try:
            service_dir = self.service_manager.get_service_dir(service_id)

            result = self._run_compose_command(
                service_dir,
                ['stop'],
                f"Stopping {service_id}"
            )

            if result['success']:
                return {
                    "success": True,
                    "message": f"Service '{service_id}' stopped successfully",
                    "service_id": service_id
                }
            return result

        except Exception as e:
            logger.error(f"Error stopping service {service_id}: {e}")
            return {"success": False, "error": str(e)}

    def restart(self, service_id):
        """Restart a service"""
        try:
            service_dir = self.service_manager.get_service_dir(service_id)

            result = self._run_compose_command(
                service_dir,
                ['restart'],
                f"Restarting {service_id}"
            )

            if result['success']:
                return {
                    "success": True,
                    "message": f"Service '{service_id}' restarted successfully",
                    "service_id": service_id
                }
            return result

        except Exception as e:
            logger.error(f"Error restarting service {service_id}: {e}")
            return {"success": False, "error": str(e)}

    def remove(self, service_id, remove_volumes=False):
        """
        Remove a service

        Args:
            service_id: Service identifier
            remove_volumes: Whether to remove volumes (data)

        Returns:
            dict: Result with success status
        """
        try:
            service_dir = self.service_manager.get_service_dir(service_id)

            cmd = ['down']
            if remove_volumes:
                cmd.append('-v')

            result = self._run_compose_command(
                service_dir,
                cmd,
                f"Removing {service_id}"
            )

            if result['success']:
                # Also remove .env file if it exists
                env_file = service_dir / '.env'
                if env_file.exists():
                    env_file.unlink()
                    logger.info(f"Removed .env file for {service_id}")

                return {
                    "success": True,
                    "message": f"Service '{service_id}' removed successfully",
                    "service_id": service_id,
                    "volumes_removed": remove_volumes
                }
            return result

        except Exception as e:
            logger.error(f"Error removing service {service_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_status(self, service_id):
        """
        Get current status of service containers
        Uses docker CLI with label filtering to find containers belonging to a service

        Returns:
            dict: Container status information
        """
        try:
            # Use label filter to find containers belonging to this service
            # This handles services where container_name differs from service_id
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', f'label=openhomestack.service={service_id}',
                 '--format', '{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.ID}}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {"state": "unknown", "error": "Docker command failed"}

            output = result.stdout.strip()
            if not output:
                return {"state": "not_installed"}

            # Parse the output - may have multiple containers for multi-container services
            containers = []
            for line in output.split('\n'):
                if not line.strip():
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    name = parts[0]
                    status = parts[1]
                    image = parts[2] if len(parts) > 2 else "unknown"
                    container_id = parts[3] if len(parts) > 3 else "unknown"

                    # Determine state from status string
                    status_lower = status.lower()
                    if 'up' in status_lower:
                        state = 'running'
                    elif 'exited' in status_lower:
                        state = 'exited'
                    elif 'paused' in status_lower:
                        state = 'paused'
                    elif 'restarting' in status_lower:
                        state = 'restarting'
                    elif 'created' in status_lower:
                        state = 'created'
                    else:
                        state = 'unknown'

                    containers.append({
                        "state": state,
                        "id": container_id[:12] if len(container_id) >= 12 else container_id,
                        "name": name,
                        "image": image,
                        "status_text": status
                    })

            if not containers:
                return {"state": "not_installed"}

            # For single container services, return simple status
            if len(containers) == 1:
                return containers[0]

            # For multi-container services, determine overall state
            # Running if any container is running, otherwise use first container's state
            states = [c['state'] for c in containers]
            if 'running' in states:
                overall_state = 'running'
            elif 'restarting' in states:
                overall_state = 'restarting'
            elif all(s == 'exited' for s in states):
                overall_state = 'exited'
            else:
                overall_state = containers[0]['state']

            return {
                "state": overall_state,
                "containers": containers,
                "container_count": len(containers)
            }

        except Exception as e:
            logger.error(f"Error getting status for {service_id}: {e}")
            return {"state": "error", "error": str(e)}

    def get_logs(self, service_id, tail=100, follow=False):
        """
        Get container logs using docker CLI

        Args:
            service_id: Service identifier
            tail: Number of lines to return
            follow: Stream logs (not implemented for HTTP response)

        Returns:
            str: Container logs
        """
        try:
            # First, find the container(s) by label
            find_result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', f'label=openhomestack.service={service_id}',
                 '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if find_result.returncode != 0:
                return f"Error finding containers: {find_result.stderr}"

            container_names = [n.strip() for n in find_result.stdout.strip().split('\n') if n.strip()]

            if not container_names:
                return f"No containers found for service '{service_id}'"

            # Get logs from all containers (useful for multi-container services)
            all_logs = []
            for container_name in container_names:
                result = subprocess.run(
                    ['docker', 'logs', container_name, '--tail', str(tail), '--timestamps'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    if len(container_names) > 1:
                        all_logs.append(f"=== {container_name} ===\n{result.stdout}")
                    else:
                        all_logs.append(result.stdout)
                else:
                    all_logs.append(f"=== {container_name} ===\nError: {result.stderr}")

            return '\n'.join(all_logs)

        except Exception as e:
            logger.error(f"Error getting logs for {service_id}: {e}")
            return f"Error: {str(e)}"

    def _run_compose_command(self, service_dir, args, description="Docker compose"):
        """
        Run a docker-compose command

        Args:
            service_dir: Path to service directory
            args: List of command arguments
            description: Description for logging

        Returns:
            dict: Result with success status and output
        """
        try:
            cmd = ['docker-compose'] + args
            logger.info(f"{description}: {' '.join(cmd)} in {service_dir}")

            result = subprocess.run(
                cmd,
                cwd=service_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                logger.info(f"{description} completed successfully")
                return {
                    "success": True,
                    "output": result.stdout
                }
            else:
                logger.error(f"{description} failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "returncode": result.returncode
                }

        except subprocess.TimeoutExpired:
            logger.error(f"{description} timed out")
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            logger.error(f"{description} error: {e}")
            return {"success": False, "error": str(e)}

    def _create_data_directories(self, service_id):
        """
        Create /home/containers/{service_id} directory structure and deploy default configs

        Args:
            service_id: Service identifier
        """
        import platform
        import shutil

        if platform.system() == 'Windows':
            base_path = Path(f"C:\\containers\\{service_id}")
        else:
            base_path = Path(f"/home/containers/{service_id}")

        try:
            base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created data directory: {base_path}")

            # Get service directory for config templates
            service_dir = self.service_manager.get_service_dir(service_id)
            config_template_dir = service_dir / 'config'

            # Deploy default config files if they exist in the service directory
            if config_template_dir.exists() and config_template_dir.is_dir():
                self._deploy_config_files(service_id, config_template_dir, base_path)

            # Special handling for specific services
            if service_id == 'plex':
                for subdir in ['media/movies', 'media/tv', 'media/music', 'config', 'transcode']:
                    (base_path / subdir).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created Plex media directories")

            elif service_id == 'dns':
                (base_path / 'config').mkdir(parents=True, exist_ok=True)

            elif service_id == 'monitoring':
                for subdir in ['prometheus', 'prometheus-config', 'grafana']:
                    (base_path / subdir).mkdir(parents=True, exist_ok=True)

            elif service_id == 'pihole':
                for subdir in ['etc-pihole', 'etc-dnsmasq.d']:
                    (base_path / subdir).mkdir(parents=True, exist_ok=True)

            elif service_id == 'homeassistant':
                (base_path / 'config').mkdir(parents=True, exist_ok=True)

            elif service_id == 'gaming-vpn':
                (base_path / 'config').mkdir(parents=True, exist_ok=True)

            # Set ownership to PUID:PGID (1000:1000) - only on Linux
            if platform.system() != 'Windows':
                os.system(f"chown -R 1000:1000 {base_path}")

        except Exception as e:
            logger.error(f"Error creating data directories for {service_id}: {e}")
            raise

    def _deploy_config_files(self, service_id, config_template_dir, base_path):
        """
        Deploy default configuration files from service template directory

        Args:
            service_id: Service identifier
            config_template_dir: Path to config templates in service directory
            base_path: Destination base path for container data
        """
        import shutil

        try:
            # Map service configs to their deployment locations
            config_mappings = {
                'dns': {'config/Corefile': 'config/Corefile'},
                'monitoring': {'config/prometheus.yml': 'prometheus-config/prometheus.yml'},
            }

            mappings = config_mappings.get(service_id, {})

            for src_rel, dst_rel in mappings.items():
                src_path = config_template_dir.parent / src_rel
                dst_path = base_path / dst_rel

                if src_path.exists():
                    # Create destination directory if needed
                    dst_path.parent.mkdir(parents=True, exist_ok=True)

                    # Only copy if destination doesn't exist (don't overwrite user configs)
                    if not dst_path.exists():
                        shutil.copy2(src_path, dst_path)
                        logger.info(f"Deployed config: {src_rel} -> {dst_path}")
                    else:
                        logger.info(f"Config already exists, skipping: {dst_path}")

        except Exception as e:
            logger.warning(f"Error deploying config files for {service_id}: {e}")

    def _create_env_file(self, service_dir, env_vars):
        """
        Create .env file from user-provided environment variables

        Args:
            service_dir: Path to service directory
            env_vars: Dict of environment variables
        """
        env_file_path = service_dir / '.env'

        try:
            with open(env_file_path, 'w') as f:
                for key, value in env_vars.items():
                    # Only write non-empty values
                    if value:
                        f.write(f"{key.upper()}={value}\n")

            logger.info(f"Created .env file for service in {service_dir}")

        except Exception as e:
            logger.error(f"Error creating .env file: {e}")
            raise
