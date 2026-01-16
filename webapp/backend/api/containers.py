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
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None

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

        Returns:
            dict: Container status information
        """
        if not self.docker_client:
            return {"state": "unknown", "error": "Docker client not available"}

        try:
            # Find containers for this service
            containers = self.docker_client.containers.list(
                all=True,
                filters={"label": f"openhomestack.service={service_id}"}
            )

            if not containers:
                # Fallback: try to find by container name (usually same as service_id)
                try:
                    container = self.docker_client.containers.get(service_id)
                    containers = [container]
                except docker.errors.NotFound:
                    return {"state": "not_installed"}

            if not containers:
                return {"state": "not_installed"}

            # Get status of first container (most services have one)
            container = containers[0]
            container.reload()

            return {
                "state": container.status,  # running, paused, restarting, exited, etc.
                "id": container.id[:12],
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "created": container.attrs['Created'],
                "started_at": container.attrs.get('State', {}).get('StartedAt'),
            }

        except Exception as e:
            logger.error(f"Error getting status for {service_id}: {e}")
            return {"state": "error", "error": str(e)}

    def get_logs(self, service_id, tail=100, follow=False):
        """
        Get container logs

        Args:
            service_id: Service identifier
            tail: Number of lines to return
            follow: Stream logs (not implemented for HTTP response)

        Returns:
            str: Container logs
        """
        if not self.docker_client:
            return "Docker client not available"

        try:
            container = self.docker_client.containers.get(service_id)
            logs = container.logs(tail=tail, timestamps=True).decode('utf-8')
            return logs
        except docker.errors.NotFound:
            return f"Container '{service_id}' not found"
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
        Create /home/containers/{service_id} directory structure

        Args:
            service_id: Service identifier
        """
        base_path = Path(f"/home/containers/{service_id}")

        try:
            base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created data directory: {base_path}")

            # Set ownership to PUID:PGID (1000:1000)
            os.system(f"chown -R 1000:1000 {base_path}")

            # Special handling for specific services
            if service_id == 'plex':
                # Create media subdirectories
                for subdir in ['media/movies', 'media/tv', 'media/music', 'config', 'transcode']:
                    (base_path / subdir).mkdir(parents=True, exist_ok=True)
                os.system(f"chown -R 1000:1000 {base_path}")
                logger.info(f"Created Plex media directories")

        except Exception as e:
            logger.error(f"Error creating data directories for {service_id}: {e}")
            raise

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
