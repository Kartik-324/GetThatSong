import yt_dlp
from typing import Optional
import traceback
import re


class YouTubeService:
    """Service to search YouTube videos using yt-dlp"""
    
    @staticmethod
    def search_video(query: str, limit: int = 1) -> Optional[str]:
        """
        Search YouTube for a video and return the first result URL using yt-dlp
        
        Args:
            query: Search query string
            limit: Number of results to fetch
            
        Returns:
            YouTube video URL or None if not found
        """
        try:
            print(f"\n🔍 Searching YouTube for: '{query}'")
            
            # Configure yt-dlp for searching
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just get info
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Use ytsearch: prefix to search YouTube
                search_url = f"ytsearch{limit}:{query}"
                
                try:
                    result = ydl.extract_info(search_url, download=False)
                    
                    if result and 'entries' in result:
                        entries = result['entries']
                        
                        # Filter out None entries
                        valid_entries = [e for e in entries if e is not None]
                        
                        if valid_entries:
                            first_video = valid_entries[0]
                            
                            # Get video ID
                            video_id = first_video.get('id')
                            video_title = first_video.get('title', 'Unknown')
                            
                            if video_id:
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                print(f"✅ Found: '{video_title}'")
                                print(f"   URL: {video_url}")
                                return video_url
                            else:
                                # Try to extract from URL or webpage_url
                                url = first_video.get('url') or first_video.get('webpage_url')
                                if url:
                                    print(f"✅ Found: '{video_title}'")
                                    print(f"   URL: {url}")
                                    return url
                
                except Exception as e:
                    print(f"⚠️ yt-dlp extraction error: {e}")
            
            print(f"❌ No results found for: '{query}'")
            return None
            
        except Exception as e:
            print(f"❌ Error searching YouTube: {e}")
            print(traceback.format_exc())
            return None
    
    @staticmethod
    def search_multiple(queries: list) -> dict:
        """
        Search multiple queries and return results
        
        Args:
            queries: List of search query strings
            
        Returns:
            Dictionary mapping query to video URL
        """
        results = {}
        for query in queries:
            url = YouTubeService.search_video(query)
            results[query] = url
        
        return results