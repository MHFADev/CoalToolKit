# Main route handlers for Universal Toolkit
from flask import Blueprint, render_template
from utils.config import INDONESIAN_LABELS

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page"""
    tools = [
        {
            'name': 'downloader',
            'title': INDONESIAN_LABELS['downloader'],
            'description': 'Unduh video, audio, dan galeri dari berbagai platform',
            'icon': '⬇️',
            'url': '/downloader'
        },
        {
            'name': 'video',
            'title': INDONESIAN_LABELS['video'],
            'description': 'Konversi, kompres, gabung, dan pisahkan video',
            'icon': '🎥',
            'url': '/video'
        },
        {
            'name': 'audio',
            'title': INDONESIAN_LABELS['audio'],
            'description': 'Konversi format audio dan pemrosesan suara',
            'icon': '🎵',
            'url': '/audio'
        },
        {
            'name': 'image',
            'title': INDONESIAN_LABELS['image'],
            'description': 'Konversi format, resize, dan edit gambar',
            'icon': '🖼️',
            'url': '/image'
        },
        {
            'name': 'document',
            'title': INDONESIAN_LABELS['document'],
            'description': 'Konversi dokumen antar format (PDF, DOCX, ODT)',
            'icon': '📄',
            'url': '/document'
        },
        {
            'name': 'utilities',
            'title': INDONESIAN_LABELS['utilities'],
            'description': 'QR code, metadata, arsip, dan utilitas lainnya',
            'icon': '🛠️',
            'url': '/utilities'
        }
    ]
    
    return render_template('index.html', tools=tools, labels=INDONESIAN_LABELS)

@main_bp.route('/video')
def video():
    """Video tools page"""
    return render_template('video.html', labels=INDONESIAN_LABELS)

@main_bp.route('/downloader')
def downloader():
    """Media downloader page"""
    return render_template('downloader.html', labels=INDONESIAN_LABELS)

@main_bp.route('/audio')
def audio():
    """Audio tools page"""
    return render_template('audio.html', labels=INDONESIAN_LABELS)

@main_bp.route('/image')
def image():
    """Image tools page"""
    return render_template('image.html', labels=INDONESIAN_LABELS)

@main_bp.route('/document')
def document():
    """Document tools page"""
    return render_template('document.html', labels=INDONESIAN_LABELS)

@main_bp.route('/utilities')
def utilities():
    """Utilities page"""
    return render_template('utilities.html', labels=INDONESIAN_LABELS)