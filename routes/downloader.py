# Downloader API routes for Universal Toolkit
from flask import Blueprint, request, jsonify, send_file
import threading
import os
from utils.yt_dlp_wrapper import MediaDownloader
from utils.common import generate_task_id, get_progress
from utils.config import OUTPUT_FOLDER

downloader_bp = Blueprint('downloader_api', __name__)

# Initialize downloader
media_downloader = MediaDownloader(OUTPUT_FOLDER)

@downloader_bp.route('/api/download/video', methods=['POST'])
def download_video():
    """Download video with various quality options"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'mp4')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'URL diperlukan'}), 400
        
        task_id = generate_task_id()
        
        def download_task():
            media_downloader.download_video(url, task_id, format_type, quality)
        
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Unduhan video dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@downloader_bp.route('/api/download/audio', methods=['POST'])
def download_audio():
    """Download audio only"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'mp3')
        quality = data.get('quality', '192')
        
        if not url:
            return jsonify({'error': 'URL diperlukan'}), 400
        
        task_id = generate_task_id()
        
        def download_task():
            media_downloader.download_audio(url, task_id, format_type, quality)
        
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Unduhan audio dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@downloader_bp.route('/api/download/playlist', methods=['POST'])
def download_playlist():
    """Download playlist with limit"""
    try:
        data = request.get_json()
        url = data.get('url')
        max_downloads = data.get('max_downloads', 10)
        
        if not url:
            return jsonify({'error': 'URL diperlukan'}), 400
        
        if max_downloads > 50:
            return jsonify({'error': 'Maksimal 50 video per playlist'}), 400
        
        task_id = generate_task_id()
        
        def download_task():
            media_downloader.download_playlist(url, task_id, max_downloads)
        
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Unduhan playlist dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@downloader_bp.route('/api/download/gallery', methods=['POST'])
def download_gallery():
    """Download image gallery"""
    try:
        data = request.get_json()
        url = data.get('url')
        site_type = data.get('site_type', 'auto')
        
        if not url:
            return jsonify({'error': 'URL diperlukan'}), 400
        
        task_id = generate_task_id()
        
        def download_task():
            media_downloader.download_gallery(url, task_id, site_type)
        
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Unduhan galeri dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@downloader_bp.route('/api/video/info', methods=['POST'])
def get_video_info():
    """Get video information without downloading"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL diperlukan'}), 400
        
        info = media_downloader.get_video_info(url)
        
        if info:
            return jsonify({'success': True, 'info': info})
        else:
            return jsonify({'error': 'Gagal mendapatkan informasi video'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@downloader_bp.route('/api/progress/<task_id>')
def get_download_progress(task_id):
    """Get download progress"""
    try:
        progress = get_progress(task_id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@downloader_bp.route('/download/<task_id>')
def download_result(task_id):
    """Download the processed file"""
    try:
        # Find the output file for this task
        for filename in os.listdir(OUTPUT_FOLDER):
            if task_id in filename:
                file_path = os.path.join(OUTPUT_FOLDER, filename)
                return send_file(file_path, as_attachment=True)
        
        return jsonify({'error': 'File tidak ditemukan'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500