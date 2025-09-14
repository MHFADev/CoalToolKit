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
            }
            
            # Add post-processors if needed
            if format_type == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_type == 'mp4' and quality != 'best':
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
                      quality: str = '192') -> bool:
        """Download audio only with yt-dlp"""
        try:
            update_progress(task_id, 10, 'processing', 'Mengambil informasi audio...')
            
            output_template = os.path.join(self.output_folder, f'audio_{task_id}.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': 'bestaudio/best',
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_type,
                    'preferredquality': quality,
                }],
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
                'format': 'best[height<=720]',
                'playlistend': max_downloads,
                'ignoreerrors': True,
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
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
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
    
    def _get_format_selector(self, format_type: str, quality: str) -> str:
        """Get format selector for yt-dlp based on format and quality"""
        if format_type == 'mp4':
            if quality == 'best':
                return 'best[ext=mp4]'
            elif quality == '720p':
                return 'best[height<=720][ext=mp4]'
            elif quality == '480p':
                return 'best[height<=480][ext=mp4]'
            elif quality == '360p':
                return 'best[height<=360][ext=mp4]'
        elif format_type == 'webm':
            return 'best[ext=webm]'
        elif format_type == 'mkv':
            return 'best[ext=mkv]'
            
        return 'best'