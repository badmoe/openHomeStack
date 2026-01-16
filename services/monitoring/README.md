# System Monitor

Complete monitoring stack with Grafana, Prometheus, Node Exporter, and cAdvisor for visualizing system and container metrics.

## Overview

This monitoring stack provides comprehensive visibility into your openHomeStack server:
- **Grafana** - Beautiful dashboards and visualizations
- **Prometheus** - Time-series metrics database
- **Node Exporter** - Host system metrics (CPU, RAM, disk, network)
- **cAdvisor** - Container-specific metrics

## Default Configuration

- **Grafana Web UI:** http://YOUR_SERVER_IP:3000
- **Prometheus:** http://YOUR_SERVER_IP:9090 (admin only)
- **Default Login:** admin / admin (change on first login)

## Storage Structure

```
/home/containers/monitoring/
├── grafana/              # Grafana dashboards and settings
├── prometheus/           # Prometheus time-series data
└── prometheus-config/    # Prometheus configuration files
```

## Installation via Dashboard

When installing through the openHomeStack dashboard, you'll be prompted for:

**Grafana Admin Password (Optional)**
- Default: `admin`
- You'll be forced to change it on first login
- Choose a strong password for security

## Manual Setup (if not using dashboard)

1. Copy this directory to your server
2. Create Prometheus config directory:
   ```bash
   mkdir -p /home/containers/monitoring/prometheus-config
   ```
3. Create prometheus.yml (see Configuration section)
4. Set password (optional):
   ```bash
   export GRAFANA_PASSWORD="your-admin-password"
   ```
5. Start the stack:
   ```bash
   docker-compose up -d
   ```

## First Time Setup

### Initial Login

1. Navigate to http://YOUR_SERVER_IP:3000
2. Login: `admin` / `admin` (or your custom password)
3. You'll be prompted to change the password
4. Set a secure password

### Add Prometheus Data Source

1. In Grafana, click the gear icon (Configuration) → Data Sources
2. Click "Add data source"
3. Select "Prometheus"
4. Set URL: `http://localhost:9090`
5. Click "Save & Test"
6. Should show "Data source is working"

### Import Dashboards

**Option 1: Import Pre-built Dashboards**

1. Click "+" → Import
2. Enter dashboard ID from https://grafana.com/grafana/dashboards/
3. Recommended dashboards:
   - **1860** - Node Exporter Full
   - **893** - Docker and System Monitoring
   - **193** - Container Monitoring
4. Select Prometheus data source
5. Click Import

**Option 2: Create Custom Dashboard**

1. Click "+" → Dashboard
2. Add Panel
3. Write PromQL queries
4. Customize visualization
5. Save dashboard

## Prometheus Configuration

Create `/home/containers/monitoring/prometheus-config/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (host metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  # cAdvisor (container metrics)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8081']
```

After editing, restart Prometheus:
```bash
docker-compose restart prometheus
```

## Available Metrics

### Host System (Node Exporter)
- CPU usage per core
- Memory usage and available
- Disk I/O and space
- Network traffic
- System load
- Temperature sensors
- Uptime

### Containers (cAdvisor)
- CPU usage per container
- Memory usage per container
- Network I/O per container
- Disk I/O per container
- Container state and health

### Example PromQL Queries

**CPU Usage:**
```promql
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory Usage:**
```promql
100 * (1 - ((node_memory_MemAvailable_bytes) / (node_memory_MemTotal_bytes)))
```

**Disk Usage:**
```promql
100 - ((node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} * 100) / node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"})
```

**Container CPU:**
```promql
rate(container_cpu_usage_seconds_total{name!=""}[5m]) * 100
```

**Container Memory:**
```promql
container_memory_usage_bytes{name!=""}
```

## Creating Alerts

### In Prometheus

Edit `prometheus.yml` to add alert rules:

```yaml
rule_files:
  - 'alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
```

Create `/home/containers/monitoring/prometheus-config/alerts.yml`:

```yaml
groups:
  - name: host
    rules:
      - alert: HighCPU
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"

      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
```

### In Grafana

1. Go to Alerting → Alert Rules
2. Create new alert rule
3. Define query condition
4. Set evaluation frequency
5. Configure notification channels

## Resource Usage

- **Prometheus:** ~100-300MB RAM (grows with metrics retention)
- **Grafana:** ~50-100MB RAM
- **Node Exporter:** ~10-20MB RAM
- **cAdvisor:** ~50-100MB RAM
- **Total:** ~250-500MB RAM
- **Disk:** Grows over time (configure retention)

## Troubleshooting

**Can't access Grafana:**
- Verify container is running: `docker ps | grep grafana`
- Check logs: `docker logs grafana`
- Ensure port 3000 isn't used by another service
- Check firewall settings

**Prometheus not scraping metrics:**
- Check Prometheus targets: http://YOUR_SERVER_IP:9090/targets
- All should show "UP" state
- If DOWN, check container connectivity
- Verify prometheus.yml syntax

**No data in Grafana:**
- Verify Prometheus data source is configured
- Check Prometheus is collecting data: http://YOUR_SERVER_IP:9090
- Try a simple query: `up`
- Check time range in Grafana dashboard

**High disk usage:**
- Configure retention in prometheus.yml:
  ```yaml
  storage:
    tsdb:
      retention.time: 15d
  ```
- Restart Prometheus after changes

## Advanced Configuration

### Configure Data Retention

Edit docker-compose.yml, add to prometheus command:

```yaml
command:
  - '--config.file=/etc/prometheus/prometheus.yml'
  - '--storage.tsdb.path=/prometheus'
  - '--storage.tsdb.retention.time=30d'
  - '--storage.tsdb.retention.size=10GB'
```

### Enable Authentication

**Grafana:**
- Already has authentication
- Configure LDAP/OAuth in grafana.ini

**Prometheus:**
- Use reverse proxy with basic auth
- Or configure auth in Prometheus config

### Add More Exporters

Popular Prometheus exporters:
- **Blackbox Exporter** - Endpoint monitoring
- **MySQL Exporter** - Database metrics
- **Nginx Exporter** - Web server metrics

Add to docker-compose.yml and prometheus.yml scrape configs.

## Backup and Restore

**Backup Grafana:**
```bash
# Dashboards are in SQLite DB
docker exec grafana cp /var/lib/grafana/grafana.db /var/lib/grafana/grafana-backup.db
docker cp grafana:/var/lib/grafana/grafana-backup.db ./grafana-backup.db
```

**Backup Prometheus:**
```bash
# Stop Prometheus first
docker-compose stop prometheus
# Backup data
tar -czf prometheus-backup.tar.gz /home/containers/monitoring/prometheus
# Restart
docker-compose start prometheus
```

**Restore:**
- Copy backup files back to volumes
- Restart containers

## Dashboard Examples

### System Overview Dashboard

Panels to include:
- CPU usage (gauge)
- Memory usage (gauge)
- Disk usage (gauge)
- Network traffic (graph)
- Container count (stat)
- System uptime (stat)

### Container Dashboard

Panels per container:
- CPU usage over time
- Memory usage over time
- Network I/O
- Restart count
- Status (up/down)

## Security Considerations

- Grafana web UI is password-protected
- Do NOT expose Prometheus (port 9090) to internet
- Change default Grafana password immediately
- Consider adding reverse proxy with HTTPS
- Restrict access to monitoring stack on local network

## Links

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [PromQL Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Node Exporter](https://github.com/prometheus/node_exporter)
- [cAdvisor](https://github.com/google/cadvisor)
