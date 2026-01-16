"""
openHomeStack Backend API
RESTful API for managing containerized services
"""

from flask import Flask, jsonify
from flask_cors import CORS
from api.routes import api_bp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Enable CORS for frontend development
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "service": "openHomeStack API"})

    logger.info("openHomeStack backend API initialized")
    return app

if __name__ == '__main__':
    app = create_app()
    # Only for development - use gunicorn or similar in production
    app.run(host='0.0.0.0', port=5000, debug=True)
