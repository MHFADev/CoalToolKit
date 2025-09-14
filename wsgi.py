# WSGI configuration for production deployment
import os
import sys
import logging
from app import create_app, initialize_app

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Validate required environment variables for production
required_env_vars = ['SESSION_SECRET']
missing_vars = []

for var in required_env_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg)
    raise EnvironmentError(error_msg)

# Initialize the application
try:
    initialize_app()
    application = create_app()
    logger.info("✅ WSGI application initialized successfully for production")
except Exception as e:
    logger.error(f"❌ Failed to initialize WSGI application: {e}")
    raise

# Production-specific configurations
if __name__ != '__main__':
    # We're running under a WSGI server
    logger.info("🚀 Running under WSGI server in production mode")