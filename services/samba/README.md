# Samba File Share

Network file sharing for easy access to your container data from any device.

## Overview

Samba provides SMB/CIFS file sharing, making your container data accessible from Windows, Mac, and Linux devices. This is the easiest way to manage media files for Plex, ROMs for ROMM, and other container data without needing SSH or command-line access.

## Default Configuration

- **Share Name:** containers
- **Share Path:** /home/containers
- **Access:** Read/Write for all users
- **Guest Access:** Disabled (authentication required)

## Accessing the Share

### Windows
1. Open File Explorer
2. In the address bar, type: `\\YOUR_SERVER_IP\containers`
3. Press Enter
4. Enter credentials if prompted (typically your system username/password)
5. The containers folder will appear as a network drive

**Map as Network Drive:**
- Right-click "This PC" → Map network drive
- Choose drive letter
- Folder: `\\YOUR_SERVER_IP\containers`
- Check "Reconnect at sign-in" for persistence

### macOS
1. Open Finder
2. Press `Cmd + K` (or Go → Connect to Server)
3. Enter: `smb://YOUR_SERVER_IP/containers`
4. Click Connect
5. Enter credentials if prompted

**Add to Favorites:**
- After connecting, drag the share to Finder sidebar

### Linux
1. Open file manager
2. Connect to Server or Network
3. Enter: `smb://YOUR_SERVER_IP/containers`
4. Or use command line: `smbclient //YOUR_SERVER_IP/containers`

## Folder Structure

The `containers` share exposes all service data:

```
\\YOUR_SERVER_IP\containers\
├── plex\
│   ├── config\
│   ├── transcode\
│   └── media\
│       ├── movies\
│       ├── tv\
│       └── music\
├── romm\
│   ├── roms\
│   ├── config\
│   └── database\
├── pihole\
│   ├── etc-pihole\
│   └── etc-dnsmasq.d\
└── [other services]
```

## Common Use Cases

**Adding Media to Plex:**
1. Connect to `\\YOUR_SERVER_IP\containers`
2. Navigate to `plex\media\movies` (or tv, music)
3. Copy your media files here
4. Plex will auto-scan and add them to your library

**Adding ROMs to ROMM:**
1. Connect to share
2. Navigate to `romm\roms`
3. Create platform folders (nes, snes, etc.)
4. Copy ROM files to appropriate folders
5. Scan library in ROMM

**Backing Up Container Data:**
- Simply copy folders from the share to your PC
- Reverse process to restore

## Troubleshooting

**Can't connect to share:**
- Verify Samba container is running: `docker ps | grep samba`
- Check logs: `docker logs samba`
- Ensure firewall allows SMB (ports 139, 445)
- Try IP address instead of hostname

**Permission denied errors:**
- Check file permissions on server
- Ensure files are owned by PUID=1000
- Try reconnecting to refresh credentials

**Share not browseable:**
- Directly type the path: `\\YOUR_SERVER_IP\containers`
- Network discovery may be disabled on your device

**Slow file transfers:**
- Check network speed (gigabit recommended for large media)
- Ensure SMB2/SMB3 is enabled (not SMB1)
- Consider wired connection for large transfers

**Files not appearing in services:**
- Check file permissions: should be readable by PUID=1000
- Verify files are in correct directories
- Trigger manual scan in service (Plex, ROMM, etc.)

## Security Considerations

- Samba share is accessible to anyone on your local network
- Do NOT expose Samba ports to the internet
- Keep on local network or behind VPN only
- Consider adding user authentication for sensitive data

## Performance Tips

**For Large File Transfers:**
- Use wired Ethernet (not WiFi) for best speed
- Transfer overnight for very large libraries
- Consider upgrading to 2.5GbE or 10GbE for massive media collections

**For Many Small Files:**
- Compress into archives before transferring
- Use rsync instead for thousands of small files

## Advanced Configuration

**Add User Authentication:**
Edit docker-compose.yml environment:
```yaml
- USER=yourname;yourpassword
```

**Add Additional Shares:**
```yaml
- SHARE2=media;/home/containers/plex/media;yes;yes;no;all;none
```

**Change Share Permissions:**
Modify the SHARE variable format:
- `yes` after path = Browseable
- `yes` after browseable = Read-only
- `yes` after read-only = Guest access allowed

## Links

- [dperson/samba Docker Image](https://github.com/dperson/samba)
- [Samba Official Documentation](https://www.samba.org/samba/docs/)
