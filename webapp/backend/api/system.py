"""
System Monitoring
Provides system resource usage and information
"""

import psutil
import logging
import docker

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitors system resources and Docker status"""

    def __init__(self):
        """Initialize system monitor"""
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None

    def get_system_info(self):
        """
        Get comprehensive system information

        Returns:
            dict: System resource usage and status
        """
        info = {
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "docker": self._get_docker_info(),
            "containers": self._get_container_stats()
        }
        return info

    def _get_cpu_info(self):
        """Get CPU usage information"""
        try:
            return {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(logical=True),
                "physical_count": psutil.cpu_count(logical=False)
            }
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return {"error": str(e)}

    def _get_memory_info(self):
        """Get memory usage information"""
        try:
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {"error": str(e)}

    def _get_disk_info(self):
        """Get disk usage for /home/containers"""
        try:
            # Check /home/containers partition
            usage = psutil.disk_usage('/home/containers' if psutil.disk_partitions() else '/')
            return {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent
            }
        except Exception as e:
            # Fallback to root partition
            try:
                usage = psutil.disk_usage('/')
                return {
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent,
                    "note": "Root partition (containers path not available)"
                }
            except Exception as e2:
                logger.error(f"Error getting disk info: {e2}")
                return {"error": str(e2)}

    def _get_docker_info(self):
        """Get Docker daemon information"""
        if not self.docker_client:
            return {"status": "unavailable"}

        try:
            info = self.docker_client.info()
            return {
                "status": "running",
                "containers_running": info.get('ContainersRunning', 0),
                "containers_stopped": info.get('ContainersStopped', 0),
                "containers_total": info.get('Containers', 0),
                "images": info.get('Images', 0),
                "server_version": info.get('ServerVersion', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error getting Docker info: {e}")
            return {"status": "error", "error": str(e)}

    def _get_container_stats(self):
        """Get basic stats for all running containers"""
        if not self.docker_client:
            return []

        try:
            containers = self.docker_client.containers.list()
            stats = []

            for container in containers:
                try:
                    # Get labels to identify openHomeStack services
                    labels = container.labels
                    service_name = labels.get('openhomestack.service', container.name)

                    stats.append({
                        "name": container.name,
                        "service": service_name,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown"
                    })
                except Exception as e:
                    logger.warning(f"Error getting stats for container {container.name}: {e}")

            return stats

        except Exception as e:
            logger.error(f"Error getting container stats: {e}")
            return []
