# YouTube-DL wrapper for enhanced media downloading
import os
import yt_dlp
import gallery_dl
import logging
from typing import Dict, Optional, List
from .common import update_progress

logger = logging.getLogger(__name__)

class MediaDownloader:
    """Enhanced media downloader with yt-dlp and gallery-dl support"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        # Set ffmpeg path for yt-dlp to find ffmpeg and ffprobe
        import shutil
        self.ffmpeg_location = shutil.which('ffmpeg')
        
    def download_video(self, url: str, task_id: str, format_type: str = 'mp4', 
                      quality: str = 'best') -> bool:
        """Download video with yt-dlp"""
        try:
            update_progress(task_id, 10, 'processing', 'Mengambil informasi video...')
            
            output_template = os.path.join(self.output_folder, f'video_{task_id}.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': self._get_format_selector(format_type, quality),
                'noplaylist': True,
                'extract_flat': False,
                'ffmpeg_location': self.ffmpeg_location,
            }
            
            # Add post-processors if needed
            if format_type == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_type == 'mp4' and quality in ['2160p', '1440p', '1080p']:
                # Ensure video+audio merge for high quality downloads
                ydl_opts['merge_output_format'] = 'mp4'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
                
            update_progress(task_id, 30, 'processing', 'Memulai unduhan...')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            update_progress(task_id, 100, 'completed', 'Unduhan berhasil!')
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            update_progress(task_id, 0, 'error', f'Unduhan gagal: {str(e)}')
            return False
    
    def download_audio(self, url: str, task_id: str, format_type: str = 'mp3', 
                      quality: str = '320') -> bool:
        """Download audio only with yt-dlp - supports multiple formats"""
        try:
            update_progress(task_id, 10, 'processing', 'Mengambil informasi audio...')
            
            output_template = os.path.join(self.output_folder, f'audio_{task_id}.%(ext)s')
            
            # Get audio configuration based on format
            audio_config = self._get_audio_config(format_type, quality)
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': 'bestaudio/best',
                'noplaylist': True,
                'postprocessors': [audio_config],
                'ffmpeg_location': self.ffmpeg_location,
            }
            
            update_progress(task_id, 30, 'processing', 'Memulai unduhan audio...')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            update_progress(task_id, 100, 'completed', 'Unduhan audio berhasil!')
            return True
            
        except Exception as e:
            logger.error(f"Audio download failed: {e}")
            update_progress(task_id, 0, 'error', f'Unduhan audio gagal: {str(e)}')
            return False
    
    def download_playlist(self, url: str, task_id: str, max_downloads: int = 10) -> bool:
        """Download playlist with limit"""
        try:
            update_progress(task_id, 10, 'processing', 'Menganalisis playlist...')
            
            output_template = os.path.join(self.output_folder, f'playlist_{task_id}_%(playlist_index)s.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': 'best[height<=2160]',
                'playlistend': max_downloads,
                'ignoreerrors': True,
                'ffmpeg_location': self.ffmpeg_location,
            }
            
            update_progress(task_id, 30, 'processing', f'Mengunduh maksimal {max_downloads} video...')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            update_progress(task_id, 100, 'completed', 'Unduhan playlist berhasil!')
            return True
            
        except Exception as e:
            logger.error(f"Playlist download failed: {e}")
            update_progress(task_id, 0, 'error', f'Unduhan playlist gagal: {str(e)}')
            return False
    
    def download_gallery(self, url: str, task_id: str, site_type: str = 'auto') -> bool:
        """Download image galleries with gallery-dl"""
        try:
            update_progress(task_id, 10, 'processing', 'Menganalisis galeri...')
            
            output_dir = os.path.join(self.output_folder, f'gallery_{task_id}')
            os.makedirs(output_dir, exist_ok=True)
            
            # Configure gallery-dl
            config = {
                'extractor': {
                    'base-directory': output_dir,
                    'skip': True,  # Skip existing files
                },
            }
            
            update_progress(task_id, 30, 'processing', 'Mengunduh galeri...')
            
            # Use gallery-dl to download
            import subprocess
            result = subprocess.run([
                'gallery-dl', 
                '--config', '-',  # Read config from stdin
                url
            ], input=str(config), text=True, capture_output=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                update_progress(task_id, 100, 'completed', 'Unduhan galeri berhasil!')
                return True
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            logger.error(f"Gallery download failed: {e}")
            update_progress(task_id, 0, 'error', f'Unduhan galeri gagal: {str(e)}')
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'ffmpeg_location': self.ffmpeg_location,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    return None
                    
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': len(info.get('formats', [])),
                }
                
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None
    
    def _get_audio_config(self, format_type: str, quality: str) -> Dict:
        """Get audio configuration for different formats"""
        base_config = {
            'key': 'FFmpegExtractAudio',
            'preferredquality': quality,
        }
        
        # Format-specific configurations
        if format_type == 'mp3':
            base_config['preferredcodec'] = 'mp3'
        elif format_type == 'opus':
            base_config['preferredcodec'] = 'opus'
        elif format_type == 'm4a':
            base_config['preferredcodec'] = 'm4a'
        elif format_type == 'aac':
            base_config['preferredcodec'] = 'aac'
        elif format_type == 'flac':
            base_config['preferredcodec'] = 'flac'
            # FLAC is lossless, so don't limit quality for best results
            if quality in ['320', 'best']:
                del base_config['preferredquality']
        elif format_type == 'wav':
            base_config['preferredcodec'] = 'wav'
            # WAV is uncompressed, remove quality setting
            del base_config['preferredquality']
        elif format_type == 'ogg':
            base_config['preferredcodec'] = 'vorbis'
        elif format_type == 'webm':
            # For WebM container with Opus codec
            base_config['preferredcodec'] = 'opus'
            base_config['preferredformat'] = 'webm'
        else:
            # Default to mp3 for unknown formats
            base_config['preferredcodec'] = 'mp3'
            
        return base_config
    
    def _get_format_selector(self, format_type: str, quality: str) -> str:
        """Get format selector for yt-dlp based on format and quality"""
        if format_type == 'mp4':
            if quality == 'best':
                return 'best[ext=mp4]'
            elif quality == '2160p':
                # Ensure audio+video merge for 4K
                return 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]'
            elif quality == '1440p':
                # Ensure audio+video merge for 1440p
                return 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440][ext=mp4]'
            elif quality == '1080p':
                # Ensure audio+video merge for 1080p
                return 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]'
            elif quality == '720p':
                return 'best[height<=720][ext=mp4]'
            elif quality == '480p':
                return 'best[height<=480][ext=mp4]'
            elif quality == '360p':
                return 'best[height<=360][ext=mp4]'
        elif format_type == 'webm':
            return 'best[ext=webm]'
        elif format_type == 'mkv':
            return 'best[ext=mkv]:best'
        elif format_type == 'mp3':
            return 'bestaudio/best'
        return 'best'
        
        