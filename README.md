# openHomeStack

⚠️ STATUS: UNDER CONSTRUCTION / NOT READY FOR USE

This project is actively being designed and documented. It is not yet recommended for deployment in any environment.

**⚠️ BEFORE PRODUCTION: Paths will need to be changed from Windows to Linux for persistent storage volumes on containers.** The current docker-compose files use `C:\containers` for testing on Windows. For Linux deployment, all volume paths must be updated to `/home/containers`.

## Overview

openHomeStack is an open-source, turnkey home server solution that transforms bare metal hardware into a fully configured self-hosted platform. Designed for gamers, media enthusiasts, and homelab users, it provides a bootable installation that deploys Proxmox, provisions an Ubuntu VM, and offers a web-based dashboard for managing containerized services.

The goal of this project is to make self-hosting accessible—starting with a technical foundation that can evolve toward ease-of-use for less experienced users. No cloud dependencies, no vendor lock-in, just open-source tools running on your hardware.

When complete, users will write an ISO to a flash drive, boot their hardware, and end up with a working home server stack complete with a browser-based interface for installing services like Plex, Pi-hole, Home Assistant, and more.

This project is intended for self-hosters, homelab enthusiasts, PC gamers building home infrastructure, and technically inclined users who want powerful services without enterprise complexity.

## Design Goals

**Turnkey deployment** - Boot from USB, get a working system with minimal manual configuration. **Home-first design** - Optimized for residential networks and personal infrastructure, not enterprise environments. **Web-based management** - Simple dashboard for service installation, monitoring, and control without SSH. **Low operational overhead** - Automated setup using proven tools (Proxmox, Docker, Ansible). **Composable services** - Users deploy only what they want from a curated catalog. **Accessible storage** - Network file sharing (Samba) for easy media and data management from any device.

## Architecture

**Physical Server**  
→ **Bootable ISO** (automated Proxmox installation)  
→ **Proxmox VE** (bare metal hypervisor)  
→ **Ubuntu VM** (container host, auto-provisioned)  
→ **Docker + Docker Compose** (container runtime)  
→ **Web Dashboard** (nginx-hosted management UI)  
→ **Individual Services** (user-selectable containers)  

The bootable ISO automates Proxmox installation and initial configuration. Ansible playbooks then provision the Ubuntu VM, install Docker, deploy the web dashboard, and make services available for one-click installation. Users manage everything through a browser without needing to SSH or run commands manually.

## Included Services

openHomeStack provides pre-configured Docker Compose definitions for the following services:

### Media  
**Plex Media Server** - Stream your personal media library to any device  
**ROMM** - Retro game ROM library manager for organizing classic game collections

### Networking & Security  
**DNS Server** - Local DNS for friendly naming and custom resolution  
**Gaming VPN** - Virtual LAN (WireGuard-based) for secure multiplayer gaming without affecting internet traffic  
**Pi-hole** - Network-wide ad blocking and DNS filtering

### Home Automation  
**Home Assistant** - Smart home automation and device control platform

### Management & Monitoring  
**System Monitor** - Dashboard for viewing container and host status (Grafana + Prometheus or similar)  
**Samba File Share** - Network file access for managing container data from Windows/Mac/Linux

### Future Considerations
**Local AI** - Self-hosted LLM for private AI assistance  
**Additional services** based on community feedback and contribution

## User Experience

1. **Download** the openHomeStack ISO from releases
2. **Write** the ISO to a USB flash drive (8GB+)
3. **Boot** your server hardware from the USB drive
4. **Wait** while Proxmox installs and the Ubuntu VM provisions automatically
5. **Open** your browser to the server's IP address
6. **Install services** with one click from the web dashboard
7. **Access** your container data via network file share (\\\\server-ip\\containers)

## What This Project Is Not

This project is **not** a managed hosting platform, **not** focused on cloud deployment, **not** using Kubernetes (intentionally keeping it simpler), **not** designed for enterprise compliance requirements, and **not** a commercial product. The emphasis is on clarity, control, and accessibility for home users rather than maximum scalability or abstraction.

## Current Status

**Repository structure** is established. **Documentation** is in progress. **Service definitions** are in development. **Automation scripts** are being written. **Stability** is not production-ready. **Breaking changes** should be expected until an initial stable release is announced.

## Technology Stack

- **Proxmox VE 8.x** - Hypervisor layer
- **Ubuntu 22.04 LTS** - Container host VM
- **Docker & Docker Compose** - Container runtime
- **Ansible 2.14+** - Automation and provisioning
- **Python 3.10+** - Build scripts and backend API
- **Flask/FastAPI** - Web dashboard backend
- **Nginx** - Web server for dashboard

## License

This project is open source and intended to be freely used, adapted, and shared. See the LICENSE file for details.

## Contributing

Contribution guidelines will be added once the project structure stabilizes. Until then, feedback and design discussion are welcome via GitHub issues. Frequent iteration should be expected during early development.

## Disclaimer

This project is provided as-is, without warranty. Running services on your home network—especially those exposed to the internet—carries inherent risk. Users are responsible for understanding and securing their own environments. Always keep systems updated and follow security best practices.