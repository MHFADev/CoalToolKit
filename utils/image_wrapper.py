# Image processing wrapper using Pillow and ImageMagick
import os
import subprocess
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import logging
from typing import Optional, List, Tuple, Dict
from .common import update_progress

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Comprehensive image processing with Pillow and ImageMagick"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
    def convert_format(self, input_path: str, task_id: str, output_format: str = 'jpg',
                      quality: int = 95) -> Optional[str]:
        """Convert image format with quality control"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengonversi format gambar...')
            
            output_filename = f'converted_image_{task_id}.{output_format.lower()}'
            output_path = os.path.join(self.output_folder, output_filename)
            
            with Image.open(input_path) as img:
                # Handle transparency for JPEG
                if output_format.lower() in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif output_format.lower() == 'png' and img.mode not in ('RGBA', 'RGB', 'P'):
                    img = img.convert('RGBA')
                
                update_progress(task_id, 60, 'processing', 'Menyimpan gambar...')
                
                save_kwargs = {}
                if output_format.lower() in ['jpg', 'jpeg']:
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                elif output_format.lower() == 'png':
                    save_kwargs['optimize'] = True
                elif output_format.lower() == 'webp':
                    save_kwargs['quality'] = quality
                    save_kwargs['method'] = 6
                
                img.save(output_path, format=output_format.upper(), **save_kwargs)
            
            update_progress(task_id, 100, 'completed', f'Gambar berhasil dikonversi ke {output_format}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Image conversion failed: {e}")
            update_progress(task_id, 0, 'error', f'Konversi gambar gagal: {str(e)}')
            return None
    
    def resize_image(self, input_path: str, task_id: str, width: int, height: int,
                    maintain_aspect: bool = True, resize_method: str = 'lanczos') -> Optional[str]:
        """Resize image with various options"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengubah ukuran gambar...')
            
            output_filename = f'resized_image_{task_id}.jpg'
            output_path = os.path.join(self.output_folder, output_filename)
            
            with Image.open(input_path) as img:
                original_width, original_height = img.size
                
                if maintain_aspect:
                    # Calculate aspect ratio
                    aspect_ratio = original_width / original_height
                    
                    if width / height > aspect_ratio:
                        # Height is the limiting factor
                        new_height = height
                        new_width = int(height * aspect_ratio)
                    else:
                        # Width is the limiting factor
                        new_width = width
                        new_height = int(width / aspect_ratio)
                else:
                    new_width, new_height = width, height
                
                # Choose resampling method
                resample_methods = {
                    'lanczos': Image.Resampling.LANCZOS,
                    'bicubic': Image.Resampling.BICUBIC,
                    'bilinear': Image.Resampling.BILINEAR,
                    'nearest': Image.Resampling.NEAREST,
                }
                
                resample = resample_methods.get(resize_method, Image.Resampling.LANCZOS)
                
                update_progress(task_id, 60, 'processing', 'Memproses resize...')
                
                resized_img = img.resize((new_width, new_height), resample)
                
                # Convert to RGB if necessary for JPEG
                if resized_img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', resized_img.size, (255, 255, 255))
                    if resized_img.mode == 'P':
                        resized_img = resized_img.convert('RGBA')
                    background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                    resized_img = background
                
                resized_img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            update_progress(task_id, 100, 'completed', f'Gambar berhasil diubah ke ukuran {new_width}x{new_height}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Image resize failed: {e}")
            update_progress(task_id, 0, 'error', f'Resize gambar gagal: {str(e)}')
            return None
    
    def batch_process(self, input_paths: List[str], task_id: str, operation: str,
                     **kwargs) -> List[str]:
        """Batch process multiple images"""
        try:
            update_progress(task_id, 10, 'processing', f'Memproses batch {len(input_paths)} gambar...')
            
            results = []
            total_images = len(input_paths)
            
            for i, input_path in enumerate(input_paths):
                # Update progress for each image
                progress = 10 + (80 * i // total_images)
                update_progress(task_id, progress, 'processing', 
                              f'Memproses gambar {i+1} dari {total_images}...')
                
                individual_task_id = f"{task_id}_{i}"
                
                if operation == 'resize':
                    result = self.resize_image(input_path, individual_task_id, 
                                             kwargs.get('width', 800), 
                                             kwargs.get('height', 600),
                                             kwargs.get('maintain_aspect', True))
                elif operation == 'convert':
                    result = self.convert_format(input_path, individual_task_id,
                                               kwargs.get('output_format', 'jpg'),
                                               kwargs.get('quality', 95))
                elif operation == 'enhance':
                    result = self.enhance_image(input_path, individual_task_id,
                                              kwargs.get('brightness', 1.0),
                                              kwargs.get('contrast', 1.0),
                                              kwargs.get('saturation', 1.0),
                                              kwargs.get('sharpness', 1.0))
                
                if result:
                    results.append(result)
            
            update_progress(task_id, 100, 'completed', f'Batch processing selesai! {len(results)} gambar berhasil.')
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            update_progress(task_id, 0, 'error', f'Batch processing gagal: {str(e)}')
            return []
    
    def enhance_image(self, input_path: str, task_id: str, brightness: float = 1.0,
                     contrast: float = 1.0, saturation: float = 1.0, 
                     sharpness: float = 1.0) -> Optional[str]:
        """Enhance image with brightness, contrast, saturation, and sharpness"""
        try:
            update_progress(task_id, 20, 'processing', 'Meningkatkan kualitas gambar...')
            
            output_filename = f'enhanced_image_{task_id}.jpg'
            output_path = os.path.join(self.output_folder, output_filename)
            
            with Image.open(input_path) as img:
                # Apply enhancements
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness)
                
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast)
                
                if saturation != 1.0:
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(saturation)
                
                if sharpness != 1.0:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(sharpness)
                
                update_progress(task_id, 60, 'processing', 'Menyimpan gambar yang ditingkatkan...')
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            update_progress(task_id, 100, 'completed', 'Gambar berhasil ditingkatkan!')
            return output_path
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            update_progress(task_id, 0, 'error', f'Peningkatan gambar gagal: {str(e)}')
            return None
    
    def apply_filters(self, input_path: str, task_id: str, filter_type: str) -> Optional[str]:
        """Apply various filters to image"""
        try:
            update_progress(task_id, 20, 'processing', f'Menerapkan filter {filter_type}...')
            
            output_filename = f'filtered_image_{task_id}.jpg'
            output_path = os.path.join(self.output_folder, output_filename)
            
            with Image.open(input_path) as img:
                if filter_type == 'blur':
                    filtered_img = img.filter(ImageFilter.BLUR)
                elif filter_type == 'sharpen':
                    filtered_img = img.filter(ImageFilter.SHARPEN)
                elif filter_type == 'emboss':
                    filtered_img = img.filter(ImageFilter.EMBOSS)
                elif filter_type == 'contour':
                    filtered_img = img.filter(ImageFilter.CONTOUR)
                elif filter_type == 'edge_enhance':
                    filtered_img = img.filter(ImageFilter.EDGE_ENHANCE)
                elif filter_type == 'grayscale':
                    filtered_img = ImageOps.grayscale(img)
                elif filter_type == 'sepia':
                    # Create sepia effect
                    filtered_img = ImageOps.colorize(ImageOps.grayscale(img), '#704214', '#C0A882')
                else:
                    filtered_img = img  # No filter
                
                update_progress(task_id, 60, 'processing', 'Menyimpan gambar yang difilter...')
                
                # Convert to RGB if necessary
                if filtered_img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', filtered_img.size, (255, 255, 255))
                    if filtered_img.mode == 'P':
                        filtered_img = filtered_img.convert('RGBA')
                    background.paste(filtered_img, mask=filtered_img.split()[-1] if filtered_img.mode == 'RGBA' else None)
                    filtered_img = background
                
                filtered_img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            update_progress(task_id, 100, 'completed', f'Filter {filter_type} berhasil diterapkan!')
            return output_path
            
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            update_progress(task_id, 0, 'error', f'Penerapan filter gagal: {str(e)}')
            return None
    
    def get_image_info(self, file_path: str) -> Optional[Dict]:
        """Get comprehensive image information"""
        try:
            with Image.open(file_path) as img:
                info = {
                    'filename': os.path.basename(file_path),
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P') and 'transparency' in img.info,
                }
                
                # Get additional info if available
                if hasattr(img, '_getexif') and img._getexif():
                    info['has_exif'] = True
                else:
                    info['has_exif'] = False
                
                # File size
                info['file_size'] = os.path.getsize(file_path)
                
                return info
                
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return None