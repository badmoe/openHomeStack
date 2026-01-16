# Plex Media Server

Stream your personal media library to any device on your network.

## Overview

Plex organizes your video, music, and photo collections and streams them to all your devices. This configuration uses host networking for optimal performance and auto-discovery.

## Default Configuration

- **Web Interface:** http://YOUR_SERVER_IP:32400/web
- **Network Mode:** Host (for auto-discovery and best performance)
- **Hardware Transcoding:** Enabled (Intel QuickSync via /dev/dri)

## Storage Structure

```
/home/containers/plex/
├── config/          # Plex configuration and metadata database
├── transcode/       # Temporary transcoding files
└── media/
    ├── movies/      # Place your movie files here
    ├── tv/          # Place your TV show files here
    └── music/       # Place your music files here
```

Access these folders via the Samba share at `\\YOUR_SERVER_IP\containers\plex\media`

## Installation via Dashboard

When installing through the openHomeStack dashboard, you'll be prompted for:

**Plex Claim Token (Optional)**
- Get your claim token from: https://plex.tv/claim
- Valid for 4 minutes after generation
- If you skip this, you can claim your server later via the Plex web UI

## Manual Setup (if not using dashboard)

1. Copy this directory to your server
2. Set the PLEX_CLAIM environment variable (optional):
   ```bash
   export PLEX_CLAIM="claim-xxxxxxxxxxxxxxxxxxxx"
   ```
3. Start the service:
   ```bash
   docker-compose up -d
   ```

## First Time Setup

1. Navigate to http://YOUR_SERVER_IP:32400/web
2. Sign in with your Plex account
3. Follow the setup wizard to add your media libraries:
   - Movies: `/movies`
   - TV Shows: `/tv`
   - Music: `/music`

## Hardware Transcoding

This configuration enables Intel QuickSync hardware transcoding via `/dev/dri`. 

**If your CPU doesn't support QuickSync or you get errors:**
- Comment out the `devices` section in docker-compose.yml
- Transcoding will fall back to CPU (slower but works on any system)

**To verify hardware transcoding is working:**
- Play a video that requires transcoding
- Go to Plex Settings → Dashboard
- Look for "(hw)" next to the transcode session

## Accessing Your Media

**From your PC (Windows/Mac/Linux):**
- Connect to `\\YOUR_SERVER_IP\containers` (Windows) or `smb://YOUR_SERVER_IP/containers` (Mac/Linux)
- Navigate to `plex/media/movies` (or tv/music)
- Copy your media files here

**Media Organization Tips:**
- Movies: `moviename (year).ext` → Example: `The Matrix (1999).mkv`
- TV Shows: `showname/Season 01/showname S01E01.ext`
- Music: `artist/album/track.ext`

See Plex's [media preparation guide](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/) for details.

## Resource Usage

- **Idle:** ~200MB RAM
- **Streaming (direct play):** ~300MB RAM, minimal CPU
- **Transcoding:** CPU/GPU intensive, RAM varies by stream count
- **Storage:** Metadata grows with library size (typically 1-5GB)

## Troubleshooting

**Can't access Plex web interface:**
- Verify container is running: `docker ps | grep plex`
- Check logs: `docker logs plex`
- Ensure port 32400 isn't blocked by firewall

**Server not appearing in Plex app:**
- Host networking should make it auto-discover
- Manually add via Settings → Server → Add Server → IP:32400

**Hardware transcoding not working:**
- Verify /dev/dri exists: `ls -la /dev/dri`
- Check container has access: `docker exec plex ls -la /dev/dri`
- Ensure user has proper permissions (video group)

**Library not updating:**
- Go to library settings → "Scan Library Files"
- Check file permissions (should be readable by PUID=1000)

## Advanced Configuration

**Change timezone:**
Edit `TZ` in docker-compose.yml to your timezone (e.g., `America/New_York`)

**Disable hardware transcoding:**
Comment out the `devices:` section in docker-compose.yml

**Add additional media folders:**
Add volume mounts like:
```yaml
- /home/containers/plex/media/audiobooks:/audiobooks
```

Then add the library in Plex UI pointing to `/audiobooks`

## Links

- [Plex Official Documentation](https://support.plex.tv/)
- [LinuxServer.io Plex Image](https://docs.linuxserver.io/images/docker-plex)
- [Plex Media Naming Guide](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/)
- [Get Claim Token](https://plex.tv/claim)