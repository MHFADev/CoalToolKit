# Universal Toolkit - Modular Flask Application
import os
import logging
import threading
import time
import atexit
from flask import Flask, jsonify, send_file

# Import all route blueprints
from routes.main import main_bp
from routes.downloader import downloader_bp
from routes.video import video_bp
from routes.audio import audio_bp
from routes.image import image_bp
from routes.document import document_bp
from routes.utility import utility_bp

# Import utility functions
from utils.common import cleanup_old_files, get_progress
from utils.config import UPLOAD_FOLDER, OUTPUT_FOLDER

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    session_secret = os.environ.get('SESSION_SECRET')
    if not session_secret:
        raise ValueError('SESSION_SECRET environment variable must be set for production')
    app.secret_key = session_secret
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    
    # Register all blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(downloader_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(audio_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(utility_bp)
    
    # Common progress endpoint (used by all modules)
    @app.route('/api/progress/<task_id>')
    def api_get_progress(task_id):
        """Get progress for any task"""
        try:
            progress = get_progress(task_id)
            return jsonify(progress)
        except Exception as e:
            logger.error(f"Progress endpoint error: {str(e)[:100]}")
            return jsonify({'error': 'Gagal mendapatkan progress'}), 500
    
    # Common download endpoint (used by all modules)
    @app.route('/download/<task_id>')
    def api_download_file(task_id):
        """Download the processed file"""
        try:
            # Find the output file for this task
            for filename in os.listdir(OUTPUT_FOLDER):
                if task_id in filename:
                    file_path = os.path.join(OUTPUT_FOLDER, filename)
                    return send_file(file_path, as_attachment=True)
            
            return jsonify({'error': 'File tidak ditemukan'}), 404
            
        except Exception as e:
            logger.error(f"Download endpoint error: {str(e)[:100]}")
            return jsonify({'error': 'File tidak dapat diunduh'}), 500
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File terlalu besar. Maksimal ukuran adalah 100MB.'}), 413

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)[:100]}...")  # Log limited error info
        return jsonify({'error': 'Terjadi kesalahan sistem. Silakan coba lagi.'}), 500
    
    return app

def check_binary_dependencies():
    """Check if required binaries are available"""
    import shutil
    
    required_binaries = {
        'ffmpeg': 'Required for audio/video conversion',
        'pandoc': 'Required for document conversion',
        'convert': 'ImageMagick - Required for advanced image processing',
        'sox': 'Required for advanced audio processing'
    }
    
    available_binaries = {}
    
    for binary, description in required_binaries.items():
        if shutil.which(binary):
            available_binaries[binary] = True
            logger.info(f"✓ {binary}: Available")
        else:
            available_binaries[binary] = False
            logger.warning(f"✗ {binary}: Not available - {description}")
    
    # Check critical dependencies
    critical_missing = []
    if not available_binaries.get('ffmpeg'):
        critical_missing.append('ffmpeg')
    if not available_binaries.get('pandoc'):
        critical_missing.append('pandoc')
    
    if critical_missing:
        logger.error(f"Critical binaries missing: {', '.join(critical_missing)}")
        logger.error("Some core features will not work. Please install missing dependencies.")
        return False
    
    logger.info("All critical binaries are available")
    return True

def initialize_cleanup_scheduler():
    """Initialize periodic cleanup of old files"""
    def periodic_cleanup():
        """Run cleanup every hour"""
        while True:
            time.sleep(3600)  # Run every hour
            try:
                cleanup_old_files([UPLOAD_FOLDER, OUTPUT_FOLDER], max_age_hours=2)
            except Exception as e:
                logger.error(f"Error during periodic cleanup: {e}")
    
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("Periodic cleanup scheduler initialized")

def initialize_app():
    """Initialize the application with dependency checks and cleanup"""
    logger.info("🚀 Initializing Universal Toolkit...")
    
    # Create required directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    logger.info(f"Created directories: {UPLOAD_FOLDER}, {OUTPUT_FOLDER}")
    
    # Check binary dependencies
    if not check_binary_dependencies():
        logger.warning("⚠️ Some features may not work due to missing dependencies")
    
    # Initial cleanup
    cleanup_old_files([UPLOAD_FOLDER, OUTPUT_FOLDER], max_age_hours=1)
    logger.info("Initial cleanup completed")
    
    # Start cleanup scheduler
    initialize_cleanup_scheduler()
    
    logger.info("✅ Universal Toolkit initialized successfully")

# Create Flask app
app = create_app()

# Register cleanup on exit
atexit.register(lambda: cleanup_old_files([UPLOAD_FOLDER, OUTPUT_FOLDER], max_age_hours=0))

if __name__ == '__main__':
    initialize_app()
    
    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🌐 Starting Universal Toolkit on {host}:{port}")
    logger.info(f"🔧 Debug mode: {'enabled' if debug else 'disabled'}")
    
    app.run(host=host, port=port, debug=debug)