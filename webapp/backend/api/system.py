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
        """Get Docker daemon information using CLI"""
        import subprocess

        try:
            # Check if docker is running
            result = subprocess.run(
                ['docker', 'info', '--format', '{{.Containers}}\t{{.ContainersRunning}}\t{{.ContainersStopped}}\t{{.Images}}\t{{.ServerVersion}}'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return {"status": "unavailable"}

            parts = result.stdout.strip().split('\t')
            if len(parts) >= 5:
                return {
                    "status": "running",
                    "containers_total": int(parts[0]),
                    "containers_running": int(parts[1]),
                    "containers_stopped": int(parts[2]),
                    "images": int(parts[3]),
                    "server_version": parts[4]
                }

            return {"status": "running"}

        except Exception as e:
            logger.error(f"Error getting Docker info: {e}")
            return {"status": "unavailable"}

    def _get_container_stats(self):
        """Get basic stats for all running containers using CLI"""
        import subprocess

        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}\t{{.Image}}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            stats = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('\t')
                if len(parts) >= 3:
                    name = parts[0]
                    status = parts[1]
                    image = parts[2]

                    # Extract service name (usually same as container name)
                    stats.append({
                        "name": name,
                        "service": name,  # Could enhance this by checking labels
                        "status": "running" if "Up" in status else "unknown",
                        "image": image
                    })

            return stats

        except Exception as e:
            logger.error(f"Error getting container stats: {e}")
            return []
