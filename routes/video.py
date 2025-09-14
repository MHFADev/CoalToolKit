# Video processing API routes for Universal Toolkit
from flask import Blueprint, request, jsonify, send_file
import threading
import os
from werkzeug.utils import secure_filename
from utils.ffmpeg_wrapper import FFmpegProcessor
from utils.common import generate_task_id, get_progress, validate_file_content, allowed_file
from utils.config import OUTPUT_FOLDER, UPLOAD_FOLDER

video_bp = Blueprint('video_api', __name__)

# Initialize video processor
video_processor = FFmpegProcessor(OUTPUT_FOLDER)

@video_bp.route('/api/video/convert', methods=['POST'])
def convert_video():
    """Convert video format with compression options"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'mp4')
        resolution = request.form.get('resolution', None)
        crf = int(request.form.get('crf', 23))
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Format file video tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def convert_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Convert video
                result_path = video_processor.convert_video(input_path, task_id, output_format, resolution, crf)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Konversi video gagal: {str(e)}')
        
        thread = threading.Thread(target=convert_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Konversi video dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@video_bp.route('/api/video/extract-audio', methods=['POST'])
def extract_audio():
    """Extract audio from video file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'mp3')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Format file video tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def extract_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Extract audio
                result_path = video_processor.extract_audio_from_video(input_path, task_id, output_format)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Ekstraksi audio gagal: {str(e)}')
        
        thread = threading.Thread(target=extract_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Ekstraksi audio dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@video_bp.route('/api/video/split', methods=['POST'])
def split_video():
    """Split/trim video by time"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        start_time = request.form.get('start_time', '00:00:00')
        duration = request.form.get('duration', '00:01:00')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Format file video tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def split_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Split video
                result_path = video_processor.split_video(input_path, task_id, start_time, duration)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Pemotongan video gagal: {str(e)}')
        
        thread = threading.Thread(target=split_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Pemotongan video dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@video_bp.route('/api/video/info', methods=['POST'])
def get_video_info():
    """Get video file information"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Format file video tidak valid'}), 400
        
        # Save file temporarily
        task_id = generate_task_id()
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{task_id}_{filename}')
        file.save(temp_path)
        
        # Get video info
        info = video_processor.get_media_info(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if info:
            return jsonify({'success': True, 'info': info})
        else:
            return jsonify({'error': 'Gagal mendapatkan informasi video'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500