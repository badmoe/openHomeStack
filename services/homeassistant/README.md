# Home Assistant

Open-source smart home automation platform for controlling all your devices.

## Overview

Home Assistant brings together all your smart home devices into one unified interface. Control lights, thermostats, cameras, locks, and more - all from a single dashboard. Supports thousands of integrations and powerful automation.

## Default Configuration

- **Web Interface:** http://YOUR_SERVER_IP:8123
- **Network Mode:** Host (for device discovery)
- **Privileged Mode:** Enabled (for USB device access)

## Storage Structure

```
/home/containers/homeassistant/
└── config/           # Home Assistant configuration and database
```

## Installation via Dashboard

Simply click "Install" - Home Assistant requires no additional configuration during setup.

## Manual Setup (if not using dashboard)

1. Copy this directory to your server
2. Start the service:
   ```bash
   docker-compose up -d
   ```

## First Time Setup

1. Navigate to http://YOUR_SERVER_IP:8123
2. Wait for Home Assistant to initialize (first start takes 2-3 minutes)
3. Create your admin account
4. Set your location for weather, timezone, and local services
5. Skip device discovery for now (you can add devices later)
6. Welcome to Home Assistant!

## Adding Devices and Integrations

**Auto-Discovery:**
- Home Assistant automatically discovers many devices on your network
- Check Notifications for discovered devices
- Click to configure and add them

**Manual Integration:**
1. Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for your device/service
4. Follow setup wizard

**Popular Integrations:**
- Philips Hue (lights)
- Google Nest (thermostats)
- Ring (doorbells, cameras)
- Spotify (media)
- Weather services
- Mobile app (iOS/Android)

## USB Device Support (Zigbee/Z-Wave)

This setup includes support for USB dongles:

**Supported Protocols:**
- Zigbee (Zigbee2MQTT, ZHA)
- Z-Wave (Z-Wave JS)
- Matter/Thread

**Setup:**
1. Plug USB dongle into server (e.g., /dev/ttyUSB0)
2. Verify device appears: `ls -la /dev/ttyUSB*`
3. Edit docker-compose.yml if using different USB port
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration
6. Choose Zigbee or Z-Wave
7. Select USB device path

**If you don't have USB devices:**
Comment out the `devices` section in docker-compose.yml

## Creating Automations

**Simple Example - Turn on lights at sunset:**
1. Settings → Automations & Scenes
2. Create Automation
3. Trigger: Sun (sunset)
4. Action: Turn on lights
5. Save

**Advanced Automations:**
- Use conditions (if temperature < 65°F)
- Multiple triggers and actions
- Scripts for complex sequences
- Visual editor or YAML mode

## Resource Usage

- **Idle:** ~200MB RAM
- **Active (with devices):** ~300-500MB RAM
- **Database Growth:** 100MB-1GB over time
- **CPU:** Low (spikes during automations)

## Troubleshooting

**Can't access web interface:**
- Wait 2-3 minutes on first start
- Check logs: `docker logs homeassistant`
- Verify port 8123 isn't blocked
- Try http://localhost:8123 from server

**Devices not discovered:**
- Ensure Home Assistant and devices are on same network
- Check router settings (mDNS/Bonjour enabled)
- Try manual integration instead
- Verify network_mode: host is set

**USB device not detected:**
- Check device path: `ls -la /dev/ttyUSB*`
- Update devices section in docker-compose.yml
- Ensure container has privileged access
- Check USB dongle is recognized by host

**Database growing too large:**
- Settings → System → Storage
- Configure recorder to purge old data
- Exclude entities you don't need history for
- Default: keeps 10 days of history

**Slow performance:**
- Too many integrations polling
- Reduce recorder history length
- Disable unused integrations
- Consider more powerful hardware

## Configuration Files

Home Assistant configuration is in `/home/containers/homeassistant/config/`

**Key Files:**
- `configuration.yaml` - Main configuration
- `automations.yaml` - Automation definitions
- `scripts.yaml` - Script definitions
- `scenes.yaml` - Scene definitions
- `home-assistant.log` - Application logs

**Editing Configuration:**
1. Access via Samba: `\\YOUR_SERVER_IP\containers\homeassistant\config`
2. Edit YAML files
3. Settings → Server Controls → Check Configuration
4. Restart Home Assistant

## Mobile App

**Install the App:**
- iOS: App Store - "Home Assistant"
- Android: Play Store - "Home Assistant"

**Setup:**
1. Open app
2. Enter server URL: http://YOUR_SERVER_IP:8123
3. Login with your credentials
4. Enable location tracking (optional, for presence detection)
5. Allow notifications

**Features:**
- Control devices from anywhere
- Receive automation notifications
- Location-based automations
- Quick actions widget

## Advanced Configuration

**Add Custom Integrations (HACS):**
1. Install HACS (Home Assistant Community Store)
2. Browse thousands of community integrations
3. One-click install for custom components

**Voice Control:**
- Integrate with Google Assistant
- Integrate with Amazon Alexa
- Local voice control with Rhasspy

**Energy Monitoring:**
- Settings → Energy
- Add energy sensors
- Track consumption over time

**Presence Detection:**
- Use mobile app for GPS tracking
- Bluetooth trackers for room presence
- Network device tracking (less accurate)

## Backup and Restore

**Create Backup:**
1. Settings → System → Backups
2. Create Backup
3. Wait for completion
4. Download backup file

**Restore Backup:**
1. Settings → System → Backups
2. Upload backup file
3. Click Restore
4. System will restart

**Manual Backup:**
```bash
# Backup entire config directory
cp -r /home/containers/homeassistant/config /backup/location
```

## Security Considerations

- Do NOT expose port 8123 to the internet directly
- Use Nabu Casa Cloud for secure remote access
- Or set up VPN to access remotely
- Enable 2FA for your account
- Keep Home Assistant updated

## Integration Examples

**Example 1: Motion-Activated Lights**
- Trigger: Motion sensor detects movement
- Condition: After sunset
- Action: Turn on hallway lights for 5 minutes

**Example 2: Climate Control**
- Trigger: Temperature below 68°F
- Condition: Someone home
- Action: Set thermostat to 72°F

**Example 3: Security Notification**
- Trigger: Door opens
- Condition: Nobody home
- Action: Send mobile notification + camera snapshot

## Links

- [Home Assistant Official Site](https://www.home-assistant.io/)
- [Documentation](https://www.home-assistant.io/docs/)
- [Community Forum](https://community.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- [Integration List](https://www.home-assistant.io/integrations/)
