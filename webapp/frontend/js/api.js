/**
 * API Client for openHomeStack Backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

class API {
    /**
     * Make a fetch request with error handling
     */
    static async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    /**
     * Get all available services
     */
    static async getServices() {
        return await this.request('/services');
    }

    /**
     * Get details for a specific service
     */
    static async getService(serviceId) {
        return await this.request(`/services/${serviceId}`);
    }

    /**
     * Install a service
     */
    static async installService(serviceId, envVars = {}) {
        return await this.request(`/services/${serviceId}/install`, {
            method: 'POST',
            body: JSON.stringify({ env: envVars })
        });
    }

    /**
     * Start a service
     */
    static async startService(serviceId) {
        return await this.request(`/services/${serviceId}/start`, {
            method: 'POST'
        });
    }

    /**
     * Stop a service
     */
    static async stopService(serviceId) {
        return await this.request(`/services/${serviceId}/stop`, {
            method: 'POST'
        });
    }

    /**
     * Restart a service
     */
    static async restartService(serviceId) {
        return await this.request(`/services/${serviceId}/restart`, {
            method: 'POST'
        });
    }

    /**
     * Remove a service
     */
    static async removeService(serviceId, removeVolumes = false) {
        return await this.request(`/services/${serviceId}`, {
            method: 'DELETE',
            body: JSON.stringify({ remove_volumes: removeVolumes })
        });
    }

    /**
     * Get service status
     */
    static async getServiceStatus(serviceId) {
        return await this.request(`/services/${serviceId}/status`);
    }

    /**
     * Get service logs
     */
    static async getServiceLogs(serviceId, tail = 100) {
        return await this.request(`/services/${serviceId}/logs?tail=${tail}`);
    }

    /**
     * Get system information
     */
    static async getSystemInfo() {
        return await this.request('/system');
    }
}
