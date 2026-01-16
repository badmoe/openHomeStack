# Open Home Stack

⚠️ STATUS: UNDER CONSTRUCTION / NOT READY FOR USE

This project is actively being designed and documented. It is not yet recommended for deployment in any environment.

## Overview

This repository is an open-source, home-first server stack intended to be deployed in a residential or small personal environment. It is designed to support both internal home services and externally accessible services (such as game servers or remote access), while remaining simple, understandable, and maintainable.

The goal of this project is to provide a clear, opinionated reference architecture for running a modern home server using well-understood tools, without unnecessary enterprise complexity or cloud dependencies.

When complete, this project will document and provide examples for a bare-metal hypervisor layer, one or more container host virtual machines, and a collection of optional, containerized services commonly useful on a home network.

This project is intended for self-hosters, homelab users, and technically inclined home users who want a structured but flexible foundation.

## Design Goals

Home-first design focused on residential networks and personal infrastructure. Intentional exposure with a clear separation between internal-only and internet-facing services. Low operational overhead through simple, proven tools. Composable services where users deploy only what they want. Explicit documentation where architecture and decisions are explained rather than implied.

## Planned Architecture

Physical Server  
→ Hypervisor  
→ Container Host Virtual Machine  
→ Docker / Docker Compose  
→ Individual Containerized Services  

The hypervisor provides isolation, snapshots, and hardware abstraction. The container host runs Docker and Docker Compose. Services are deployed as independent containers and grouped by purpose and exposure level.

## Planned Services

The stack is expected to include optional examples and documentation for the following services.

### Remote Access:  
A lightweight VPN providing secure external access. The VPN will be configurable for either full access to the home network or access limited to specific services only. This is intended primarily for administration and private remote use.

### Media:  
Plex for home media hosting with internal and/or VPN-based access and persistent media and metadata storage.

### Networking:  
A simple DNS server allowing local DNS records for internal services, friendly service names instead of IP addresses, and optional split-DNS behavior for VPN users.

### Web / UI:  
A lightweight and customizable nginx page acting as a simple landing page for home services, with optional internal-only exposure and minimal configuration.

### Local AI
A locally hosted LLM service for private AI chatbot use on the home network. This service is intended to run entirely within the local environment, keeping prompts and responses private, and may be used for general assistance, experimentation, or reference without relying on external APIs.

### Retro Gaming
A ROM library manager for organizing and browsing retro game collections on the local network. This service is intended to manage metadata and library structure for supported platforms and integrate with emulators or front-end tools without requiring internet exposure.

## What This Project Is Not

This project is not a managed hosting platform, not Kubernetes-first, not cloud-native by default, not focused on enterprise compliance, and not intended to be a turnkey appliance in its early stages. The emphasis is on clarity and control rather than abstraction.

## Current Status

Documentation is in progress. Architecture is evolving. Service definitions are in draft form. Stability is not production-ready. Breaking changes should be expected until an initial stable release is announced.

## License

This project is open source and intended to be freely used, adapted, and shared. See the LICENSE file for details.

## Contributing

Contribution guidelines will be added once the project structure stabilizes. Until then, feedback and design discussion are welcome, and frequent iteration should be expected.

## Disclaimer

This project is provided as-is, without warranty. Running services exposed to the internet carries inherent risk. Users are responsible for understanding and securing their own environments.
