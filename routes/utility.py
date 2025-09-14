# Utility API routes for Universal Toolkit
from flask import Blueprint, request, jsonify, send_file
import threading
import os
from werkzeug.utils import secure_filename
from utils.utility_wrapper import UtilityProcessor
from utils.common import generate_task_id, get_progress, validate_file_content
from utils.config import OUTPUT_FOLDER, UPLOAD_FOLDER

utility_bp = Blueprint('utility_api', __name__)

# Initialize utility processor
utility_processor = UtilityProcessor(OUTPUT_FOLDER)

@utility_bp.route('/api/qr/generate', methods=['POST'])
def generate_qr_code():
    """Generate QR code with customization options"""
    try:
        data = request.get_json()
        text = data.get('text')
        error_correction = data.get('error_correction', 'M')
        box_size = data.get('box_size', 10)
        border = data.get('border', 4)
        fill_color = data.get('fill_color', 'black')
        back_color = data.get('back_color', 'white')
        
        if not text:
            return jsonify({'error': 'Teks diperlukan untuk membuat QR code'}), 400
        
        task_id = generate_task_id()
        
        def generate_task():
            utility_processor.generate_qr_code(text, task_id, error_correction, box_size, border, fill_color, back_color)
        
        thread = threading.Thread(target=generate_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Pembuatan QR code dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@utility_bp.route('/api/archive/create', methods=['POST'])
def create_archive():
    """Create archive from uploaded files"""
    try:
        if not request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        archive_type = request.form.get('archive_type', 'zip')
        archive_name = request.form.get('archive_name', 'archive')
        
        # Save all uploaded files
        task_id = generate_task_id()
        file_paths = []
        
        for key, file in request.files.items():
            if file and file.filename:
                # Validate each file
                is_valid, message = validate_file_content(file)
                if is_valid:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                    file.save(file_path)
                    file_paths.append(file_path)
        
        if not file_paths:
            return jsonify({'error': 'Tidak ada file valid yang ditemukan'}), 400
        
        def archive_task():
            try:
                # Create archive
                result_path = utility_processor.create_archive(file_paths, task_id, archive_type, archive_name)
                
                # Clean up uploaded files
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Pembuatan arsip gagal: {str(e)}')
        
        thread = threading.Thread(target=archive_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Pembuatan arsip dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@utility_bp.route('/api/archive/extract', methods=['POST'])
def extract_archive():
    """Extract archive file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if it's an archive file
        allowed_extensions = ['.zip', '.tar', '.gz', '.bz2']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Format file arsip tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def extract_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Extract archive
                result_path = utility_processor.extract_archive(input_path, task_id)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Ekstraksi arsip gagal: {str(e)}')
        
        thread = threading.Thread(target=extract_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Ekstraksi arsip dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@utility_bp.route('/api/hash/generate', methods=['POST'])
def generate_file_hash():
    """Generate file hash (MD5, SHA1, SHA256)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        hash_type = request.form.get('hash_type', 'md5')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        task_id = generate_task_id()
        
        def hash_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Generate hash
                result = utility_processor.generate_file_hash(input_path, task_id, hash_type)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Perhitungan hash gagal: {str(e)}')
        
        thread = threading.Thread(target=hash_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Perhitungan hash dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@utility_bp.route('/api/encoding/convert', methods=['POST'])
def convert_text_encoding():
    """Convert text file encoding"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        target_encoding = request.form.get('encoding', 'utf-8')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if it's a text file
        if not file.filename.lower().endswith(('.txt', '.md', '.csv', '.json', '.xml', '.html')):
            return jsonify({'error': 'Hanya file teks yang didukung'}), 400
        
        task_id = generate_task_id()
        
        def encoding_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Convert encoding
                result_path = utility_processor.convert_text_encoding(input_path, task_id, target_encoding)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Konversi encoding gagal: {str(e)}')
        
        thread = threading.Thread(target=encoding_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Konversi encoding dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500