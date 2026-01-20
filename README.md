# openHomeStack

A self-hosted home server dashboard for managing Docker-based services. Install media servers, DNS filtering, VPNs, home automation, and more through a simple web interface.

## Overview

openHomeStack is a lightweight web application that provides a dashboard for installing and managing containerized home server services. It runs as a pair of Docker containers (frontend + backend API) and lets you deploy additional services with one click.

No cloud dependencies, no vendor lock-in—just open-source tools running on your hardware.

## Features

- **Web-based dashboard** for service management without SSH or command line
- **One-click installation** of pre-configured services
- **Real-time monitoring** of container status, CPU, memory, and disk usage
- **Service catalog** with curated Docker Compose configurations
- **Wizard-based setup** for services requiring configuration

## Available Services

### Media
- **Plex** - Stream your personal media library
- **Jellyfin** - Free and open-source media streaming server

### DNS & Ad Blocking
- **Pi-hole** - Network-wide ad blocking and DNS management
- **AdGuard Home** - DNS server with ad-blocking and web management

### Networking
- **Gaming VPN** - WireGuard-based VPN with web management UI
- **Samba** - Network file sharing for Windows/Mac/Linux

### Home Automation
- **Home Assistant** - Smart home automation platform

### Monitoring
- **Prometheus + Grafana** - System and container monitoring dashboards

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Linux host recommended (works on Windows/WSL for testing)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/openHomeStack.git
   cd openHomeStack
   ```

2. Start the dashboard:
   ```bash
   cd webapp
   docker-compose up -d
   ```

3. Open your browser to `http://localhost:5000`

4. Use the web dashboard to install services

### Data Storage

Services store their data in `/home/containers/{service-name}/` on Linux. This keeps all persistent data organized and easy to back up.

## Architecture

```
┌─────────────────────────────────────────┐
│           Web Dashboard (nginx)         │
│              localhost:80               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Backend API (Flask)            │
│            localhost:5000               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Docker Engine                  │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│    │  Plex   │ │ Pi-hole │ │  etc... │  │
│    └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────┘
```

The dashboard communicates with the Docker daemon to manage service containers. Each service has its own Docker Compose definition with openHomeStack labels for metadata.

## Project Structure

```
openHomeStack/
├── services/           # Docker Compose definitions for each service
│   ├── plex/
│   ├── jellyfin/
│   ├── pihole/
│   ├── dns/            # AdGuard Home
│   ├── gaming-vpn/
│   ├── homeassistant/
│   ├── monitoring/
│   └── samba/
├── webapp/
│   ├── frontend/       # Web dashboard (HTML/CSS/JS)
│   └── backend/        # Flask API
└── README.md
```

## Adding Custom Services

Create a new folder in `services/` with a `docker-compose.yml` file. Add openHomeStack labels to make it appear in the dashboard:

```yaml
services:
  myservice:
    image: someimage:latest
    labels:
      - "openhomestack.service=myservice"
      - "openhomestack.name=My Service"
      - "openhomestack.description=What this service does"
      - "openhomestack.icon=box"
      - "openhomestack.category=other"
      - "openhomestack.url=http://localhost:8080"
```

Available icons: `film`, `shield`, `gamepad`, `folder`, `home`, `chart`, `globe`, `box`

Available categories: `media`, `dns`, `networking`, `automation`, `management`, `other`

## Status

This project is under active development. Core functionality works but expect changes. Contributions and feedback welcome via GitHub issues.

## License

Open source under the MIT License. See LICENSE file for details.

## Disclaimer

This software is provided as-is. Running services on your home network carries inherent risk. Users are responsible for securing their own environments.
