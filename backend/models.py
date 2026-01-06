from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Song(BaseModel):
    """Model for individual song"""
    model_config = ConfigDict(from_attributes=True)
    
    title: str = Field(description="Song title")
    artist: str = Field(description="Artist name")
    youtube_url: Optional[str] = None
    download_status: Optional[str] = "pending"
    file_path: Optional[str] = None

class QueryRequest(BaseModel):
    """Request model for song query"""
    model_config = ConfigDict(from_attributes=True)
    
    query: str = Field(description="Natural language query for songs")

class SongExtractionResponse(BaseModel):
    """Response model after extracting songs from query"""
    model_config = ConfigDict(from_attributes=True)
    
    songs: List[Song]
    message: str
    intent: str = "list"  # "list" or "download"
    suggestion: Optional[str] = None  # Suggestion text for user

class DownloadRequest(BaseModel):
    """Request model for downloading songs"""
    model_config = ConfigDict(from_attributes=True)
    
    songs: List[Song]

class DownloadResponse(BaseModel):
    """Response model after download attempt"""
    model_config = ConfigDict(from_attributes=True)
    
    songs: List[Song]
    success_count: int
    failed_count: int
    message: str