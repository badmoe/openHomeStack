# DNS Server (CoreDNS)

Local DNS server for custom domain names and local network resolution.

## Overview

CoreDNS provides a lightweight, flexible DNS server for your home network. Use it to create custom domain names for your services (e.g., `plex.home` instead of `192.168.1.100:32400`) or override external DNS entries.

## Default Configuration

- **DNS Port:** 5353 (UDP/TCP)
- **Note:** Uses port 5353 to avoid conflicts with Pi-hole on port 53

## Storage Structure

```
/home/containers/dns/
└── config/
    └── Corefile     # CoreDNS configuration
```

## Installation via Dashboard

Simply click "Install" - no additional configuration needed during setup.

## Manual Setup (if not using dashboard)

1. Create config directory:
   ```bash
   mkdir -p /home/containers/dns/config
   ```

2. Create Corefile (see Configuration section below)

3. Start the service:
   ```bash
   docker-compose up -d
   ```

## Configuration

### Basic Corefile

Create `/home/containers/dns/config/Corefile`:

```
.:5353 {
    # Forward all queries to upstream DNS (Cloudflare)
    forward . 1.1.1.1 1.0.0.1

    # Enable query logging
    log

    # Handle errors
    errors

    # Cache responses for 30 seconds
    cache 30
}
```

### Custom Local Domains

To add custom local domain names, create a hosts file:

**Corefile:**
```
.:5353 {
    # Local domain resolution
    hosts /etc/coredns/hosts {
        fallthrough
    }

    # Forward everything else
    forward . 1.1.1.1 1.0.0.1

    log
    errors
    cache 30
}
```

**Create `/home/containers/dns/config/hosts`:**
```
192.168.1.100  homeserver.home
192.168.1.100  plex.home
192.168.1.100  grafana.home
192.168.1.100  homeassistant.home
192.168.1.101  nas.home
192.168.1.102  printer.home
```

### Zone-Based Configuration

For more advanced setups, use zones:

```
# Handle .home domain
home:5353 {
    file /etc/coredns/home.zone
    log
    errors
}

# Everything else
.:5353 {
    forward . 1.1.1.1 1.0.0.1
    log
    errors
    cache 30
}
```

**Create `/home/containers/dns/config/home.zone`:**
```
$ORIGIN home.
@   IN  SOA ns.home. admin.home. (
        2024011501 ; serial
        3600       ; refresh
        1800       ; retry
        604800     ; expire
        86400 )    ; minimum

    IN  NS  ns.home.

plex           IN  A  192.168.1.100
grafana        IN  A  192.168.1.100
homeassistant  IN  A  192.168.1.100
nas            IN  A  192.168.1.101
```

## Using the DNS Server

### Configure Devices

Point your devices to use CoreDNS:

**Windows:**
1. Network Settings → Change adapter options
2. Right-click network → Properties
3. IPv4 → Properties
4. Preferred DNS: `YOUR_SERVER_IP`
5. Alternate DNS: `1.1.1.1` (for fallback)

**macOS:**
1. System Preferences → Network
2. Advanced → DNS
3. Add `YOUR_SERVER_IP`

**Linux:**
Edit `/etc/resolv.conf`:
```
nameserver YOUR_SERVER_IP
nameserver 1.1.1.1
```

**Note:** Since CoreDNS uses port 5353, you'll need to specify it explicitly or use port forwarding. See Integration section below.

### Testing DNS Resolution

```bash
# Test from command line (specify port)
dig @YOUR_SERVER_IP -p 5353 plex.home

# Or with nslookup
nslookup plex.home YOUR_SERVER_IP
```

## Integration with Pi-hole

CoreDNS and Pi-hole can work together:

**Option 1: Use Pi-hole as primary, CoreDNS for custom domains**
- Set Pi-hole upstream DNS to CoreDNS (YOUR_SERVER_IP:5353)
- Pi-hole handles ad blocking
- CoreDNS handles custom .home domains

**Option 2: Port forwarding**
If you want CoreDNS on port 53, edit docker-compose.yml:
```yaml
ports:
  - "5353:53/tcp"  # Maps host 5353 to container 53
  - "5353:53/udp"
```

Then configure devices to use `YOUR_SERVER_IP:5353`

## Common Use Cases

### 1. Friendly Service Names

Instead of remembering IPs:
```
http://192.168.1.100:32400/web  → http://plex.home:32400/web
http://192.168.1.100:3000       → http://grafana.home:3000
http://192.168.1.100:8123       → http://homeassistant.home:8123
```

### 2. Block Specific Domains

Add to Corefile:
```
example-tracker.com:5353 {
    template IN A {
        answer "{{ .Name }} 0 IN A 0.0.0.0"
    }
}
```

### 3. Split DNS (Different internal/external)

```
# Internal
company.com:5353 {
    file /etc/coredns/company-internal.zone
}

# External
.:5353 {
    forward . 1.1.1.1
}
```

## Resource Usage

- **RAM:** ~10-20MB
- **CPU:** Very low
- **Disk:** Minimal (logs only)

## Troubleshooting

**DNS not resolving:**
- Verify CoreDNS is running: `docker ps | grep coredns`
- Check logs: `docker logs coredns`
- Test resolution: `dig @YOUR_SERVER_IP -p 5353 google.com`
- Verify Corefile syntax

**Custom domains not working:**
- Check hosts file or zone file syntax
- Verify file permissions
- Check CoreDNS logs for errors
- Ensure fallthrough is set in Corefile

**Port conflicts:**
- If port 5353 is in use, change in docker-compose.yml
- Check what's using port: `sudo netstat -tulpn | grep 5353`

**Slow DNS responses:**
- Increase cache time in Corefile
- Check upstream DNS servers are responsive
- Consider using faster upstream (1.1.1.1, 8.8.8.8)

## Advanced Configuration

### Enable DNS over TLS (DoT)

```
.:5353 {
    forward . tls://1.1.1.1 tls://1.0.0.1 {
        tls_servername cloudflare-dns.com
    }
    cache 30
}
```

### Conditional Forwarding

```
# Forward .local to router
local:5353 {
    forward . 192.168.1.1
}

# Everything else
.:5353 {
    forward . 1.1.1.1
    cache 30
}
```

### Logging Queries to File

Edit Corefile:
```
.:5353 {
    log {
        class all
    }
    forward . 1.1.1.1
}
```

Access logs: `docker logs coredns`

### Rewrite Rules

Redirect domains:
```
.:5353 {
    rewrite name old-server.home new-server.home
    forward . 1.1.1.1
}
```

## Reload Configuration

After editing Corefile:
```bash
docker restart coredns
```

Or send reload signal:
```bash
docker kill -s SIGUSR1 coredns
```

## Security Considerations

- CoreDNS has no authentication
- Do NOT expose port 5353 to the internet
- Keep on local network only
- Use with firewall rules
- Regularly update CoreDNS image

## Example Configurations

### Home Lab Setup

```
# .home domain for local services
home:5353 {
    hosts /etc/coredns/hosts {
        192.168.1.100 server.home
        192.168.1.100 plex.home
        192.168.1.100 grafana.home
        fallthrough
    }
    log
}

# Forward everything else
.:5353 {
    forward . 1.1.1.1 1.0.0.1
    cache 60
    errors
}
```

### Development Environment

```
# .dev domain
dev:5353 {
    file /etc/coredns/dev.zone
}

# .test domain
test:5353 {
    file /etc/coredns/test.zone
}

# Everything else
.:5353 {
    forward . 1.1.1.1
}
```

## Links

- [CoreDNS Official Site](https://coredns.io/)
- [CoreDNS Documentation](https://coredns.io/manual/toc/)
- [Corefile Syntax](https://coredns.io/manual/toc/#configuration)
- [CoreDNS Plugins](https://coredns.io/plugins/)
