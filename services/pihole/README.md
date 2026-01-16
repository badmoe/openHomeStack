# Pi-hole

Network-wide ad blocking and DNS management for your entire home network.

## Overview

Pi-hole acts as a DNS sinkhole, blocking ads and trackers at the network level before they even reach your devices. Works on all devices connected to your network without requiring individual browser extensions or apps.

## Default Configuration

- **Web Interface:** http://YOUR_SERVER_IP/admin
- **DNS Server:** Port 53 (TCP/UDP)
- **DHCP Server:** Port 67 (optional, disabled by default)
- **Upstream DNS:** Cloudflare (1.1.1.1)

## Storage Structure

```
/home/containers/pihole/
├── etc-pihole/         # Pi-hole configuration and blocklists
└── etc-dnsmasq.d/      # DNS configuration files
```

## Installation via Dashboard

When installing through the openHomeStack dashboard, you'll be prompted for:

**Web Admin Password (Required)**
- Used to access the Pi-hole web interface
- Choose a strong password
- Can be changed later via command line

**Server IP Address (Required)**
- The static IP of your openHomeStack server
- Example: `192.168.1.100`
- Must match your server's actual IP on the network
- Used for proper DNS configuration

## Manual Setup (if not using dashboard)

1. Copy this directory to your server
2. Set environment variables:
   ```bash
   export PIHOLE_PASSWORD="your-admin-password"
   export SERVER_IP="192.168.1.100"  # Your server's IP
   ```
3. Start the service:
   ```bash
   docker-compose up -d
   ```

## First Time Setup

1. Navigate to http://YOUR_SERVER_IP/admin
2. Login with the password you set during installation
3. Configure your blocklists (defaults are already active)
4. Update your network to use Pi-hole as DNS:

### Option A: Configure Router (Recommended)
- Access your router's admin panel
- Find DHCP/DNS settings
- Set primary DNS to your Pi-hole IP (e.g., 192.168.1.100)
- Set secondary DNS to 1.1.1.1 (for fallback)
- All devices will automatically use Pi-hole

### Option B: Configure Individual Devices
- On each device, go to network settings
- Set DNS server to your Pi-hole IP
- Works immediately, but must be done per-device

## Verifying Pi-hole is Working

1. Navigate to http://YOUR_SERVER_IP/admin
2. Dashboard shows:
   - Queries blocked today
   - Percentage of ads blocked
   - Clients using Pi-hole
3. Visit an ad-heavy website
4. Check Pi-hole dashboard to see blocked queries

## Resource Usage

- **Idle:** ~50MB RAM
- **Active (handling DNS):** ~100-200MB RAM
- **CPU:** Very low (1-2%)
- **Disk:** ~100MB for configuration and logs

## Blocklist Management

**Default Blocklists:**
- Pi-hole ships with curated blocklists
- Blocks most common ads and trackers

**Adding More Blocklists:**
1. Go to Group Management → Adlists
2. Add blocklist URLs (search "Pi-hole blocklists" for collections)
3. Popular sources:
   - https://firebog.net/ (curated lists)
   - https://github.com/blocklistproject/Lists
4. Update Gravity: Tools → Update Gravity

**Whitelist Management:**
- Some sites break when ads are blocked
- Add to whitelist: Whitelist → Exact or Domain
- Common examples: Reddit, some news sites

**Blacklist Additional Domains:**
- Manually block specific domains
- Blacklist → Exact or Domain
- Useful for blocking specific trackers or unwanted sites

## Troubleshooting

**Can't access web interface:**
- Verify container is running: `docker ps | grep pihole`
- Check logs: `docker logs pihole`
- Ensure port 80 isn't used by another service
- Try http://YOUR_SERVER_IP/admin (not https)

**DNS not working:**
- Verify Pi-hole is running: `docker logs pihole`
- Test DNS: `nslookup google.com YOUR_SERVER_IP`
- Check if port 53 is accessible
- Ensure firewall allows DNS traffic

**Some sites not loading:**
- Check Pi-hole query log for blocked domains
- Whitelist the specific domain if needed
- Temporarily disable Pi-hole to verify: Settings → Disable (5 minutes)

**Slow DNS resolution:**
- Check upstream DNS servers (Settings → DNS)
- Try different upstream DNS (Google 8.8.8.8, Cloudflare 1.1.1.1)
- Update Gravity database: Tools → Update Gravity

**Pi-hole not blocking ads:**
- Verify device is using Pi-hole as DNS
- Check device DNS settings: `nslookup google.com` should show Pi-hole IP
- Update Gravity: Tools → Update Gravity
- Check if domain is whitelisted

## Advanced Configuration

**Change Upstream DNS:**
- Settings → DNS
- Uncheck Cloudflare
- Check Google, Quad9, or custom DNS
- Save changes

**Enable DHCP Server:**
- Only if you want Pi-hole to handle DHCP instead of your router
- Settings → DHCP → Enable
- Disable DHCP on your router first
- Configure IP range and gateway

**Custom DNS Records:**
- Local DNS → DNS Records
- Add custom domain names for local devices
- Example: `homeserver.local` → `192.168.1.100`

**Conditional Forwarding:**
- Settings → DNS → Advanced DNS settings
- Enable conditional forwarding
- Enter router IP and local domain
- Shows hostnames instead of IPs in Pi-hole

**Query Logging:**
- Settings → Privacy
- Choose privacy level (0-4)
- Level 0: Show everything
- Level 4: Anonymous mode

## Integration with Other Services

**DNS Server (openHomeStack):**
- Can work alongside custom DNS server
- Pi-hole handles ad blocking
- Custom DNS adds additional records

**VPN Integration:**
- Configure VPN to use Pi-hole DNS
- Blocks ads even when away from home
- Requires VPN server configuration

## Backup and Restore

**Backup Settings:**
1. Settings → Teleporter
2. Click "Backup"
3. Downloads configuration file
4. Store safely

**Restore Settings:**
1. Fresh Pi-hole installation
2. Settings → Teleporter
3. Choose backup file
4. Click "Restore"

**Manual Backup:**
```bash
# Backup configuration
docker exec pihole tar -czf /backup.tar.gz /etc/pihole /etc/dnsmasq.d
docker cp pihole:/backup.tar.gz ./pihole-backup.tar.gz
```

## Security Considerations

- Web interface is password-protected
- Do NOT expose port 80 to the internet
- Keep admin password secure
- Regularly update Pi-hole: `docker pull pihole/pihole:latest && docker-compose up -d`

## Performance Tips

**For Large Networks:**
- Increase cache size in dnsmasq settings
- Use SSD storage for faster query lookups
- Consider dedicated hardware for Pi-hole

**Reduce Log Size:**
- Settings → Privacy → Set retention period
- Or disable query logging for less-critical networks

## Links

- [Pi-hole Official Site](https://pi-hole.net/)
- [Pi-hole Documentation](https://docs.pi-hole.net/)
- [Blocklist Collection](https://firebog.net/)
- [Pi-hole Community](https://discourse.pi-hole.net/)
