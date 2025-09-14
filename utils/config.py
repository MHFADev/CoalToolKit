# Configuration constants for Universal Toolkit
import os

# Directory paths
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# File type extensions
ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', '3gp', 'asf'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma', 'opus', 'mp2'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'ppm', 'pgm'},
    'document': {'pdf', 'docx', 'doc', 'odt', 'txt', 'md', 'html', 'rtf', 'epub', 'tex'}
}

# MIME type validation
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp',
    'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/aac', 'audio/flac', 'audio/x-m4a',
    'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo', 'video/webm',
    'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword', 'text/plain', 'text/markdown', 'text/html'
}

# Indonesian text labels
INDONESIAN_LABELS = {
    'downloader': 'Pengunduh Media',
    'video': 'Alat Video', 
    'audio': 'Alat Audio',
    'image': 'Alat Gambar',
    'document': 'Alat Dokumen',
    'utilities': 'Utilitas',
    'convert': 'Konversi',
    'upload_file': 'Unggah File',
    'choose_format': 'Pilih Format',
    'processing': 'Memproses...',
    'completed': 'Selesai!',
    'failed': 'Gagal',
    'download': 'Unduh',
    'generate_qr': 'Buat QR Code',
    'extract_metadata': 'Ekstrak Metadata'
}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)