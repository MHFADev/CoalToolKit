# Audio processing API routes for Universal Toolkit
from flask import Blueprint, request, jsonify, send_file
import threading
import os
from werkzeug.utils import secure_filename
from utils.ffmpeg_wrapper import FFmpegProcessor
from utils.utility_wrapper import UtilityProcessor
from utils.common import generate_task_id, get_progress, validate_file_content, allowed_file
from utils.config import OUTPUT_FOLDER, UPLOAD_FOLDER

audio_bp = Blueprint('audio_api', __name__)

# Initialize processors
ffmpeg_processor = FFmpegProcessor(OUTPUT_FOLDER)
utility_processor = UtilityProcessor(OUTPUT_FOLDER)

@audio_bp.route('/api/audio/convert', methods=['POST'])
def convert_audio():
    """Convert audio format with quality options"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'mp3')
        quality = request.form.get('quality', '192')
        sample_rate = request.form.get('sample_rate', type=int)
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'Format file audio tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def convert_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Convert audio
                result_path = ffmpeg_processor.convert_audio(input_path, task_id, output_format, quality, sample_rate)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Konversi audio gagal: {str(e)}')
        
        thread = threading.Thread(target=convert_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Konversi audio dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@audio_bp.route('/api/audio/metadata', methods=['POST'])
def extract_audio_metadata():
    """Extract comprehensive audio metadata"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'Format file audio tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def extract_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{task_id}_{filename}')
                file.save(temp_path)
                
                # Extract metadata
                metadata = utility_processor.extract_audio_metadata(temp_path, task_id)
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if metadata:
                    # Save metadata to file
                    import json
                    metadata_filename = f'metadata_{task_id}.json'
                    metadata_path = os.path.join(OUTPUT_FOLDER, metadata_filename)
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Ekstraksi metadata gagal: {str(e)}')
        
        thread = threading.Thread(target=extract_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Ekstraksi metadata dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@audio_bp.route('/api/audio/info', methods=['POST'])
def get_audio_info():
    """Get audio file information immediately"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'Format file audio tidak valid'}), 400
        
        # Save file temporarily
        task_id = generate_task_id()
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{task_id}_{filename}')
        file.save(temp_path)
        
        # Get audio info using ffmpeg
        info = ffmpeg_processor.get_media_info(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if info:
            return jsonify({'success': True, 'info': info})
        else:
            return jsonify({'error': 'Gagal mendapatkan informasi audio'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500