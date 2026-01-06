from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import os

from models import (
    QueryRequest, 
    SongExtractionResponse, 
    DownloadRequest, 
    DownloadResponse,
    Song
)
from llm_agents import SongExtractionAgent, DownloadAgent
from youtube_service import YouTubeService
from downloader import MP3Downloader

app = FastAPI(title="AI Playlist Downloader API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
song_extraction_agent = SongExtractionAgent()
download_agent = DownloadAgent()
youtube_service = YouTubeService()
mp3_downloader = MP3Downloader()


@app.get("/")
async def root():
    return {
        "message": "AI Playlist Downloader API",
        "endpoints": {
            "extract_songs": "/api/extract-songs",
            "search_youtube": "/api/search-youtube",
            "download_songs": "/api/download-songs",
            "download_file": "/api/download-file/{filename}"
        }
    }


@app.post("/api/extract-songs", response_model=SongExtractionResponse)
async def extract_songs(request: QueryRequest):
    """
    Extract song information from natural language query using GPT-4
    Detects if user wants to list or download songs
    """
    try:
        print(f"\n📝 Received query: {request.query}")
        
        result = song_extraction_agent.extract_songs(request.query)
        
        print(f"✅ Extraction result: intent={result.get('intent')}, songs={len(result.get('songs', []))}")
        
        songs = result.get('songs', [])
        intent = result.get('intent', 'list')
        suggestion = result.get('suggestion')
        
        if not songs:
            message = "No songs could be extracted. Try: 'list songs by [artist]' or 'download [song]'"
        else:
            if intent == "list":
                message = f"Found {len(songs)} song(s) for you!"
            else:
                message = f"Ready to download {len(songs)} song(s)"
        
        return SongExtractionResponse(
            songs=songs,
            message=message,
            intent=intent,
            suggestion=suggestion
        )
        
    except Exception as e:
        import traceback
        print(f"❌ Error in extract_songs endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error extracting songs: {str(e)}")


@app.post("/api/search-youtube")
async def search_youtube(songs: List[Song]):
    """
    Search YouTube for each song and return URLs
    """
    try:
        results = []
        
        for song in songs:
            print(f"\n=== Processing song: {song.title} by {song.artist} ===")
            
            # Generate optimized search query using GPT-3.5
            search_query = download_agent.generate_search_query(song)
            print(f"Generated search query: {search_query}")
            
            # Search YouTube
            video_url = youtube_service.search_video(search_query)
            print(f"Video URL found: {video_url}")
            
            song.youtube_url = video_url
            song.download_status = "ready" if video_url else "not_found"
            
            results.append(song)
        
        success_count = sum(1 for s in results if s.youtube_url)
        
        return {
            "songs": results,
            "message": f"Found YouTube links for {success_count}/{len(results)} song(s)"
        }
        
    except Exception as e:
        print(f"Error in search_youtube: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {str(e)}")


@app.post("/api/download-songs", response_model=DownloadResponse)
async def download_songs(request: DownloadRequest):
    """
    Download songs as MP3 files
    """
    try:
        songs_data = [
            {
                'youtube_url': song.youtube_url,
                'title': song.title,
                'artist': song.artist
            }
            for song in request.songs
            if song.youtube_url
        ]
        
        if not songs_data:
            return DownloadResponse(
                songs=request.songs,
                success_count=0,
                failed_count=len(request.songs),
                message="No valid YouTube URLs to download"
            )
        
        # Download all songs
        download_results = mp3_downloader.download_batch(songs_data)
        
        # Update song objects with results
        updated_songs = []
        success_count = 0
        failed_count = 0
        
        for song, result in zip(request.songs, download_results):
            if result['success']:
                song.download_status = "completed"
                song.file_path = result['file_path']
                success_count += 1
            else:
                song.download_status = "failed"
                failed_count += 1
            
            updated_songs.append(song)
        
        return DownloadResponse(
            songs=updated_songs,
            success_count=success_count,
            failed_count=failed_count,
            message=f"Downloaded {success_count} song(s), {failed_count} failed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading songs: {str(e)}")


@app.get("/api/stream-file/{filename}")
async def stream_file(filename: str):
    """
    Stream audio file for in-browser playback
    """
    from fastapi.responses import StreamingResponse
    
    file_path = Path("downloads") / filename
    
    print(f"\n🎵 Stream request: {filename}")
    print(f"   Path: {file_path}")
    print(f"   Exists: {file_path.exists()}")
    
    if not file_path.exists():
        print(f"   ❌ File not found!")
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on extension
    ext = file_path.suffix.lower()
    media_types = {
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.webm': 'audio/webm',
        '.opus': 'audio/opus',
        '.ogg': 'audio/ogg',
    }
    
    media_type = media_types.get(ext, 'audio/mpeg')
    
    print(f"   📄 Type: {media_type}")
    
    # Stream for playback (inline)
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like
    
    return StreamingResponse(
        iterfile(),
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*"
        }
    )


@app.get("/api/download-file/{filename}")
async def download_file(filename: str):
    """
    Download audio file (forces download, not playback)
    """
    file_path = Path("downloads") / filename
    
    print(f"\n⬇️ Download request: {filename}")
    print(f"   Path: {file_path}")
    print(f"   Exists: {file_path.exists()}")
    
    if not file_path.exists():
        print(f"   ❌ File not found!")
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on extension
    ext = file_path.suffix.lower()
    media_types = {
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.webm': 'audio/webm',
        '.opus': 'audio/opus',
        '.ogg': 'audio/ogg',
    }
    
    media_type = media_types.get(ext, 'audio/mpeg')
    
    print(f"   📄 Type: {media_type}")
    print(f"   📦 Size: {file_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Force download with attachment header
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Allow-Origin": "*"
        }
    )


@app.get("/api/list-downloads")
async def list_downloads():
    """
    List all downloaded MP3 files
    """
    downloads_path = Path("downloads")
    
    if not downloads_path.exists():
        return {"files": []}
    
    files = [
        {
            "filename": f.name,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime
        }
        for f in downloads_path.glob("*.mp3")
    ]
    
    return {"files": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)