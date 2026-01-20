/**
 * openHomeStack Frontend Application
 * Version: 1.2 (with DNS warning feature)
 */

// Global state
let allServices = [];
let currentCategory = 'all';
let currentServiceForInstall = null;
let currentServiceForLogs = null;

// Wizard state
let wizardStep = 1;
let wizardSelectedCategory = null;
let wizardSelectedService = null;

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

// Category icons and display names
const categoryConfig = {
    'media': { icon: 'fa-film', name: 'Media' },
    'dns': { icon: 'fa-shield-halved', name: 'DNS & Ad Blocking' },
    'networking': { icon: 'fa-network-wired', name: 'Networking' },
    'automation': { icon: 'fa-home', name: 'Automation' },
    'management': { icon: 'fa-chart-line', name: 'Management' },
    'other': { icon: 'fa-box', name: 'Other' }
};

/**
 * Initialize the application
 */
async function init() {
    console.log('openHomeStack Dashboard v1.2 - Initializing...');

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
 * Get installed services (not_installed filtered out)
 */
function getInstalledServices() {
    return allServices.filter(s => s.status?.state && s.status.state !== 'not_installed');
}

/**
 * Get available (not installed) services
 */
function getAvailableServices() {
    return allServices.filter(s => !s.status?.state || s.status.state === 'not_installed');
}

/**
 * Get available services grouped by category
 */
function getAvailableServicesByCategory() {
    const available = getAvailableServices();
    const grouped = {};

    available.forEach(service => {
        const cat = service.category || 'other';
        if (!grouped[cat]) {
            grouped[cat] = [];
        }
        grouped[cat].push(service);
    });

    return grouped;
}

/**
 * Render services in the table (only installed services)
 */
function renderServices() {
    const tbody = document.getElementById('servicesBody');

    // Get only installed services
    const installedServices = getInstalledServices();

    // Filter by category
    const filteredServices = currentCategory === 'all'
        ? installedServices
        : installedServices.filter(s => s.category === currentCategory);

    if (filteredServices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-cell">
                    <i class="fas fa-inbox"></i> No services installed${currentCategory !== 'all' ? ' in this category' : ''}
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

    // Add Configure button for all installed services
    actions.push(`<button class="btn btn-secondary" onclick="showConfigModal('${service.id}')">Configure</button>`);
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

// ============================================
// Wizard Functions
// ============================================

/**
 * Show Add Service wizard modal
 */
async function showAddServiceModal() {
    // Refresh services to get latest status before showing wizard
    await loadServices();

    // Reset wizard state
    wizardStep = 1;
    wizardSelectedCategory = null;
    wizardSelectedService = null;

    // Update UI
    updateWizardStep();
    populateWizardStep1();

    document.getElementById('addServiceModal').style.display = 'block';
}

/**
 * Close Add Service modal
 */
function closeAddServiceModal() {
    document.getElementById('addServiceModal').style.display = 'none';
    wizardStep = 1;
    wizardSelectedCategory = null;
    wizardSelectedService = null;
}

/**
 * Update wizard step indicators and visibility
 */
function updateWizardStep() {
    // Update step indicators
    document.querySelectorAll('.wizard-step').forEach(stepEl => {
        const step = parseInt(stepEl.dataset.step);
        stepEl.classList.remove('active', 'completed');
        if (step === wizardStep) {
            stepEl.classList.add('active');
        } else if (step < wizardStep) {
            stepEl.classList.add('completed');
        }
    });

    // Update content visibility
    document.getElementById('wizardStep1').style.display = wizardStep === 1 ? 'block' : 'none';
    document.getElementById('wizardStep2').style.display = wizardStep === 2 ? 'block' : 'none';
    document.getElementById('wizardStep3').style.display = wizardStep === 3 ? 'block' : 'none';

    // Update buttons
    const backBtn = document.getElementById('wizardBackBtn');
    const nextBtn = document.getElementById('wizardNextBtn');
    const installBtn = document.getElementById('wizardInstallBtn');

    backBtn.style.display = wizardStep > 1 ? 'inline-block' : 'none';
    nextBtn.style.display = wizardStep < 3 ? 'inline-block' : 'none';
    installBtn.style.display = wizardStep === 3 ? 'inline-block' : 'none';

    // Update title
    const titles = {
        1: 'Add Service - Select Category',
        2: 'Add Service - Select Service',
        3: `Install ${wizardSelectedService?.name || 'Service'}`
    };
    document.getElementById('wizardTitle').textContent = titles[wizardStep];
}

/**
 * Populate Step 1: Category Selection
 */
function populateWizardStep1() {
    const grouped = getAvailableServicesByCategory();
    const categoryList = document.getElementById('categoryList');

    if (Object.keys(grouped).length === 0) {
        categoryList.innerHTML = `
            <div class="no-services-available">
                <i class="fas fa-check-circle"></i>
                <p>All available services are already installed!</p>
            </div>
        `;
        document.getElementById('wizardNextBtn').style.display = 'none';
        return;
    }

    // Sort categories
    const sortedCategories = Object.keys(grouped).sort((a, b) => {
        const nameA = categoryConfig[a]?.name || a;
        const nameB = categoryConfig[b]?.name || b;
        return nameA.localeCompare(nameB);
    });

    categoryList.innerHTML = sortedCategories.map(cat => {
        const config = categoryConfig[cat] || { icon: 'fa-box', name: cat };
        const count = grouped[cat].length;
        const selected = wizardSelectedCategory === cat ? 'selected' : '';

        return `
            <div class="category-item ${selected}" onclick="selectCategory('${cat}')">
                <i class="category-icon fas ${config.icon}"></i>
                <div class="category-info">
                    <div class="category-name">${config.name}</div>
                    <div class="category-count">${count} service${count !== 1 ? 's' : ''} available</div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Select a category in step 1
 */
function selectCategory(category) {
    wizardSelectedCategory = category;

    // Update UI to show selection
    document.querySelectorAll('.category-item').forEach(el => {
        el.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    // Check for DNS conflict warning (case-insensitive comparison)
    if (category.toLowerCase() === 'dns') {
        const installedServices = getInstalledServices();
        const installedDnsServices = installedServices.filter(s =>
            s.category && s.category.toLowerCase() === 'dns'
        );

        if (installedDnsServices.length > 0) {
            const installedNames = installedDnsServices.map(s => s.name || s.id).join(', ');
            showDnsWarning(installedNames);
            return; // Don't auto-advance until they acknowledge
        }
    }

    // Proceed to service selection step
    proceedWithCategorySelection(category);
}

/**
 * Proceed with category selection (after warning acknowledged or no warning needed)
 */
function proceedWithCategorySelection(category) {
    // Always show step 2 (service selection)
    wizardStep = 2;
    updateWizardStep();
    populateWizardStep2();
}

/**
 * Show DNS conflict warning
 */
function showDnsWarning(installedNames) {
    const warningHtml = `
        <div class="dns-warning">
            <div class="dns-warning-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="dns-warning-content">
                <h3>DNS Service Already Installed</h3>
                <p>You already have <strong>${installedNames}</strong> installed.</p>
                <p>Running multiple DNS services simultaneously can cause port conflicts and unexpected network behavior. Consider removing the existing DNS service before installing a new one, or ensure they are configured to use different ports.</p>
            </div>
            <div class="dns-warning-actions">
                <button class="btn btn-secondary" onclick="dismissDnsWarning()">Go Back</button>
                <button class="btn btn-warning" onclick="acknowledgeDnsWarning()">Continue Anyway</button>
            </div>
        </div>
    `;

    document.getElementById('wizardStep1').innerHTML = warningHtml;
    document.getElementById('wizardNextBtn').style.display = 'none';
}

/**
 * Restore the wizard step 1 structure (after warning replaced it)
 */
function restoreWizardStep1Structure() {
    document.getElementById('wizardStep1').innerHTML = `
        <p class="wizard-instruction">Select a service category:</p>
        <div class="category-list" id="categoryList">
        </div>
    `;
}

/**
 * Dismiss DNS warning and go back to category selection
 */
function dismissDnsWarning() {
    wizardSelectedCategory = null;
    restoreWizardStep1Structure();
    populateWizardStep1();
    document.getElementById('wizardNextBtn').style.display = 'inline-block';
}

/**
 * Acknowledge DNS warning and continue
 */
function acknowledgeDnsWarning() {
    restoreWizardStep1Structure();
    populateWizardStep1();
    document.getElementById('wizardNextBtn').style.display = 'inline-block';

    // Re-select the DNS category visually
    document.querySelectorAll('.category-item').forEach(el => {
        if (el.textContent.includes('DNS')) {
            el.classList.add('selected');
        }
    });

    // Proceed with the selection
    proceedWithCategorySelection(wizardSelectedCategory);
}

/**
 * Populate Step 2: Service Selection
 */
function populateWizardStep2() {
    const grouped = getAvailableServicesByCategory();
    const services = grouped[wizardSelectedCategory] || [];
    const serviceList = document.getElementById('serviceList');

    serviceList.innerHTML = services.map(service => {
        const icon = serviceIcons[service.icon] || 'fa-box';
        const selected = wizardSelectedService?.id === service.id ? 'selected' : '';

        return `
            <div class="available-service-item ${selected}" onclick="selectService('${service.id}')">
                <i class="available-service-icon fas ${icon}"></i>
                <div class="available-service-info">
                    <div class="available-service-name">${service.name || service.id}</div>
                    <div class="available-service-description">${service.description || ''}</div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Select a service in step 2
 */
function selectService(serviceId) {
    const available = getAvailableServices();
    wizardSelectedService = available.find(s => s.id === serviceId);

    // Update UI to show selection
    document.querySelectorAll('.available-service-item').forEach(el => {
        el.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

/**
 * Populate Step 3: Configuration Form
 */
async function populateWizardStep3() {
    const configForm = document.getElementById('configForm');

    if (!wizardSelectedService) {
        configForm.innerHTML = '<p>No service selected.</p>';
        return;
    }

    try {
        // Fetch full service details including install prompts
        const response = await API.getService(wizardSelectedService.id);
        const service = response.service;
        wizardSelectedService = service; // Update with full details

        const prompts = service.install_prompts || [];

        if (prompts.length === 0) {
            configForm.innerHTML = `
                <p>Ready to install <strong>${service.name}</strong>?</p>
                <p class="form-help">This service requires no additional configuration.</p>
            `;
        } else {
            const formHtml = prompts.map(prompt => `
                <div class="form-group">
                    <label for="wizard-input-${prompt.env_var}">${prompt.label}</label>
                    <input
                        type="text"
                        id="wizard-input-${prompt.env_var}"
                        name="${prompt.env_var}"
                        class="wizard-input"
                        placeholder="Enter ${prompt.label.toLowerCase()}"
                    >
                </div>
            `).join('');

            configForm.innerHTML = formHtml;
        }
    } catch (error) {
        console.error('Failed to load service details:', error);
        configForm.innerHTML = '<p>Failed to load service configuration.</p>';
    }
}

/**
 * Go back one step in the wizard
 */
function wizardBack() {
    if (wizardStep > 1) {
        wizardStep--;
        updateWizardStep();

        if (wizardStep === 1) {
            populateWizardStep1();
        } else if (wizardStep === 2) {
            populateWizardStep2();
        }
    }
}

/**
 * Go to next step in the wizard
 */
function wizardNext() {
    if (wizardStep === 1) {
        if (!wizardSelectedCategory) {
            showError('Please select a category');
            return;
        }
        wizardStep = 2;
        updateWizardStep();
        populateWizardStep2();
    } else if (wizardStep === 2) {
        if (!wizardSelectedService) {
            showError('Please select a service');
            return;
        }
        wizardStep = 3;
        updateWizardStep();
        populateWizardStep3();
    }
}

/**
 * Execute installation from wizard
 */
async function wizardInstall() {
    if (!wizardSelectedService) {
        showError('No service selected');
        return;
    }

    const installBtn = document.getElementById('wizardInstallBtn');
    installBtn.disabled = true;
    installBtn.textContent = 'Installing...';

    // Save service info before closing modal (which resets wizardSelectedService)
    const serviceName = wizardSelectedService.name || wizardSelectedService.id;
    const serviceId = wizardSelectedService.id;

    try {
        const envVars = {};
        const inputs = document.querySelectorAll('#configForm .wizard-input');
        inputs.forEach(input => {
            if (input.value) {
                envVars[input.name] = input.value;
            }
        });

        await API.installService(serviceId, envVars);

        closeAddServiceModal();
        showSuccess(`${serviceName} installed successfully!`);
        await loadServices();
    } catch (error) {
        console.error('Installation failed:', error);
        showError(`Failed to install ${serviceName}: ${error.message}`);
    } finally {
        installBtn.disabled = false;
        installBtn.textContent = 'Install';
    }
}

// ============================================
// Legacy Install Modal (keeping for compatibility)
// ============================================

/**
 * Show install modal for a service (legacy - now uses wizard)
 */
async function showInstallModal(serviceId) {
    // Use the wizard instead
    const available = getAvailableServices();
    const service = available.find(s => s.id === serviceId);

    if (service) {
        wizardSelectedCategory = service.category;
        wizardSelectedService = service;
        wizardStep = 3;

        showAddServiceModal();
        updateWizardStep();
        await populateWizardStep3();
    }
}

/**
 * Close install modal (legacy)
 */
function closeInstallModal() {
    document.getElementById('installModal').style.display = 'none';
    currentServiceForInstall = null;
}

/**
 * Confirm and execute installation (legacy)
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

// ============================================
// Service Actions
// ============================================

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

// ============================================
// Configuration Modal
// ============================================

let currentServiceForConfig = null;
let currentConfigVolumes = [];

/**
 * Show configuration modal for a service
 */
async function showConfigModal(serviceId) {
    currentServiceForConfig = serviceId;

    const service = allServices.find(s => s.id === serviceId);
    document.getElementById('configTitle').textContent = `Configure ${service?.name || serviceId}`;

    document.getElementById('configModal').style.display = 'block';
    document.getElementById('volumesList').innerHTML = '<p>Loading configuration...</p>';

    try {
        const response = await API.getServiceConfig(serviceId);
        currentConfigVolumes = response.config.volumes || [];
        renderVolumesList();
    } catch (error) {
        document.getElementById('volumesList').innerHTML = `<p>Error loading configuration: ${error.message}</p>`;
    }
}

/**
 * Render the volumes list in the config modal
 */
function renderVolumesList() {
    const volumesList = document.getElementById('volumesList');

    if (currentConfigVolumes.length === 0) {
        volumesList.innerHTML = '<p>No volume mappings configured for this service.</p>';
        return;
    }

    volumesList.innerHTML = currentConfigVolumes.map((vol, index) => `
        <div class="volume-item">
            <div class="volume-item-header">
                <i class="fas fa-folder"></i>
                <span>Container path: ${vol.container_path}</span>
            </div>
            <div class="volume-paths">
                <div class="volume-path-row">
                    <label>Host path:</label>
                    <input type="text"
                           id="volume-host-${index}"
                           value="${vol.host_path}"
                           data-index="${index}"
                           onchange="updateVolumeHost(${index}, this.value)">
                    <button class="browse-btn" onclick="openBrowseModal(${index})" title="Browse">
                        <i class="fas fa-folder-open"></i>
                    </button>
                </div>
                <div class="volume-path-row">
                    <label>Container:</label>
                    <input type="text" value="${vol.container_path}" disabled>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Update a volume's host path
 */
function updateVolumeHost(index, newPath) {
    if (currentConfigVolumes[index]) {
        currentConfigVolumes[index].host_path = newPath;
    }
}

/**
 * Close configuration modal
 */
function closeConfigModal() {
    document.getElementById('configModal').style.display = 'none';
    currentServiceForConfig = null;
    currentConfigVolumes = [];
}

/**
 * Show restart warning before applying config
 */
function showRestartWarning() {
    document.getElementById('restartWarningModal').style.display = 'block';
}

/**
 * Close restart warning modal
 */
function closeRestartWarning() {
    document.getElementById('restartWarningModal').style.display = 'none';
}

/**
 * Apply configuration and restart the service
 */
async function applyConfigAndRestart() {
    if (!currentServiceForConfig) return;

    const applyBtn = document.querySelector('#restartWarningModal .btn-warning');
    applyBtn.disabled = true;
    applyBtn.textContent = 'Applying...';

    try {
        await API.updateServiceConfig(currentServiceForConfig, currentConfigVolumes, true);

        closeRestartWarning();
        closeConfigModal();
        showSuccess('Configuration updated and service restarted');
        await loadServices();
    } catch (error) {
        showError(`Failed to update configuration: ${error.message}`);
    } finally {
        applyBtn.disabled = false;
        applyBtn.textContent = 'Restart and Apply';
    }
}

// ============================================
// Directory Browser Modal
// ============================================

let browseVolumeIndex = null;
let browseCurrentPath = '';
let browseParentPath = null;

/**
 * Open the directory browser modal
 */
async function openBrowseModal(volumeIndex) {
    browseVolumeIndex = volumeIndex;

    // Start from the current host path or default
    const currentPath = currentConfigVolumes[volumeIndex]?.host_path || '/home';

    document.getElementById('browseModal').style.display = 'block';
    document.getElementById('browseList').innerHTML = '<p class="browse-empty">Loading...</p>';

    await browseTo(currentPath);
}

/**
 * Browse to a specific directory
 */
async function browseTo(path) {
    try {
        const response = await API.browseDirectory(path);

        browseCurrentPath = response.current_path;
        browseParentPath = response.parent_path;

        document.getElementById('browseCurrentPath').textContent = browseCurrentPath;
        document.getElementById('browseUpBtn').disabled = !browseParentPath;

        const browseList = document.getElementById('browseList');

        if (response.directories.length === 0) {
            browseList.innerHTML = '<p class="browse-empty">No subdirectories</p>';
        } else {
            browseList.innerHTML = response.directories.map(dir => `
                <div class="browse-item" onclick="browseTo('${dir.path.replace(/\\/g, '\\\\')}')">
                    <i class="fas fa-folder"></i>
                    <span>${dir.name}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        document.getElementById('browseList').innerHTML =
            `<p class="browse-empty">Error: ${error.message}</p>`;
    }
}

/**
 * Navigate up one directory
 */
function browseUp() {
    if (browseParentPath) {
        browseTo(browseParentPath);
    }
}

/**
 * Select the current directory and close the browser
 */
function selectCurrentDirectory() {
    if (browseVolumeIndex !== null && browseCurrentPath) {
        // Update the volume host path
        currentConfigVolumes[browseVolumeIndex].host_path = browseCurrentPath;

        // Update the input field
        const input = document.getElementById(`volume-host-${browseVolumeIndex}`);
        if (input) {
            input.value = browseCurrentPath;
        }
    }
    closeBrowseModal();
}

/**
 * Close the directory browser modal
 */
function closeBrowseModal() {
    document.getElementById('browseModal').style.display = 'none';
    browseVolumeIndex = null;
    browseCurrentPath = '';
    browseParentPath = null;
}

/**
 * Open a service in new tab
 */
function openService(url) {
    window.open(url, '_blank');
}

/**
 * Get or create the toast container
 */
function getToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'success') {
    const container = getToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    toast.innerHTML = `
        <i class="toast-icon fas ${icon}"></i>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('toast-hiding');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

/**
 * Show error message
 */
function showError(message) {
    showToast(message, 'error');
}

/**
 * Show success message
 */
function showSuccess(message) {
    showToast(message, 'success');
}

// Close modals when clicking outside
window.onclick = function(event) {
    const installModal = document.getElementById('installModal');
    const logsModal = document.getElementById('logsModal');
    const addServiceModal = document.getElementById('addServiceModal');
    const configModal = document.getElementById('configModal');
    const restartWarningModal = document.getElementById('restartWarningModal');
    const browseModal = document.getElementById('browseModal');

    if (event.target === installModal) {
        closeInstallModal();
    }
    if (event.target === logsModal) {
        closeLogsModal();
    }
    if (event.target === addServiceModal) {
        closeAddServiceModal();
    }
    if (event.target === configModal) {
        closeConfigModal();
    }
    if (event.target === restartWarningModal) {
        closeRestartWarning();
    }
    if (event.target === browseModal) {
        closeBrowseModal();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
