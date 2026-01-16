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
