# Gaming VPN (WireGuard)

WireGuard-based virtual LAN for secure multiplayer gaming without affecting your internet connection.

## Overview

This Gaming VPN creates a private virtual network for you and your friends to play LAN multiplayer games over the internet. Unlike traditional VPNs, it only routes game traffic through the VPN - your regular internet browsing stays on your normal connection.

**Perfect for:**
- Playing "LAN-only" games with friends online
- Hosting game servers
- Bypassing NAT/CGNAT for multiplayer
- Low-latency gaming connections

## Default Configuration

- **VPN Port:** 51820 (UDP)
- **Internal Subnet:** 10.13.13.0/24
- **VPN IP Range:** 10.13.13.1 - 10.13.13.254
- **Protocol:** WireGuard (modern, fast, secure)

## Storage Structure

```
/home/containers/gaming-vpn/
└── config/
    ├── wg0.conf              # Server configuration
    ├── peer1/                # Peer 1 config and QR code
    ├── peer2/                # Peer 2 config and QR code
    └── ...
```

## Installation via Dashboard

When installing through the openHomeStack dashboard, you'll be prompted for:

**Server URL or Public IP (Optional)**
- Leave blank for auto-detection
- Or enter your public IP: `123.45.67.89`
- Or your domain: `vpn.yourdomain.com`
- Required for peers to connect to the server

**Number of Peer Configurations (Optional)**
- Default: 5 peers
- Creates configuration files for this many devices/friends
- Can add more later by recreating the container

## Manual Setup (if not using dashboard)

1. Copy this directory to your server
2. Set environment variables (optional):
   ```bash
   export SERVER_URL="123.45.67.89"  # Your public IP
   export VPN_PEERS="5"              # Number of peers
   ```
3. Start the service:
   ```bash
   docker-compose up -d
   ```

## First Time Setup

### 1. Get Peer Configuration Files

After installation, peer configurations are auto-generated:

```bash
# List peer configs
ls /home/containers/gaming-vpn/config/peer*

# View peer1 config
cat /home/containers/gaming-vpn/config/peer1/peer1.conf

# View peer1 QR code (for mobile)
cat /home/containers/gaming-vpn/config/peer1/peer1.png
```

### 2. Distribute Configs to Friends

**For PC/Mac Users:**
- Send them the `.conf` file from their peer folder
- They'll import it into WireGuard client

**For Mobile Users:**
- Send them the QR code image (`.png`)
- They'll scan it with WireGuard mobile app

### 3. Install WireGuard Client

**Windows/Mac/Linux:**
1. Download from https://www.wireguard.com/install/
2. Install WireGuard application
3. Import tunnel config (click "Add Tunnel" → select `.conf` file)
4. Activate the tunnel

**iOS/Android:**
1. Install "WireGuard" app from App Store/Play Store
2. Open app → "+" → "Create from QR code"
3. Scan QR code image
4. Activate tunnel

## Using the Gaming VPN

### Connecting

1. Open WireGuard client
2. Click "Activate" on your tunnel
3. You're now on the virtual LAN at `10.13.13.X`

**To check your VPN IP:**
```bash
# On Linux/Mac
ip addr show wg0

# On Windows (PowerShell)
Get-NetIPAddress -InterfaceAlias "WireGuard*"
```

### Hosting a Game

1. Activate WireGuard tunnel
2. Start game and choose "LAN" or "Host"
3. Game binds to `10.13.13.2` (your VPN IP)
4. Friends connect to `10.13.13.2` in-game

**Common VPN IPs:**
- Server: `10.13.13.1`
- Peer 1: `10.13.13.2`
- Peer 2: `10.13.13.3`
- Peer 3: `10.13.13.4`
- etc.

### Joining a Game

1. Activate WireGuard tunnel
2. In game, choose "Join LAN"
3. Enter host's VPN IP (e.g., `10.13.13.2`)
4. Connect and play!

## Supported Games

Any game that supports LAN multiplayer will work:

**Examples:**
- Minecraft (Java Edition LAN mode)
- Terraria
- Stardew Valley
- Left 4 Dead 2
- Age of Empires series
- Civilization series
- Many more!

**Note:** Some games require port forwarding. See Advanced Configuration.

## Firewall Configuration

**If hosting games, open port 51820:**

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 51820/udp

# firewalld (CentOS/RHEL)
sudo firewall-cmd --add-port=51820/udp --permanent
sudo firewall-cmd --reload

# Windows Firewall
# Allow UDP port 51820 inbound
```

## Resource Usage

- **RAM:** ~10-20MB
- **CPU:** Very low (efficient WireGuard protocol)
- **Network:** Only uses bandwidth for game traffic
- **Latency:** Typically adds <5ms (depends on server location)

## Troubleshooting

**Can't connect to VPN:**
- Verify container is running: `docker ps | grep gaming-vpn`
- Check logs: `docker logs gaming-vpn`
- Ensure port 51820 is open in firewall
- Check your router forwards port 51820 to server IP

**Connected to VPN but can't see other players:**
- Verify all players are connected (active tunnel)
- Check VPN IPs: ping other players (e.g., `ping 10.13.13.3`)
- Ensure game is binding to VPN interface
- Check game-specific firewall rules

**High latency/slow connection:**
- Check server upload bandwidth (should be 5+ Mbps)
- Ensure server has good internet connection
- Players too far from server geographically
- Try different WireGuard endpoint IP (if using domain)

**Peer config missing:**
- Recreate container with more peers
- Or manually add peer (see Advanced Configuration)

**VPN disconnects frequently:**
- Check server internet stability
- Verify port 51820 isn't being blocked
- Try increasing persistent keepalive (see Advanced)

## Advanced Configuration

### Add More Peers

1. Stop container: `docker-compose down`
2. Edit docker-compose.yml: `PEERS=10`
3. Remove old config: `rm -rf /home/containers/gaming-vpn/config`
4. Start container: `docker-compose up -d`
5. New configs generated for all 10 peers

### Manual Peer Addition

Edit `/home/containers/gaming-vpn/config/wg0.conf`, add:

```ini
[Peer]
# peer6
PublicKey=PEER_PUBLIC_KEY_HERE
AllowedIPs=10.13.13.7/32
```

Create peer config manually with matching private key.

### Port Forwarding for Specific Games

Some games need specific ports open. Example for Minecraft:

**On server (docker-compose.yml):**
```yaml
ports:
  - "51820:51820/udp"
  - "25565:25565/tcp"  # Minecraft port
```

**In game:**
- Host binds to `0.0.0.0:25565`
- Friends connect to `10.13.13.2:25565`

### Persistent Keepalive

For NAT traversal, edit peer configs, add:

```ini
PersistentKeepalive = 25
```

Sends keepalive packet every 25 seconds to maintain connection.

### Custom Subnet

Edit docker-compose.yml:

```yaml
environment:
  - INTERNAL_SUBNET=10.20.30.0
```

All peers will be on 10.20.30.x instead.

### DNS Configuration

By default, peers use auto DNS. To use custom:

Edit peer configs:
```ini
[Interface]
DNS = 1.1.1.1, 1.0.0.1
```

### Split Tunneling

Default configuration only routes VPN subnet (10.13.13.0/24) through VPN.

To route all traffic (like normal VPN):
```ini
AllowedIPs = 0.0.0.0/0
```

To add specific routes:
```ini
AllowedIPs = 10.13.13.0/24, 192.168.50.0/24
```

## Security Considerations

- WireGuard uses state-of-the-art cryptography
- Each peer has unique key pair
- Only allows specified IPs (10.13.13.0/24)
- Do NOT share private keys
- Regularly rotate keys for security
- Use firewall on server

## Comparison to Other VPN Solutions

**Why WireGuard for Gaming:**
- **Low Latency:** <5ms overhead typically
- **Fast:** Modern protocol, very efficient
- **Secure:** Proven cryptography
- **Easy:** Simple configuration
- **Mobile-Friendly:** Native iOS/Android apps

**vs. Traditional VPN (NordVPN, etc.):**
- Gaming VPN only routes game traffic
- Your internet stays on normal connection
- Much faster for gaming

**vs. Hamachi/ZeroTier:**
- WireGuard is open-source
- Better performance
- No account required
- You control the server

## Bandwidth Requirements

**For Host (Server):**
- Upload: 1 Mbps per connected player
- Example: 5 players = 5 Mbps upload minimum

**For Players:**
- Download: depends on game
- Upload: minimal
- Most home connections work fine

## Mobile Gaming

WireGuard works great on phones/tablets:

1. Install WireGuard app
2. Scan QR code from peer config
3. Activate tunnel
4. Play mobile multiplayer games on VPN

**Good for:**
- Minecraft Pocket Edition
- Terraria Mobile
- Stardew Valley Mobile

## Backup Configuration

```bash
# Backup all peer configs
tar -czf vpn-configs-backup.tar.gz /home/containers/gaming-vpn/config

# Restore
tar -xzf vpn-configs-backup.tar.gz -C /
```

**Important:** Keep backups of peer configs. If you lose them, you'll need to regenerate and redistribute to all friends.

## Links

- [WireGuard Official Site](https://www.wireguard.com/)
- [WireGuard Downloads](https://www.wireguard.com/install/)
- [WireGuard Documentation](https://www.wireguard.com/quickstart/)
- [linuxserver/wireguard Docker Image](https://docs.linuxserver.io/images/docker-wireguard)
