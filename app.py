import os
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import yt_dlp
import ffmpeg
from PIL import Image
import qrcode
from qrcode import QRCode
import qrcode.constants
import mutagen
import pypandoc
import tempfile
import uuid
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs' 
ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'},
    'document': {'pdf', 'docx', 'doc', 'odt', 'txt', 'md', 'html', 'rtf'}
}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Progress tracking
progress_data = {}

def allowed_file(filename, file_type):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def update_progress(task_id, progress, status, message=""):
    progress_data[task_id] = {
        'progress': progress,
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/downloader')
def downloader():
    return render_template('downloader.html')

@app.route('/audio')
def audio():
    return render_template('audio.html')

@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/document')
def document():
    return render_template('document.html')

@app.route('/utilities')
def utilities():
    return render_template('utilities.html')

@app.route('/api/download', methods=['POST'])
def download_media():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format', 'mp4')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    task_id = str(uuid.uuid4())
    update_progress(task_id, 0, 'starting', 'Initializing download...')
    
    def download_task():
        try:
            update_progress(task_id, 10, 'processing', 'Fetching video information...')
            
            output_path = os.path.join(OUTPUT_FOLDER, f'download_{task_id}')
            
            ydl_opts = {
                'outtmpl': f'{output_path}.%(ext)s',
                'format': 'best' if format_type == 'mp4' else 'bestaudio',
            }
            
            if format_type == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            update_progress(task_id, 30, 'processing', 'Starting download...')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            update_progress(task_id, 100, 'completed', 'Download completed successfully!')
            
        except Exception as e:
            update_progress(task_id, 0, 'error', f'Download failed: {str(e)}')
    
    thread = threading.Thread(target=download_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/convert/audio', methods=['POST'])
def convert_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    output_format = request.form.get('format', 'mp3')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename or not allowed_file(file.filename, 'audio'):
        return jsonify({'error': 'Invalid audio file'}), 400
    
    task_id = str(uuid.uuid4())
    update_progress(task_id, 0, 'starting', 'Processing audio file...')
    
    def convert_task():
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
            file.save(input_path)
            
            update_progress(task_id, 30, 'processing', 'Converting audio format...')
            
            output_filename = f'converted_{task_id}.{output_format}'
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            (
                ffmpeg
                .input(input_path)
                .output(output_path, acodec='libmp3lame' if output_format == 'mp3' else None)
                .overwrite_output()
                .run(quiet=True)
            )
            
            os.remove(input_path)
            update_progress(task_id, 100, 'completed', f'Audio converted to {output_format}!')
            
        except Exception as e:
            update_progress(task_id, 0, 'error', f'Conversion failed: {str(e)}')
    
    thread = threading.Thread(target=convert_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/convert/image', methods=['POST'])
def convert_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    output_format = request.form.get('format', 'jpg')
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename or not allowed_file(file.filename, 'image'):
        return jsonify({'error': 'Invalid image file'}), 400
    
    task_id = str(uuid.uuid4())
    update_progress(task_id, 0, 'starting', 'Processing image...')
    
    def convert_task():
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
            file.save(input_path)
            
            update_progress(task_id, 30, 'processing', 'Converting image...')
            
            with Image.open(input_path) as img:
                if width and height:
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                output_filename = f'converted_{task_id}.{output_format}'
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                if output_format.lower() == 'jpg':
                    img = img.convert('RGB')
                
                img.save(output_path, format=output_format.upper())
            
            os.remove(input_path)
            update_progress(task_id, 100, 'completed', f'Image converted to {output_format}!')
            
        except Exception as e:
            update_progress(task_id, 0, 'error', f'Image conversion failed: {str(e)}')
    
    thread = threading.Thread(target=convert_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/convert/document', methods=['POST'])
def convert_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    output_format = request.form.get('format', 'pdf')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename or not allowed_file(file.filename, 'document'):
        return jsonify({'error': 'Invalid document file'}), 400
    
    task_id = str(uuid.uuid4())
    update_progress(task_id, 0, 'starting', 'Processing document...')
    
    def convert_task():
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, f'{task_id}_{filename}')
            file.save(input_path)
            
            update_progress(task_id, 30, 'processing', 'Converting document...')
            
            output_filename = f'converted_{task_id}.{output_format}'
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            pypandoc.convert_file(input_path, output_format, outputfile=output_path)
            
            os.remove(input_path)
            update_progress(task_id, 100, 'completed', f'Document converted to {output_format}!')
            
        except Exception as e:
            update_progress(task_id, 0, 'error', f'Document conversion failed: {str(e)}')
    
    thread = threading.Thread(target=convert_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/qr/generate', methods=['POST'])
def generate_qr():
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        task_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUT_FOLDER, f'qr_{task_id}.png')
        img.save(output_path)
        
        return jsonify({'task_id': task_id, 'message': 'QR code generated successfully!'})
    
    except Exception as e:
        return jsonify({'error': f'QR generation failed: {str(e)}'}), 500

@app.route('/api/metadata', methods=['POST'])
def extract_metadata():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        if not file.filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)
        
        audio_file = mutagen.File(temp_path)
        
        if audio_file is None:
            os.remove(temp_path)
            return jsonify({'error': 'Invalid or unsupported file format'}), 400
        
        metadata = {}
        for key, value in audio_file.items():
            if isinstance(value, list):
                metadata[key] = value[0] if value else ''
            else:
                metadata[key] = str(value)
        
        # Add file info
        metadata['filename'] = filename
        metadata['length'] = str(audio_file.info.length) if hasattr(audio_file.info, 'length') else 'Unknown'
        metadata['bitrate'] = str(audio_file.info.bitrate) if hasattr(audio_file.info, 'bitrate') else 'Unknown'
        
        os.remove(temp_path)
        
        return jsonify({'metadata': metadata})
    
    except Exception as e:
        return jsonify({'error': f'Metadata extraction failed: {str(e)}'}), 500

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    progress = progress_data.get(task_id, {
        'progress': 0,
        'status': 'unknown',
        'message': 'Task not found'
    })
    return jsonify(progress)

@app.route('/download/<task_id>')
def download_file(task_id):
    # Find the output file for this task
    for filename in os.listdir(OUTPUT_FOLDER):
        if task_id in filename:
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            return send_file(file_path, as_attachment=True)
    
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)