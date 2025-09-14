# FFmpeg wrapper for comprehensive audio/video processing
import os
import ffmpeg
import subprocess
import logging
from typing import Optional, Dict, List, Tuple
from .common import update_progress

logger = logging.getLogger(__name__)

class FFmpegProcessor:
    """Comprehensive FFmpeg wrapper for audio/video processing"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
    def _safe_eval_fraction(self, fraction_str: str) -> float:
        """Safely evaluate fraction string like '30/1' without using eval()"""
        try:
            if '/' not in fraction_str:
                return float(fraction_str)
            
            parts = fraction_str.split('/')
            if len(parts) != 2:
                return 0.0
                
            numerator = float(parts[0])
            denominator = float(parts[1])
            
            if denominator == 0:
                return 0.0
                
            return numerator / denominator
        except (ValueError, TypeError):
            return 0.0
        
    def convert_audio(self, input_path: str, task_id: str, output_format: str = 'mp3',
                     quality: str = '192', sample_rate: Optional[int] = None) -> Optional[str]:
        """Convert audio format with quality options"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengonversi format audio...')
            
            output_filename = f'audio_{task_id}.{output_format}'
            output_path = os.path.join(self.output_folder, output_filename)
            
            # Build ffmpeg stream
            stream = ffmpeg.input(input_path)
            
            # Audio codec options
            audio_options = {}
            if output_format == 'mp3':
                audio_options['acodec'] = 'libmp3lame'
                audio_options['audio_bitrate'] = f'{quality}k'
            elif output_format == 'aac':
                audio_options['acodec'] = 'aac'
                audio_options['audio_bitrate'] = f'{quality}k'
            elif output_format == 'ogg':
                audio_options['acodec'] = 'libvorbis'
                audio_options['audio_bitrate'] = f'{quality}k'
            elif output_format == 'flac':
                audio_options['acodec'] = 'flac'
            elif output_format == 'wav':
                audio_options['acodec'] = 'pcm_s16le'
                
            if sample_rate:
                audio_options['ar'] = sample_rate
                
            update_progress(task_id, 60, 'processing', 'Memproses audio...')
            
            stream = ffmpeg.output(stream, output_path, **audio_options)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            update_progress(task_id, 100, 'completed', f'Audio berhasil dikonversi ke {output_format}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            update_progress(task_id, 0, 'error', f'Konversi audio gagal: {str(e)}')
            return None
    
    def convert_video(self, input_path: str, task_id: str, output_format: str = 'mp4',
                     resolution: Optional[str] = None, crf: int = 23) -> Optional[str]:
        """Convert video format with compression options"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengonversi format video...')
            
            output_filename = f'video_{task_id}.{output_format}'
            output_path = os.path.join(self.output_folder, output_filename)
            
            stream = ffmpeg.input(input_path)
            
            # Video codec options
            video_options = {'crf': crf}
            if output_format == 'mp4':
                video_options['vcodec'] = 'libx264'
                video_options['acodec'] = 'aac'
            elif output_format == 'webm':
                video_options['vcodec'] = 'libvpx-vp9'
                video_options['acodec'] = 'libvorbis'
            elif output_format == 'mkv':
                video_options['vcodec'] = 'libx264'
                video_options['acodec'] = 'aac'
                
            # Resolution scaling (supports both upscaling and downscaling)
            if resolution:
                if resolution == '4K' or resolution == '2160p':
                    stream = ffmpeg.filter(stream, 'scale', 3840, 2160)
                elif resolution == '1440p':
                    stream = ffmpeg.filter(stream, 'scale', 2560, 1440)
                elif resolution == '1080p':
                    stream = ffmpeg.filter(stream, 'scale', 1920, 1080)
                elif resolution == '720p':
                    stream = ffmpeg.filter(stream, 'scale', 1280, 720)
                elif resolution == '480p':
                    stream = ffmpeg.filter(stream, 'scale', 854, 480)
                elif resolution == '360p':
                    stream = ffmpeg.filter(stream, 'scale', 640, 360)
                    
            update_progress(task_id, 60, 'processing', 'Memproses video...')
            
            stream = ffmpeg.output(stream, output_path, **video_options)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            update_progress(task_id, 100, 'completed', f'Video berhasil dikonversi ke {output_format}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Video conversion failed: {e}")
            update_progress(task_id, 0, 'error', f'Konversi video gagal: {str(e)}')
            return None
    
    def extract_audio_from_video(self, input_path: str, task_id: str, 
                               output_format: str = 'mp3') -> Optional[str]:
        """Extract audio from video file"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengekstrak audio dari video...')
            
            output_filename = f'extracted_audio_{task_id}.{output_format}'
            output_path = os.path.join(self.output_folder, output_filename)
            
            stream = ffmpeg.input(input_path)
            
            audio_options = {'vn': None}  # No video
            if output_format == 'mp3':
                audio_options['acodec'] = 'libmp3lame'
                audio_options['audio_bitrate'] = '192k'
            elif output_format == 'wav':
                audio_options['acodec'] = 'pcm_s16le'
                
            update_progress(task_id, 60, 'processing', 'Memproses ekstraksi audio...')
            
            stream = ffmpeg.output(stream, output_path, **audio_options)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            update_progress(task_id, 100, 'completed', 'Audio berhasil diekstrak!')
            return output_path
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            update_progress(task_id, 0, 'error', f'Ekstraksi audio gagal: {str(e)}')
            return None
    
    def merge_videos(self, video_paths: List[str], task_id: str) -> Optional[str]:
        """Merge multiple videos into one"""
        try:
            update_progress(task_id, 20, 'processing', 'Menggabungkan video...')
            
            output_filename = f'merged_video_{task_id}.mp4'
            output_path = os.path.join(self.output_folder, output_filename)
            
            # Create concat file for ffmpeg
            concat_file = os.path.join(self.output_folder, f'concat_{task_id}.txt')
            with open(concat_file, 'w') as f:
                for video_path in video_paths:
                    f.write(f"file '{video_path}'\n")
            
            update_progress(task_id, 60, 'processing', 'Memproses penggabungan...')
            
            (
                ffmpeg
                .input(concat_file, format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            # Clean up concat file
            os.remove(concat_file)
            
            update_progress(task_id, 100, 'completed', 'Video berhasil digabungkan!')
            return output_path
            
        except Exception as e:
            logger.error(f"Video merge failed: {e}")
            update_progress(task_id, 0, 'error', f'Penggabungan video gagal: {str(e)}')
            return None
    
    def split_video(self, input_path: str, task_id: str, start_time: str, 
                   duration: str) -> Optional[str]:
        """Split/trim video by time"""
        try:
            update_progress(task_id, 20, 'processing', 'Memotong video...')
            
            output_filename = f'split_video_{task_id}.mp4'
            output_path = os.path.join(self.output_folder, output_filename)
            
            update_progress(task_id, 60, 'processing', 'Memproses pemotongan...')
            
            (
                ffmpeg
                .input(input_path, ss=start_time, t=duration)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            update_progress(task_id, 100, 'completed', 'Video berhasil dipotong!')
            return output_path
            
        except Exception as e:
            logger.error(f"Video split failed: {e}")
            update_progress(task_id, 0, 'error', f'Pemotongan video gagal: {str(e)}')
            return None
    
    def add_subtitles(self, video_path: str, subtitle_path: str, task_id: str) -> Optional[str]:
        """Add subtitles to video"""
        try:
            update_progress(task_id, 20, 'processing', 'Menambahkan subtitle...')
            
            output_filename = f'subtitled_video_{task_id}.mp4'
            output_path = os.path.join(self.output_folder, output_filename)
            
            update_progress(task_id, 60, 'processing', 'Memproses subtitle...')
            
            video = ffmpeg.input(video_path)
            subtitle = ffmpeg.input(subtitle_path)
            
            (
                ffmpeg
                .output(video, subtitle, output_path, vcodec='copy', acodec='copy', scodec='mov_text')
                .overwrite_output()
                .run(quiet=True)
            )
            
            update_progress(task_id, 100, 'completed', 'Subtitle berhasil ditambahkan!')
            return output_path
            
        except Exception as e:
            logger.error(f"Subtitle addition failed: {e}")
            update_progress(task_id, 0, 'error', f'Penambahan subtitle gagal: {str(e)}')
            return None
    
    def get_media_info(self, file_path: str) -> Optional[Dict]:
        """Get comprehensive media information"""
        try:
            probe = ffmpeg.probe(file_path)
            
            info = {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate']),
                'format_name': probe['format']['format_name'],
                'streams': []
            }
            
            for stream in probe['streams']:
                stream_info = {
                    'index': stream['index'],
                    'codec_type': stream['codec_type'],
                    'codec_name': stream['codec_name'],
                }
                
                if stream['codec_type'] == 'video':
                    stream_info.update({
                        'width': stream.get('width'),
                        'height': stream.get('height'),
                        'fps': self._safe_eval_fraction(stream.get('r_frame_rate', '0/1')),
                    })
                elif stream['codec_type'] == 'audio':
                    stream_info.update({
                        'sample_rate': stream.get('sample_rate'),
                        'channels': stream.get('channels'),
                    })
                    
                info['streams'].append(stream_info)
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get media info: {e}")
            return None