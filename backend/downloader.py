import os
import requests
import time
import yt_dlp
from pathlib import Path
from typing import Optional


class MP3Downloader:
    """Service to download YouTube videos as MP3 - tries multiple methods"""
    
    def __init__(self, download_path: str = "downloads"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)
    
    def download_as_mp3(self, youtube_url: str, song_title: str, artist: str) -> dict:
        """
        Download YouTube video as MP3 - tries web API first, then yt-dlp
        
        Args:
            youtube_url: YouTube video URL
            song_title: Song title for filename
            artist: Artist name for filename
            
        Returns:
            Dictionary with status and file path
        """
        print(f"\n🎵 Starting download: {song_title} by {artist}")
        print(f"   URL: {youtube_url}")
        
        # Method 1: Try using yt-dlp to download audio directly (no conversion needed)
        result = self._download_with_ytdlp_audio_only(youtube_url, song_title, artist)
        if result['success']:
            return result
        
        # Method 2: Try web API (y2mate or similar)
        print("   ⚠️ Trying alternative download method...")
        result = self._download_with_web_api(youtube_url, song_title, artist)
        if result['success']:
            return result
        
        # All methods failed
        return {
            'success': False,
            'error': 'All download methods failed. Please install FFmpeg for best results.',
            'file_path': None
        }
    
    def _download_with_ytdlp_audio_only(self, youtube_url: str, song_title: str, artist: str) -> dict:
        """
        Download using yt-dlp - downloads best audio format directly (m4a, opus, etc)
        No conversion needed, so no FFmpeg required!
        """
        try:
            safe_filename = self._sanitize_filename(f"{artist} - {song_title}")
            output_template = str(self.download_path / safe_filename)
            
            # First, try WITHOUT any post-processing (no FFmpeg needed)
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio',  # Prefer m4a, fallback to best audio
                'outtmpl': output_template + '.%(ext)s',
                'quiet': False,
                'no_warnings': False,
            }
            
            print("   ⬇️ Downloading audio (no conversion)...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                
                # Find the downloaded file
                possible_extensions = ['.m4a', '.webm', '.opus', '.ogg', '.mp4']
                final_path = None
                
                for ext in possible_extensions:
                    test_path = Path(output_template + ext)
                    if test_path.exists():
                        final_path = str(test_path)
                        break
                
                # If still not found, search for any file with the base name
                if not final_path:
                    for file in self.download_path.glob(f"{safe_filename}*"):
                        if file.suffix in ['.m4a', '.webm', '.opus', '.ogg', '.mp4', '.mp3']:
                            final_path = str(file)
                            break
                
                if final_path:
                    file_size = Path(final_path).stat().st_size / (1024 * 1024)
                    file_ext = Path(final_path).suffix
                    print(f"   ✅ Downloaded successfully!")
                    print(f"   📁 Format: {file_ext.upper()} audio")
                    print(f"   💾 Size: {file_size:.2f} MB")
                    print(f"   📂 Location: {final_path}")
                    
                    return {
                        'success': True,
                        'file_path': final_path,
                        'title': info.get('title', song_title),
                        'duration': info.get('duration', 0)
                    }
                else:
                    raise Exception("Download completed but file not found")
                
        except Exception as e:
            error_msg = str(e)
            
            # Don't show FFmpeg errors as warnings since we're not trying to convert
            if 'ffmpeg' not in error_msg.lower() and 'ffprobe' not in error_msg.lower():
                print(f"   ⚠️ yt-dlp method failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def _download_with_web_api(self, youtube_url: str, song_title: str, artist: str) -> dict:
        """
        Download using web conversion API as fallback
        """
        try:
            # Extract video ID
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                return {'success': False, 'error': 'Invalid URL', 'file_path': None}
            
            # Try multiple APIs
            apis = [
                f"https://api.vevioz.com/api/button/mp3/{video_id}",
                f"https://www.yt1s.com/api/ajaxSearch/mp3/{video_id}",
            ]
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            for api_url in apis:
                try:
                    print(f"   📡 Trying API: {api_url[:50]}...")
                    response = requests.get(api_url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        download_url = data.get('dlink') or data.get('url') or data.get('download_url')
                        
                        if download_url:
                            # Download the file
                            mp3_response = requests.get(download_url, headers=headers, timeout=60)
                            if mp3_response.status_code == 200:
                                safe_filename = self._sanitize_filename(f"{artist} - {song_title}")
                                file_path = self.download_path / f"{safe_filename}.mp3"
                                
                                with open(file_path, 'wb') as f:
                                    f.write(mp3_response.content)
                                
                                file_size = file_path.stat().st_size / (1024 * 1024)
                                print(f"   ✅ Downloaded via API! Size: {file_size:.2f} MB")
                                
                                return {
                                    'success': True,
                                    'file_path': str(file_path),
                                    'title': song_title,
                                    'duration': 0
                                }
                except Exception as e:
                    print(f"   ⚠️ API failed: {e}")
                    continue
            
            return {'success': False, 'error': 'All APIs failed', 'file_path': None}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'file_path': None}
    
    def _extract_video_id(self, youtube_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        import re
        
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename.strip()
    
    def download_batch(self, songs_data: list) -> list:
        """
        Download multiple songs
        
        Args:
            songs_data: List of dicts with youtube_url, title, and artist
            
        Returns:
            List of download results
        """
        results = []
        
        for song in songs_data:
            if not song.get('youtube_url'):
                results.append({
                    'success': False,
                    'title': song.get('title'),
                    'error': 'No YouTube URL provided'
                })
                continue
            
            result = self.download_as_mp3(
                youtube_url=song['youtube_url'],
                song_title=song['title'],
                artist=song['artist']
            )
            
            result['original_title'] = song['title']
            result['artist'] = song['artist']
            results.append(result)
            
            # Small delay between downloads
            time.sleep(1)
        
        return results