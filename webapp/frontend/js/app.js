/**
 * openHomeStack Frontend Application
 */

// Global state
let allServices = [];
let currentCategory = 'all';
let currentServiceForInstall = null;
let currentServiceForLogs = null;

// Icon mapping for services
const serviceIcons = {
    'film': 'fa-film',
    'gamepad': 'fa-gamepad',
    'shield': 'fa-shield-halved',
    'folder': 'fa-folder',
    'home': 'fa-home',
    'chart': 'fa-chart-line',
    'globe': 'fa-globe',
    'box': 'fa-box'
};

/**
 * Initialize the application
 */
async function init() {
    console.log('Initializing openHomeStack Dashboard...');

    // Set up category tab listeners
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const category = btn.dataset.category;
            switchCategory(category);

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Load initial data
    await loadServices();
    await loadSystemInfo();

    // Refresh system info every 5 seconds
    setInterval(loadSystemInfo, 5000);

    // Refresh services every 10 seconds
    setInterval(loadServices, 10000);
}

/**
 * Load all services from API
 */
async function loadServices() {
    try {
        const response = await API.getServices();
        allServices = response.services || [];

        // Fetch status for each service
        await Promise.all(allServices.map(async (service) => {
            try {
                const statusResponse = await API.getServiceStatus(service.id);
                service.status = statusResponse.status;
            } catch (error) {
                console.error(`Failed to load status for ${service.id}:`, error);
                service.status = { state: 'unknown' };
            }
        }));

        renderServices();
    } catch (error) {
        console.error('Failed to load services:', error);
        showError('Failed to load services. Is the backend API running?');
    }
}

/**
 * Load system information
 */
async function loadSystemInfo() {
    try {
        const response = await API.getSystemInfo();
        const system = response.system;

        document.getElementById('cpuUsage').textContent =
            system.cpu?.percent ? `${system.cpu.percent}%` : '--';

        document.getElementById('memUsage').textContent =
            system.memory?.percent ? `${system.memory.percent}%` : '--';

        document.getElementById('diskUsage').textContent =
            system.disk?.percent ? `${system.disk.percent}%` : '--';

        document.getElementById('containerCount').textContent =
            system.docker?.containers_running !== undefined ? `${system.docker.containers_running} running` : '--';

    } catch (error) {
        console.error('Failed to load system info:', error);
    }
}

/**
 * Render services in the table
 */
function renderServices() {
    const tbody = document.getElementById('servicesBody');

    // Filter services by category
    const filteredServices = currentCategory === 'all'
        ? allServices
        : allServices.filter(s => s.category === currentCategory);

    if (filteredServices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-cell">
                    <i class="fas fa-inbox"></i> No services found in this category
                </td>
            </tr>
        `;
        return;
    }

    // Sort: running first, then by name
    filteredServices.sort((a, b) => {
        const aRunning = a.status?.state === 'running' ? 0 : 1;
        const bRunning = b.status?.state === 'running' ? 0 : 1;
        if (aRunning !== bRunning) return aRunning - bRunning;
        return (a.name || '').localeCompare(b.name || '');
    });

    tbody.innerHTML = filteredServices.map(service => createServiceRow(service)).join('');
}

/**
 * Create HTML for a service table row
 */
function createServiceRow(service) {
    const icon = serviceIcons[service.icon] || 'fa-box';
    const status = service.status?.state || 'not_installed';
    const statusClass = getStatusClass(status);
    const statusText = formatStatus(status);

    return `
        <tr data-service-id="${service.id}">
            <td>
                <div class="service-name">
                    <i class="service-icon fas ${icon}"></i>
                    <span>${service.name || service.id}</span>
                </div>
            </td>
            <td>
                <span class="status-badge ${statusClass}">${statusText}</span>
            </td>
            <td>
                <span class="category-badge">${service.category || 'other'}</span>
            </td>
            <td>
                <span class="description-text">${service.description || ''}</span>
            </td>
            <td>
                <div class="action-buttons">
                    ${getServiceActions(service, status)}
                </div>
            </td>
        </tr>
    `;
}

/**
 * Get appropriate actions for a service based on its status
 */
function getServiceActions(service, status) {
    if (status === 'not_installed') {
        return `<button class="btn btn-primary" onclick="showInstallModal('${service.id}')">Install</button>`;
    }

    let actions = [];

    if (status === 'running') {
        if (service.url) {
            actions.push(`<button class="btn btn-success" onclick="openService('${service.url}')">Open</button>`);
        }
        actions.push(`<button class="btn btn-warning" onclick="stopService('${service.id}')">Stop</button>`);
        actions.push(`<button class="btn btn-secondary" onclick="showLogs('${service.id}')">Logs</button>`);
    } else if (status === 'exited' || status === 'stopped' || status === 'restarting') {
        actions.push(`<button class="btn btn-success" onclick="startService('${service.id}')">Start</button>`);
        actions.push(`<button class="btn btn-secondary" onclick="showLogs('${service.id}')">Logs</button>`);
    }

    actions.push(`<button class="btn btn-danger" onclick="removeService('${service.id}')">Remove</button>`);

    return actions.join('');
}

/**
 * Get CSS class for status
 */
function getStatusClass(status) {
    const statusMap = {
        'running': 'status-running',
        'exited': 'status-stopped',
        'stopped': 'status-stopped',
        'not_installed': 'status-not-installed',
        'restarting': 'status-restarting',
        'error': 'status-error'
    };
    return statusMap[status] || 'status-not-installed';
}

/**
 * Format status text
 */
function formatStatus(status) {
    const statusMap = {
        'running': 'Running',
        'exited': 'Stopped',
        'stopped': 'Stopped',
        'not_installed': 'Not Installed',
        'restarting': 'Restarting',
        'error': 'Error'
    };
    return statusMap[status] || 'Unknown';
}

/**
 * Switch category filter
 */
function switchCategory(category) {
    currentCategory = category;
    renderServices();
}

/**
 * Show install modal for a service
 */
async function showInstallModal(serviceId) {
    try {
        const response = await API.getService(serviceId);
        const service = response.service;
        currentServiceForInstall = service;

        document.getElementById('modalTitle').textContent = `Install ${service.name}`;

        const prompts = service.install_prompts || [];

        if (prompts.length === 0) {
            document.getElementById('modalBody').innerHTML = `
                <p>Ready to install <strong>${service.name}</strong>?</p>
                <p class="form-help">This service requires no additional configuration.</p>
            `;
        } else {
            const formHtml = prompts.map(prompt => `
                <div class="form-group">
                    <label for="input-${prompt.env_var}">${prompt.label}</label>
                    <input
                        type="text"
                        id="input-${prompt.env_var}"
                        name="${prompt.env_var}"
                        placeholder="Enter ${prompt.label.toLowerCase()}"
                    >
                </div>
            `).join('');

            document.getElementById('modalBody').innerHTML = formHtml;
        }

        document.getElementById('installModal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load service details:', error);
        showError('Failed to load service details');
    }
}

/**
 * Close install modal
 */
function closeInstallModal() {
    document.getElementById('installModal').style.display = 'none';
    currentServiceForInstall = null;
}

/**
 * Confirm and execute installation
 */
async function confirmInstall() {
    if (!currentServiceForInstall) return;

    const installBtn = document.getElementById('installBtn');
    installBtn.disabled = true;
    installBtn.textContent = 'Installing...';

    try {
        const envVars = {};
        const inputs = document.querySelectorAll('#modalBody input');
        inputs.forEach(input => {
            if (input.value) {
                envVars[input.name] = input.value;
            }
        });

        await API.installService(currentServiceForInstall.id, envVars);

        closeInstallModal();
        showSuccess(`${currentServiceForInstall.name} installed successfully!`);
        await loadServices();
    } catch (error) {
        console.error('Installation failed:', error);
        showError(`Failed to install ${currentServiceForInstall.name}: ${error.message}`);
    } finally {
        installBtn.disabled = false;
        installBtn.textContent = 'Install';
    }
}

/**
 * Start a service
 */
async function startService(serviceId) {
    try {
        await API.startService(serviceId);
        showSuccess('Service started');
        await loadServices();
    } catch (error) {
        showError(`Failed to start service: ${error.message}`);
    }
}

/**
 * Stop a service
 */
async function stopService(serviceId) {
    try {
        await API.stopService(serviceId);
        showSuccess('Service stopped');
        await loadServices();
    } catch (error) {
        showError(`Failed to stop service: ${error.message}`);
    }
}

/**
 * Remove a service
 */
async function removeService(serviceId) {
    if (!confirm('Remove this service? This will stop and remove the container(s).')) {
        return;
    }

    try {
        await API.removeService(serviceId, false);
        showSuccess('Service removed');
        await loadServices();
    } catch (error) {
        showError(`Failed to remove service: ${error.message}`);
    }
}

/**
 * Show logs modal
 */
async function showLogs(serviceId) {
    currentServiceForLogs = serviceId;

    const service = allServices.find(s => s.id === serviceId);
    document.getElementById('logsTitle').textContent = `${service?.name || serviceId} - Logs`;

    document.getElementById('logsModal').style.display = 'block';
    document.getElementById('logsContent').textContent = 'Loading logs...';

    await refreshLogs();
}

/**
 * Refresh logs in modal
 */
async function refreshLogs() {
    if (!currentServiceForLogs) return;

    try {
        const response = await API.getServiceLogs(currentServiceForLogs, 100);
        document.getElementById('logsContent').textContent = response.logs || 'No logs available';
    } catch (error) {
        document.getElementById('logsContent').textContent = `Error loading logs: ${error.message}`;
    }
}

/**
 * Close logs modal
 */
function closeLogsModal() {
    document.getElementById('logsModal').style.display = 'none';
    currentServiceForLogs = null;
}

/**
 * Open a service in new tab
 */
function openService(url) {
    window.open(url, '_blank');
}

/**
 * Show error message
 */
function showError(message) {
    alert(`Error: ${message}`);
}

/**
 * Show success message
 */
function showSuccess(message) {
    alert(message);
}

// Close modals when clicking outside
window.onclick = function(event) {
    const installModal = document.getElementById('installModal');
    const logsModal = document.getElementById('logsModal');

    if (event.target === installModal) {
        closeInstallModal();
    }
    if (event.target === logsModal) {
        closeLogsModal();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
