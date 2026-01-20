"""
API Routes
Defines all REST endpoints for service management
"""

from flask import Blueprint, jsonify, request
from api.services import ServiceManager
from api.containers import ContainerManager
from api.system import SystemMonitor
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize managers
service_manager = ServiceManager()
container_manager = ContainerManager()
system_monitor = SystemMonitor()


# ==================== Service Discovery ====================

@api_bp.route('/services', methods=['GET'])
def get_services():
    """
    Get list of all available services
    Returns service metadata from docker-compose labels
    """
    try:
        services = service_manager.discover_services()
        return jsonify({
            "success": True,
            "count": len(services),
            "services": services
        })
    except Exception as e:
        logger.error(f"Error discovering services: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>', methods=['GET'])
def get_service_detail(service_id):
    """
    Get detailed information about a specific service
    Includes installation prompts and current status
    """
    try:
        service = service_manager.get_service(service_id)
        if not service:
            return jsonify({
                "success": False,
                "error": f"Service '{service_id}' not found"
            }), 404

        # Add current container status
        status = container_manager.get_status(service_id)
        service['status'] = status

        return jsonify({
            "success": True,
            "service": service
        })
    except Exception as e:
        logger.error(f"Error getting service {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Container Management ====================

@api_bp.route('/services/<service_id>/install', methods=['POST'])
def install_service(service_id):
    """
    Install a service with user-provided configuration
    Expects JSON body with environment variables
    """
    try:
        data = request.get_json() or {}
        env_vars = data.get('env', {})

        result = container_manager.install(service_id, env_vars)

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error installing service {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>/start', methods=['POST'])
def start_service(service_id):
    """Start an installed service"""
    try:
        result = container_manager.start(service_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error starting service {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>/stop', methods=['POST'])
def stop_service(service_id):
    """Stop a running service"""
    try:
        result = container_manager.stop(service_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error stopping service {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>/restart', methods=['POST'])
def restart_service(service_id):
    """Restart a service"""
    try:
        result = container_manager.restart(service_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error restarting service {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>', methods=['DELETE'])
def remove_service(service_id):
    """
    Remove a service
    Stops and removes containers, optionally removes volumes
    """
    try:
        data = request.get_json() or {}
        remove_volumes = data.get('remove_volumes', False)

        result = container_manager.remove(service_id, remove_volumes)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error removing service {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Configuration ====================

@api_bp.route('/services/<service_id>/config', methods=['GET'])
def get_service_config(service_id):
    """Get current configuration for a service (volumes, environment)"""
    try:
        config = service_manager.get_service_config(service_id)
        if not config:
            return jsonify({
                "success": False,
                "error": f"Service '{service_id}' not found"
            }), 404

        return jsonify({
            "success": True,
            "config": config
        })
    except Exception as e:
        logger.error(f"Error getting config for {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>/config', methods=['PUT'])
def update_service_config(service_id):
    """
    Update service configuration and optionally restart
    Expects JSON body with volumes array and restart flag
    """
    try:
        data = request.get_json() or {}
        new_volumes = data.get('volumes', [])
        should_restart = data.get('restart', True)

        # Update the configuration
        result = service_manager.update_service_config(service_id, new_volumes)

        if not result['success']:
            return jsonify(result), 400

        # Restart the container if requested
        if should_restart:
            restart_result = container_manager.restart(service_id)
            if not restart_result['success']:
                return jsonify({
                    "success": True,
                    "message": "Configuration updated but restart failed",
                    "restart_error": restart_result.get('error')
                })

            return jsonify({
                "success": True,
                "message": "Configuration updated and service restarted"
            })

        return jsonify({
            "success": True,
            "message": "Configuration updated (restart not requested)"
        })

    except Exception as e:
        logger.error(f"Error updating config for {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== File Browser ====================

@api_bp.route('/browse', methods=['GET'])
def browse_directory():
    """
    Browse directories on the server
    Query param: path (default: /home or C:\\ on Windows)
    Returns list of subdirectories at the given path
    """
    import platform
    from pathlib import Path

    try:
        # Get the path to browse, default to home directory
        if platform.system() == 'Windows':
            default_path = 'C:\\'
        else:
            default_path = '/home'

        browse_path = request.args.get('path', default_path)
        path = Path(browse_path)

        if not path.exists():
            return jsonify({
                "success": False,
                "error": f"Path does not exist: {browse_path}"
            }), 404

        if not path.is_dir():
            return jsonify({
                "success": False,
                "error": f"Path is not a directory: {browse_path}"
            }), 400

        # Get parent directory (for navigation)
        parent = str(path.parent) if path.parent != path else None

        # List subdirectories only (not files)
        directories = []
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    directories.append({
                        "name": item.name,
                        "path": str(item)
                    })
        except PermissionError:
            pass  # Skip directories we can't read

        return jsonify({
            "success": True,
            "current_path": str(path),
            "parent_path": parent,
            "directories": directories
        })

    except Exception as e:
        logger.error(f"Error browsing directory: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Monitoring ====================

@api_bp.route('/services/<service_id>/status', methods=['GET'])
def get_service_status(service_id):
    """Get current status of a service"""
    try:
        status = container_manager.get_status(service_id)
        return jsonify({
            "success": True,
            "service_id": service_id,
            "status": status
        })
    except Exception as e:
        logger.error(f"Error getting status for {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/services/<service_id>/logs', methods=['GET'])
def get_service_logs(service_id):
    """
    Get container logs
    Query params: tail (default: 100), follow (default: false)
    """
    try:
        tail = request.args.get('tail', 100, type=int)
        follow = request.args.get('follow', 'false').lower() == 'true'

        logs = container_manager.get_logs(service_id, tail=tail, follow=follow)

        return jsonify({
            "success": True,
            "service_id": service_id,
            "logs": logs
        })
    except Exception as e:
        logger.error(f"Error getting logs for {service_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route('/system', methods=['GET'])
def get_system_info():
    """Get system resource usage and information"""
    try:
        info = system_monitor.get_system_info()
        return jsonify({
            "success": True,
            "system": info
        })
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
