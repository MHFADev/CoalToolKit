# Document processing API routes for Universal Toolkit
from flask import Blueprint, request, jsonify, send_file
import threading
import os
from werkzeug.utils import secure_filename
from utils.pandoc_wrapper import DocumentProcessor
from utils.common import generate_task_id, get_progress, validate_file_content, allowed_file
from utils.config import OUTPUT_FOLDER, UPLOAD_FOLDER

document_bp = Blueprint('document_api', __name__)

# Initialize document processor
document_processor = DocumentProcessor(OUTPUT_FOLDER)

@document_bp.route('/api/document/convert', methods=['POST'])
def convert_document():
    """Convert document format using pandoc"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        output_format = request.form.get('format', 'pdf')
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'document'):
            return jsonify({'error': 'Format file dokumen tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def convert_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Convert document
                result_path = document_processor.convert_document(input_path, task_id, output_format)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Konversi dokumen gagal: {str(e)}')
        
        thread = threading.Thread(target=convert_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Konversi dokumen dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@document_bp.route('/api/document/extract-text', methods=['POST'])
def extract_text():
    """Extract plain text from document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'document'):
            return jsonify({'error': 'Format file dokumen tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def extract_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Extract text
                result_path = document_processor.extract_text(input_path, task_id)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Ekstraksi teks gagal: {str(e)}')
        
        thread = threading.Thread(target=extract_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Ekstraksi teks dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@document_bp.route('/api/document/to-markdown', methods=['POST'])
def convert_to_markdown():
    """Convert document to Markdown format"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'document'):
            return jsonify({'error': 'Format file dokumen tidak valid'}), 400
        
        task_id = generate_task_id()
        
        def convert_task():
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
                file.save(input_path)
                
                # Convert to markdown
                result_path = document_processor.convert_to_markdown(input_path, task_id)
                
                # Clean up input file
                if os.path.exists(input_path):
                    os.remove(input_path)
                    
            except Exception as e:
                from utils.common import update_progress
                update_progress(task_id, 0, 'error', f'Konversi markdown gagal: {str(e)}')
        
        thread = threading.Thread(target=convert_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'Konversi markdown dimulai'})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@document_bp.route('/api/document/info', methods=['POST'])
def get_document_info():
    """Get document information immediately"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_content(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if not allowed_file(file.filename, 'document'):
            return jsonify({'error': 'Format file dokumen tidak valid'}), 400
        
        # Save file temporarily
        task_id = generate_task_id()
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{task_id}_{filename}')
        file.save(temp_path)
        
        # Get document info
        info = document_processor.get_document_info(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if info:
            return jsonify({'success': True, 'info': info})
        else:
            return jsonify({'error': 'Gagal mendapatkan informasi dokumen'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500