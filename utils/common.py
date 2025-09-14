# Common utility functions for Universal Toolkit
import os
import time
import uuid
import logging
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from .config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES

logger = logging.getLogger(__name__)

# Progress tracking dictionary
progress_data = {}

# Rate limiting dictionary - stores last request times by IP
rate_limit_data = {}

def allowed_file(filename, file_type):
    """Check if file extension is allowed for given file type"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def validate_file_content(file, file_type=None):
    """Validate file content and type with Indonesian error messages"""
    if not file or not file.filename:
        return False, "Tidak ada file yang diunggah"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > 100 * 1024 * 1024:  # 100MB
        return False, "File terlalu besar (maksimal 100MB)"
    
    if size == 0:
        return False, "File kosong"
    
    # Basic filename validation
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        return False, "Nama file tidak valid"
    
    # Enhanced MIME type validation using filename extension
    if file_type:
        try:
            # First check extension
            if not allowed_file(file.filename, file_type):
                return False, "Format file tidak valid"
                
            # Additional MIME type validation using mimetypes
            guessed_type, _ = mimetypes.guess_type(file.filename)
            if guessed_type and guessed_type not in ALLOWED_MIME_TYPES:
                logger.warning(f"Potentially unsafe MIME type: {guessed_type}")
                
        except Exception as e:
            logger.warning(f"MIME type validation failed: {e}")
    
    return True, "Valid"

def update_progress(task_id, progress, status, message=""):
    """Update progress for a task"""
    progress_data[task_id] = {
        'progress': progress,
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

def get_progress(task_id):
    """Get progress for a task"""
    return progress_data.get(task_id, {
        'progress': 0,
        'status': 'unknown',
        'message': 'Tugas tidak ditemukan'
    })

def generate_task_id():
    """Generate unique task ID"""
    return str(uuid.uuid4())

def safe_filename(filename, task_id=None):
    """Generate safe filename with optional task ID"""
    base_name = secure_filename(filename)
    if task_id:
        name, ext = os.path.splitext(base_name)
        return f"{task_id}_{name}{ext}"
    return base_name

def cleanup_old_files(folders, max_age_hours=1):
    """Clean up old files from specified folders"""
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for folder in folders:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                            logger.info(f"Membersihkan file lama: {file_path}")
    except Exception as e:
        logger.error(f"Error saat pembersihan: {e}")

def format_file_size(bytes_count):
    """Format file size in human readable format"""
    if bytes_count == 0:
        return "0 Bytes"
    
    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    i = 0
    
    while bytes_count >= k and i < len(sizes) - 1:
        bytes_count /= k
        i += 1
    
    return f"{bytes_count:.2f} {sizes[i]}"

def check_rate_limit(ip_address, operation='default', limit_seconds=60, max_requests=10):
    """Basic rate limiting - returns True if request is allowed, False if rate limited"""
    try:
        current_time = time.time()
        key = f"{ip_address}_{operation}"
        
        if key not in rate_limit_data:
            rate_limit_data[key] = []
        
        # Clean up old requests outside the time window
        rate_limit_data[key] = [
            req_time for req_time in rate_limit_data[key]
            if current_time - req_time < limit_seconds
        ]
        
        # Check if under the rate limit
        if len(rate_limit_data[key]) >= max_requests:
            return False
        
        # Add current request
        rate_limit_data[key].append(current_time)
        return True
        
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Allow request if rate limiting fails

def cleanup_rate_limit_data():
    """Clean up old rate limit data to prevent memory leaks"""
    try:
        current_time = time.time()
        keys_to_remove = []
        
        for key, timestamps in rate_limit_data.items():
            # Remove entries older than 1 hour
            rate_limit_data[key] = [
                ts for ts in timestamps if current_time - ts < 3600
            ]
            
            # Mark empty entries for removal
            if not rate_limit_data[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del rate_limit_data[key]
            
    except Exception as e:
        logger.error(f"Rate limit cleanup failed: {e}")