# ROMM - ROM Manager

Organize, browse, and manage your retro game ROM collection with a beautiful web interface.

## Overview

ROMM is a modern ROM library manager that helps you organize your retro gaming collection. It supports multiple emulation platforms, automatic metadata fetching, cover art, and a clean web interface for browsing your games.

## Default Configuration

- **Web Interface:** http://YOUR_SERVER_IP:8080
- **Network Mode:** Host
- **Database:** MariaDB (included)

## Storage Structure

```
/home/containers/romm/
├── data/           # ROMM application data
├── config/         # Configuration files
├── database/       # MariaDB database files
├── roms/           # Your ROM files (organized by platform)
│   ├── nes/
│   ├── snes/
│   ├── genesis/
│   ├── ps1/
│   └── ...
└── assets/         # Game covers, screenshots, metadata
```

Access these folders via the Samba share at `\\YOUR_SERVER_IP\containers\romm\roms`

## Installation via Dashboard

When installing through the openHomeStack dashboard, you'll be prompted for:

**Database Password (Optional)**
- Default: `romm`
- Used for the MariaDB database
- Change this for better security

**IGDB Client ID & Secret (Optional)**
- Get credentials from: https://api.igdb.com/
- Required for automatic game metadata and cover art
- Free for non-commercial use
- If skipped, you'll need to add metadata manually

## Manual Setup (if not using dashboard)

1. Copy this directory to your server
2. Set environment variables (optional):
   ```bash
   export ROMM_DB_PASSWORD="your-secure-password"
   export IGDB_CLIENT_ID="your-client-id"
   export IGDB_CLIENT_SECRET="your-client-secret"
   ```
3. Start the service:
   ```bash
   docker-compose up -d
   ```

## First Time Setup

1. Navigate to http://YOUR_SERVER_IP:8080
2. Create your admin account
3. Configure IGDB API credentials if you have them:
   - Settings → Integrations → IGDB
   - Enter your Client ID and Secret
4. Add your ROM files to `/home/containers/romm/roms/`
5. Scan library to import games

## Adding ROM Files

**Via Samba Share (Recommended):**
- Connect to `\\YOUR_SERVER_IP\containers` (Windows) or `smb://YOUR_SERVER_IP/containers` (Mac/Linux)
- Navigate to `romm/roms/`
- Create folders for each platform (nes, snes, genesis, etc.)
- Copy your ROM files into the appropriate platform folders

**Platform Folder Names:**
- Use standard platform abbreviations (nes, snes, gb, gbc, gba, genesis, ps1, etc.)
- ROMM will auto-detect platforms based on folder names
- See ROMM documentation for complete platform list

**Supported File Formats:**
- Most common ROM formats (.zip, .7z, .nes, .smc, .bin, .iso, etc.)
- Multi-disc games should be in the same folder

## Getting IGDB API Credentials

1. Register at https://www.igdb.com/
2. Create a Twitch Developer account (IGDB is owned by Twitch)
3. Register your application at https://dev.twitch.tv/console/apps
4. Note your Client ID and Client Secret
5. Enter these in ROMM's settings or during installation

**Benefits of IGDB Integration:**
- Automatic game metadata (title, release date, description)
- Cover art and screenshots
- Genre and platform information
- Player count and ratings

## Resource Usage

- **Idle:** ~150MB RAM
- **Scanning Library:** CPU/disk intensive, RAM varies
- **Database:** 50-500MB depending on library size
- **Assets:** Variable (cover art, screenshots)

## Troubleshooting

**Can't access ROMM web interface:**
- Verify both containers are running: `docker ps | grep romm`
- Check logs: `docker logs romm` and `docker logs romm-db`
- Ensure port 8080 isn't blocked by firewall

**Database connection errors:**
- Wait 30 seconds for MariaDB to fully start on first launch
- Check database logs: `docker logs romm-db`
- Verify ROMM_DB_PASSWORD matches in both containers

**ROMs not appearing:**
- Check file permissions (should be readable by PUID=1000)
- Verify folder structure matches platform names
- Trigger manual library scan in ROMM settings
- Check ROMM logs for scan errors

**Metadata not loading:**
- Verify IGDB credentials are correct
- Check IGDB API quota (free tier has limits)
- Try manual metadata refresh for specific games

**Slow library scanning:**
- Large ROM collections take time to scan initially
- Compressed ROMs (.zip, .7z) are slower than uncompressed
- Consider upgrading hardware or scanning in batches

## Platform Organization Tips

**Recommended Folder Structure:**
```
roms/
├── nes/
│   ├── Super Mario Bros.nes
│   └── Zelda.nes
├── snes/
│   ├── Super Mario World.smc
│   └── Chrono Trigger.smc
├── ps1/
│   ├── Final Fantasy VII/
│   │   ├── disc1.bin
│   │   ├── disc2.bin
│   │   └── disc3.bin
│   └── Crash Bandicoot.bin
└── arcade/
    ├── pacman.zip
    └── galaga.zip
```

**Naming Conventions:**
- Use descriptive filenames
- ROMM will clean up names for display
- For multi-disc games, use consistent naming

## Advanced Configuration

**Change web interface port:**
Edit docker-compose.yml and change network_mode to bridge, then add:
```yaml
ports:
  - "8080:8080"
```

**Add additional ROM storage:**
Add volume mounts in docker-compose.yml:
```yaml
- /mnt/external-drive/roms:/romm/roms-external
```

**Backup your library:**
- Database: `docker exec romm-db mysqldump -u romm -promm romm > backup.sql`
- Config: Copy `/home/containers/romm/config/`
- ROMs: Already stored separately, just backup the files

## Emulator Integration

ROMM is a library manager, not an emulator. To play games:

1. **Local Emulation:**
   - Download ROMs from your ROMM library
   - Use standalone emulators (RetroArch, Dolphin, PCSX2, etc.)

2. **RetroArch Integration:**
   - Configure RetroArch to access `\\YOUR_SERVER_IP\containers\romm\roms`
   - Launch games directly from network share

3. **Steam Deck / Handheld:**
   - Add ROMM ROMs to your device via sync or network copy
   - Use EmuDeck or similar to configure emulators

## Security Notes

- ROMM does not include authentication by default (v1.x)
- Do NOT expose port 8080 to the internet
- Keep on local network or behind VPN only
- Change default database password

## Links

- [ROMM GitHub](https://github.com/rommapp/romm)
- [ROMM Documentation](https://github.com/rommapp/romm/wiki)
- [IGDB API Registration](https://api.igdb.com/)
- [Supported Platforms List](https://github.com/rommapp/romm/wiki/Platforms)
