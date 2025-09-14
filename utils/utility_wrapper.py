# Utility wrapper for QR codes, metadata extraction, and other utilities
import os
import qrcode
from qrcode import QRCode
import qrcode.constants
import mutagen
import tempfile
import zipfile
import tarfile
import json
import logging
from typing import Optional, Dict, List, Any
from .common import update_progress

logger = logging.getLogger(__name__)

class UtilityProcessor:
    """Utility functions for QR codes, metadata, archives, etc."""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
    def generate_qr_code(self, text: str, task_id: str, 
                        error_correction: str = 'M', box_size: int = 10,
                        border: int = 4, fill_color: str = 'black',
                        back_color: str = 'white') -> Optional[str]:
        """Generate QR code with customization options"""
        try:
            update_progress(task_id, 20, 'processing', 'Membuat QR code...')
            
            # Error correction levels
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H,
            }
            
            qr = QRCode(
                version=1,
                error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
                box_size=box_size,
                border=border,
            )
            
            qr.add_data(text)
            qr.make(fit=True)
            
            update_progress(task_id, 60, 'processing', 'Menghasilkan gambar QR code...')
            
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            output_filename = f'qr_code_{task_id}.png'
            output_path = os.path.join(self.output_folder, output_filename)
            img.save(output_path)
            
            update_progress(task_id, 100, 'completed', 'QR code berhasil dibuat!')
            return output_path
            
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            update_progress(task_id, 0, 'error', f'Pembuatan QR code gagal: {str(e)}')
            return None
    
    def extract_audio_metadata(self, file_path: str, task_id: str) -> Optional[Dict]:
        """Extract comprehensive audio metadata"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengekstrak metadata audio...')
            
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                raise Exception("File audio tidak valid atau tidak didukung")
            
            metadata = {}
            
            # Extract common tags
            common_tags = [
                'TIT2',  # Title
                'TPE1',  # Artist
                'TALB',  # Album
                'TDRC',  # Date
                'TCON',  # Genre
                'TPE2',  # Album Artist
                'TRCK',  # Track Number
                'TPOS',  # Disc Number
                'TPE3',  # Conductor
                'TCOM',  # Composer
            ]
            
            for tag in common_tags:
                if tag in audio_file:
                    value = audio_file[tag]
                    if isinstance(value, list):
                        metadata[tag] = str(value[0]) if value else ''
                    else:
                        metadata[tag] = str(value)
            
            # Add file information
            info = audio_file.info
            metadata.update({
                'filename': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'duration': getattr(info, 'length', 0),
                'bitrate': getattr(info, 'bitrate', 0),
                'sample_rate': getattr(info, 'sample_rate', 0),
                'channels': getattr(info, 'channels', 0),
                'format': type(audio_file).__name__,
            })
            
            # Format duration
            duration_seconds = metadata.get('duration', 0)
            if duration_seconds > 0:
                minutes, seconds = divmod(int(duration_seconds), 60)
                hours, minutes = divmod(minutes, 60)
                metadata['duration_formatted'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            update_progress(task_id, 100, 'completed', 'Metadata audio berhasil diekstrak!')
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            update_progress(task_id, 0, 'error', f'Ekstraksi metadata gagal: {str(e)}')
            return None
    
    def create_archive(self, file_paths: List[str], task_id: str, 
                      archive_type: str = 'zip', archive_name: str = None) -> Optional[str]:
        """Create archive from multiple files"""
        try:
            update_progress(task_id, 20, 'processing', f'Membuat arsip {archive_type}...')
            
            if not archive_name:
                archive_name = f'archive_{task_id}'
            
            if archive_type == 'zip':
                output_filename = f'{archive_name}.zip'
                output_path = os.path.join(self.output_folder, output_filename)
                
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i, file_path in enumerate(file_paths):
                        progress = 20 + (60 * i // len(file_paths))
                        update_progress(task_id, progress, 'processing', 
                                      f'Menambahkan file {i+1} dari {len(file_paths)}...')
                        
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                        
            elif archive_type in ['tar', 'tar.gz', 'tar.bz2']:
                ext = archive_type.replace('tar', 'tar')
                if ext == 'tar':
                    mode = 'w'
                elif 'gz' in ext:
                    mode = 'w:gz'
                elif 'bz2' in ext:
                    mode = 'w:bz2'
                    
                output_filename = f'{archive_name}.{ext}'
                output_path = os.path.join(self.output_folder, output_filename)
                
                with tarfile.open(output_path, mode) as tarf:
                    for i, file_path in enumerate(file_paths):
                        progress = 20 + (60 * i // len(file_paths))
                        update_progress(task_id, progress, 'processing', 
                                      f'Menambahkan file {i+1} dari {len(file_paths)}...')
                        
                        arcname = os.path.basename(file_path)
                        tarf.add(file_path, arcname)
            
            update_progress(task_id, 100, 'completed', f'Arsip {archive_type} berhasil dibuat!')
            return output_path
            
        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            update_progress(task_id, 0, 'error', f'Pembuatan arsip gagal: {str(e)}')
            return None
    
    def extract_archive(self, archive_path: str, task_id: str) -> Optional[str]:
        """Extract archive to folder"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengekstrak arsip...')
            
            # Create extraction directory
            extract_dir = os.path.join(self.output_folder, f'extracted_{task_id}')
            os.makedirs(extract_dir, exist_ok=True)
            
            file_ext = os.path.splitext(archive_path)[1].lower()
            
            if file_ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    for i, file_name in enumerate(file_list):
                        progress = 20 + (60 * i // len(file_list))
                        update_progress(task_id, progress, 'processing', 
                                      f'Mengekstrak file {i+1} dari {len(file_list)}...')
                        zipf.extract(file_name, extract_dir)
                        
            elif file_ext in ['.tar', '.gz', '.bz2'] or '.tar.' in archive_path:
                with tarfile.open(archive_path, 'r') as tarf:
                    members = tarf.getmembers()
                    for i, member in enumerate(members):
                        progress = 20 + (60 * i // len(members))
                        update_progress(task_id, progress, 'processing', 
                                      f'Mengekstrak file {i+1} dari {len(members)}...')
                        tarf.extract(member, extract_dir)
            
            update_progress(task_id, 100, 'completed', 'Arsip berhasil diekstrak!')
            return extract_dir
            
        except Exception as e:
            logger.error(f"Archive extraction failed: {e}")
            update_progress(task_id, 0, 'error', f'Ekstraksi arsip gagal: {str(e)}')
            return None
    
    def generate_file_hash(self, file_path: str, task_id: str, 
                          hash_type: str = 'md5') -> Optional[Dict]:
        """Generate file hash (MD5, SHA1, SHA256)"""
        try:
            update_progress(task_id, 20, 'processing', f'Menghitung hash {hash_type.upper()}...')
            
            import hashlib
            
            hash_functions = {
                'md5': hashlib.md5(),
                'sha1': hashlib.sha1(),
                'sha256': hashlib.sha256(),
                'sha512': hashlib.sha512(),
            }
            
            if hash_type not in hash_functions:
                raise Exception(f"Hash type {hash_type} tidak didukung")
            
            hasher = hash_functions[hash_type]
            
            with open(file_path, 'rb') as f:
                file_size = os.path.getsize(file_path)
                bytes_read = 0
                
                while chunk := f.read(8192):
                    hasher.update(chunk)
                    bytes_read += len(chunk)
                    
                    progress = 20 + int(60 * bytes_read / file_size)
                    update_progress(task_id, progress, 'processing', 
                                  f'Menghitung hash... {bytes_read/file_size*100:.1f}%')
            
            hash_value = hasher.hexdigest()
            
            result = {
                'filename': os.path.basename(file_path),
                'file_size': file_size,
                'hash_type': hash_type.upper(),
                'hash_value': hash_value,
            }
            
            # Save hash to file
            hash_filename = f'hash_{task_id}.json'
            hash_path = os.path.join(self.output_folder, hash_filename)
            
            with open(hash_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            update_progress(task_id, 100, 'completed', f'Hash {hash_type.upper()} berhasil dihitung!')
            return result
            
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            update_progress(task_id, 0, 'error', f'Perhitungan hash gagal: {str(e)}')
            return None
    
    def convert_text_encoding(self, file_path: str, task_id: str, 
                            target_encoding: str = 'utf-8') -> Optional[str]:
        """Convert text file encoding"""
        try:
            update_progress(task_id, 20, 'processing', f'Mengonversi encoding ke {target_encoding}...')
            
            # Try to detect current encoding
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                source_encoding = result['encoding']
            
            if not source_encoding:
                source_encoding = 'utf-8'  # Default fallback
            
            update_progress(task_id, 40, 'processing', 
                          f'Terdeteksi encoding: {source_encoding}, mengonversi ke {target_encoding}...')
            
            # Read with source encoding
            with open(file_path, 'r', encoding=source_encoding) as f:
                content = f.read()
            
            # Write with target encoding
            output_filename = f'converted_encoding_{task_id}.txt'
            output_path = os.path.join(self.output_folder, output_filename)
            
            with open(output_path, 'w', encoding=target_encoding) as f:
                f.write(content)
            
            update_progress(task_id, 100, 'completed', 
                          f'Encoding berhasil dikonversi dari {source_encoding} ke {target_encoding}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Encoding conversion failed: {e}")
            update_progress(task_id, 0, 'error', f'Konversi encoding gagal: {str(e)}')
            return None