# openHomeStack Backend API

RESTful API for managing containerized services through the openHomeStack dashboard.

## Overview

The backend API provides endpoints for:
- **Service Discovery** - Scanning and parsing docker-compose.yml files
- **Container Management** - Installing, starting, stopping, and removing services
- **Monitoring** - Container status, logs, and system resource usage

## Quick Start

### Installation

```bash
cd webapp/backend
pip install -r requirements.txt
```

### Running the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Service Discovery

#### GET /api/services
List all available services from the services directory.

**Response:**
```json
{
  "success": true,
  "count": 1,
  "services": [
    {
      "id": "plex",
      "name": "Plex Media Server",
      "description": "Stream your personal media library",
      "icon": "film",
      "category": "media",
      "url": "http://localhost:32400/web",
      "install_prompts": [
        {
          "key": "claim_token",
          "label": "Plex Claim Token (optional - get from plex.tv/claim)",
          "env_var": "CLAIM_TOKEN"
        }
      ]
    }
  ]
}
```

#### GET /api/services/:id
Get detailed information about a specific service including current status.

**Response:**
```json
{
  "success": true,
  "service": {
    "id": "plex",
    "name": "Plex Media Server",
    "status": {
      "state": "running",
      "id": "abc123def456",
      "name": "plex"
    },
    ...
  }
}
```

### Container Management

#### POST /api/services/:id/install
Install a service with optional environment variables.

**Request Body:**
```json
{
  "env": {
    "PLEX_CLAIM": "claim-xxxxxxxxxxxx"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Service 'plex' installed successfully",
  "service_id": "plex"
}
```

#### POST /api/services/:id/start
Start a stopped service.

**Response:**
```json
{
  "success": true,
  "message": "Service 'plex' started successfully"
}
```

#### POST /api/services/:id/stop
Stop a running service.

#### POST /api/services/:id/restart
Restart a service.

#### DELETE /api/services/:id
Remove a service.

**Request Body (optional):**
```json
{
  "remove_volumes": false
}
```

### Monitoring

#### GET /api/services/:id/status
Get current status of a service's containers.

**Response:**
```json
{
  "success": true,
  "service_id": "plex",
  "status": {
    "state": "running",
    "id": "abc123def456",
    "name": "plex",
    "image": "lscr.io/linuxserver/plex:latest",
    "created": "2024-01-15T12:00:00Z",
    "started_at": "2024-01-15T12:00:05Z"
  }
}
```

#### GET /api/services/:id/logs
Get container logs.

**Query Parameters:**
- `tail` - Number of lines to return (default: 100)
- `follow` - Stream logs (not yet implemented)

**Response:**
```json
{
  "success": true,
  "service_id": "plex",
  "logs": "2024-01-15T12:00:00Z Container started\n..."
}
```

#### GET /api/system
Get system resource usage and Docker information.

**Response:**
```json
{
  "success": true,
  "system": {
    "cpu": {
      "percent": 15.5,
      "count": 8,
      "physical_count": 4
    },
    "memory": {
      "total_gb": 16.0,
      "available_gb": 8.5,
      "used_gb": 7.5,
      "percent": 46.8
    },
    "disk": {
      "total_gb": 500.0,
      "used_gb": 125.0,
      "free_gb": 375.0,
      "percent": 25.0
    },
    "docker": {
      "status": "running",
      "containers_running": 3,
      "containers_stopped": 1,
      "containers_total": 4,
      "images": 10
    },
    "containers": [
      {
        "name": "plex",
        "service": "plex",
        "status": "running",
        "image": "lscr.io/linuxserver/plex:latest"
      }
    ]
  }
}
```

### Health Check

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "openHomeStack API"
}
```

## Architecture

### Components

- **app.py** - Flask application factory and configuration
- **api/routes.py** - API endpoint definitions
- **api/services.py** - Service discovery and metadata parsing
- **api/containers.py** - Docker container lifecycle management
- **api/system.py** - System resource monitoring

### Service Discovery Process

1. Scans `/services/*/docker-compose.yml` files
2. Parses `openhomestack.*` labels from container definitions
3. Extracts metadata (name, description, icon, category, URL)
4. Identifies installation prompts from `openhomestack.install.prompt.*` labels
5. Returns structured service catalog

### Container Management Process

1. **Install:**
   - Creates `/home/containers/{service}/` directory structure
   - Generates `.env` file from user-provided values
   - Runs `docker-compose up -d` in service directory

2. **Start/Stop/Restart:**
   - Executes corresponding docker-compose command

3. **Remove:**
   - Runs `docker-compose down` (optionally with `-v` for volumes)
   - Removes `.env` file

## Development

### Project Structure

```
webapp/backend/
├── app.py              # Application entry point
├── requirements.txt    # Python dependencies
├── api/
│   ├── __init__.py
│   ├── routes.py       # API endpoints
│   ├── services.py     # Service discovery
│   ├── containers.py   # Container management
│   └── system.py       # System monitoring
└── README.md
```

### Adding New Functionality

To add a new endpoint:

1. Define route in [api/routes.py](webapp/backend/api/routes.py)
2. Implement logic in appropriate module
3. Update this documentation

### Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

## Dependencies

- **Flask** - Web framework
- **Flask-CORS** - CORS support for frontend
- **PyYAML** - Parsing docker-compose.yml files
- **docker** - Docker SDK for Python
- **psutil** - System resource monitoring
- **python-dotenv** - Environment variable management

## Security Considerations

**Current (MVP):**
- No authentication required
- Intended for local network use only
- Should NOT be exposed to the internet

**Future:**
- Add basic authentication or token-based auth
- HTTPS support
- Rate limiting
- Request validation

## Testing

### Manual Testing with curl

```bash
# List services
curl http://localhost:5000/api/services

# Get service details
curl http://localhost:5000/api/services/plex

# Install Plex
curl -X POST http://localhost:5000/api/services/plex/install \
  -H "Content-Type: application/json" \
  -d '{"env": {"PLEX_CLAIM": "claim-xxxxxxxxxxxx"}}'

# Get service status
curl http://localhost:5000/api/services/plex/status

# Get logs
curl http://localhost:5000/api/services/plex/logs?tail=50

# Stop service
curl -X POST http://localhost:5000/api/services/plex/stop

# Start service
curl -X POST http://localhost:5000/api/services/plex/start

# Remove service
curl -X DELETE http://localhost:5000/api/services/plex

# System info
curl http://localhost:5000/api/system
```

## Troubleshooting

**"Docker client not available" errors:**
- Ensure Docker is installed and running
- Verify user has permissions to access Docker socket
- Add user to `docker` group: `sudo usermod -aG docker $USER`

**Service discovery returns empty list:**
- Verify services directory path is correct
- Check that docker-compose.yml files exist in service directories
- Review logs for parsing errors

**docker-compose commands fail:**
- Ensure docker-compose is installed
- Check service directory permissions
- Verify docker-compose.yml syntax with `docker-compose config`

## Future Enhancements

- WebSocket support for real-time log streaming
- Container health checks
- Automatic service updates
- Backup/restore functionality
- Multi-container service support
- Service dependency management
