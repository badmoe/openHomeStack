# openHomeStack Frontend Dashboard

Modern web interface for managing your self-hosted containerized services.

## Overview

The frontend dashboard provides a clean, intuitive interface for:
- Browsing available services
- Installing services with custom configuration
- Starting, stopping, and restarting containers
- Viewing container logs
- Monitoring system resources (CPU, RAM, disk, containers)

## Technologies

- **HTML5** - Semantic markup
- **CSS3** - Custom styling with CSS variables for theming
- **Vanilla JavaScript** - No framework dependencies, lightweight and fast
- **Font Awesome 6** - Icons
- **Fetch API** - RESTful communication with backend

## Quick Start

### Option 1: Open Directly (Development)

Simply open `index.html` in a web browser:

```bash
cd webapp/frontend
open index.html  # macOS
start index.html # Windows
xdg-open index.html # Linux
```

**Note:** You'll need to update the API URL in `js/api.js` if your backend isn't running on `localhost:5000`

### Option 2: Serve with Python (Recommended)

```bash
cd webapp/frontend
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

### Option 3: Serve with Nginx (Production)

See deployment section below.

## Configuration

### API Endpoint

The frontend connects to the backend API. By default, it expects the API at:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

To change this, edit [js/api.js](js/api.js:5)

### CORS

The backend API (Flask) has CORS enabled by default for development. In production, you may want to restrict this to your specific domain.

## Features

### Service Management

**Browse Services:**
- Grid view of all available services
- Filter by category (Media, Networking, Automation, Management)
- Real-time status indicators

**Install Services:**
- Click "Install" on any service
- Modal prompts for required configuration
- Automatically creates directories and starts containers

**Control Services:**
- Start/Stop/Restart with one click
- Open service web interfaces in new tabs
- Remove services (with confirmation)

**View Logs:**
- Click "Logs" to see container output
- Refresh logs manually
- Last 100 lines displayed

### System Monitoring

Dashboard header shows real-time:
- CPU usage percentage
- Memory usage percentage
- Disk usage percentage
- Running container count

Updates every 5 seconds.

## File Structure

```
frontend/
├── index.html          # Main dashboard page
├── css/
│   └── style.css       # All styles (dark theme)
├── js/
│   ├── api.js          # API client wrapper
│   └── app.js          # Main application logic
├── assets/             # Images, icons (currently unused)
└── README.md           # This file
```

## Customization

### Changing Theme Colors

Edit CSS variables in [css/style.css](css/style.css:1):

```css
:root {
    --primary-color: #3498db;     /* Main accent color */
    --dark-bg: #1a1a2e;           /* Page background */
    --card-bg: #16213e;           /* Card backgrounds */
    --text-primary: #eee;         /* Main text */
    --text-secondary: #a0a0a0;    /* Secondary text */
}
```

### Adding Service Icons

Icons use Font Awesome classes. To add a new icon mapping, edit [js/app.js](js/app.js:10):

```javascript
const serviceIcons = {
    'film': 'fa-film',
    'gamepad': 'fa-gamepad',
    'your-icon-key': 'fa-your-icon-class'
};
```

Then use `your-icon-key` in your service's `openhomestack.icon` label.

## API Integration

The frontend communicates with the Flask backend via REST:

**Service Discovery:**
- `GET /api/services` - List all services
- `GET /api/services/:id` - Get service details

**Container Management:**
- `POST /api/services/:id/install` - Install service
- `POST /api/services/:id/start` - Start container
- `POST /api/services/:id/stop` - Stop container
- `DELETE /api/services/:id` - Remove service

**Monitoring:**
- `GET /api/services/:id/status` - Container status
- `GET /api/services/:id/logs` - Container logs
- `GET /api/system` - System resource usage

See [backend API documentation](../backend/README.md) for details.

## Deployment

### With Nginx

Create nginx config:

```nginx
server {
    listen 80;
    server_name your-server-ip;

    # Serve frontend
    location / {
        root /path/to/openHomeStack/webapp/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask backend
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### With Docker

Create a simple Dockerfile:

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
```

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires:
- ES6+ JavaScript support
- Fetch API
- CSS Grid
- CSS Variables

## Troubleshooting

**Services not loading:**
- Check browser console for errors
- Verify backend API is running: `curl http://localhost:5000/api/services`
- Check CORS configuration if running on different domain

**"Failed to load services" error:**
- Backend API is not running
- API_BASE_URL in `js/api.js` is incorrect
- Network firewall blocking connection

**Install button doesn't work:**
- Check browser console for errors
- Verify API endpoint is accessible
- Check that docker-compose files exist for the service

**System stats showing "--":**
- Backend API `/system` endpoint may be failing
- Check backend logs
- Verify psutil and docker Python packages are installed

## Future Enhancements

- WebSocket support for real-time log streaming
- Toast notifications instead of alerts
- Dark/light theme toggle
- Service health checks and alerts
- Backup/restore UI
- User authentication
- Multi-language support

## Development

### Adding a New Feature

1. Update the UI in `index.html`
2. Add styles in `css/style.css`
3. Implement logic in `js/app.js`
4. Add API calls in `js/api.js` if needed

### Debugging

Enable verbose logging:

```javascript
// In js/app.js
console.log('Initializing...');  // Already present
// Add more console.log statements as needed
```

Use browser DevTools:
- Console: View errors and logs
- Network: Inspect API requests/responses
- Elements: Debug CSS and DOM

## Contributing

When contributing to the frontend:
- Follow existing code style
- Test in multiple browsers
- Ensure responsive design works on mobile
- Update this README if adding features

## Links

- [Backend API Documentation](../backend/README.md)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [Fetch API Reference](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
