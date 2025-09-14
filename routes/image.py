# Image processing API routes for Universal Toolkit
from flask import Blueprint, request, jsonify, send_file
import threading
import os
from werkzeug.utils import secure_filename
from utils.image_wrapper import ImageProcessor
from utils.common import generate_task_id, get_progress, validate_file_content, allowed_file
from utils.config import OUTPUT_FOLDER, UPLOAD_FOLDER

image_bp = Blueprint('image_api', __name__)

# Initialize image processor
image_processor = ImageProcessor(OUTPUT_FOLDER)

@image_bp.route('/api/image/convert', methods=['POST'])
def convert_image():
    """Convert image format with quality options"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'jpg')
        quality = int(request.form.get('quality', 95))
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'Format file gambar tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def convert_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Convert image
                result_path = image_processor.convert_format(input_path, task_id, output_format, quality)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Konversi gambar gagal: {str(e)}')
        
        thread = threading.Thread(target=convert_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Konversi gambar dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@image_bp.route('/api/image/resize', methods=['POST'])
def resize_image():
    """Resize image with aspect ratio options"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        width = int(request.form.get('width', 800))
        height = int(request.form.get('height', 600))
        maintain_aspect = request.form.get('maintain_aspect', 'true').lower() == 'true'
        resize_method = request.form.get('method', 'lanczos')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'Format file gambar tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def resize_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Resize image
                result_path = image_processor.resize_image(input_path, task_id, width, height, maintain_aspect, resize_method)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Resize gambar gagal: {str(e)}')
        
        thread = threading.Thread(target=resize_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Resize gambar dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@image_bp.route('/api/image/enhance', methods=['POST'])
def enhance_image():
    """Enhance image with brightness, contrast, saturation, sharpness"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        brightness = float(request.form.get('brightness', 1.0))
        contrast = float(request.form.get('contrast', 1.0))
        saturation = float(request.form.get('saturation', 1.0))
        sharpness = float(request.form.get('sharpness', 1.0))
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'Format file gambar tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def enhance_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Enhance image
                result_path = image_processor.enhance_image(input_path, task_id, brightness, contrast, saturation, sharpness)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Peningkatan gambar gagal: {str(e)}')
        
        thread = threading.Thread(target=enhance_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Peningkatan gambar dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@image_bp.route('/api/image/filter', methods=['POST'])
def apply_filter():
    """Apply filters to image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        filter_type = request.form.get('filter', 'none')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'Format file gambar tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def filter_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Apply filter
                result_path = image_processor.apply_filters(input_path, task_id, filter_type)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Penerapan filter gagal: {str(e)}')
        
        thread = threading.Thread(target=filter_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Penerapan filter dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@image_bp.route('/api/image/info', methods=['POST'])
def get_image_info():
    """Get image file information immediately"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'Format file gambar tidak valid'}), 400
        
        # Save file temporarily
        task_id = generate_task_id()
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{task_id}_{filename}')
        file.save(temp_path)
        
        # Get image info
        info = image_processor.get_image_info(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if info:
            return jsonify({'success': True, 'info': info})
        else:
            return jsonify({'error': 'Gagal mendapatkan informasi gambar'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500