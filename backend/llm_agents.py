import os
import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import Song
from dotenv import load_dotenv

load_dotenv()


class SongExtractionAgent:
    """Agent 1: Extracts song information from user query using GPT-4"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
    def extract_songs(self, query: str) -> dict:
        """Extract songs from natural language query and detect intent"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a music information extraction expert. 
            You MUST ALWAYS return valid JSON, even if the query is unclear.
            
            INTENT DETECTION:
            - "list" intent: User wants to see/know about songs (e.g., "give me list of", "what are", "show me", "tell me about", "famous songs", "best songs")
            - "download" intent: User wants to download songs (e.g., "download", "get me", "I want")
            
            CRITICAL: You MUST return a JSON object with this EXACT structure (no extra text):
            {{
                "intent": "list",
                "songs": [
                    {{"title": "Song Name", "artist": "Artist Name"}}
                ],
                "suggestion": "Type 'download these songs' to get them!"
            }}
            
            EXAMPLES:
            
            Input: "give me list of famous songs of Justin Bieber"
            Output:
            {{
                "intent": "list",
                "songs": [
                    {{"title": "Baby", "artist": "Justin Bieber"}},
                    {{"title": "Sorry", "artist": "Justin Bieber"}},
                    {{"title": "Love Yourself", "artist": "Justin Bieber"}},
                    {{"title": "What Do You Mean", "artist": "Justin Bieber"}},
                    {{"title": "Peaches", "artist": "Justin Bieber"}},
                    {{"title": "Yummy", "artist": "Justin Bieber"}}
                ],
                "suggestion": "Type 'download these songs' to get them!"
            }}
            
            Input: "download Baby by Justin Bieber"
            Output:
            {{
                "intent": "download",
                "songs": [
                    {{"title": "Baby", "artist": "Justin Bieber"}}
                ],
                "suggestion": null
            }}
            
            Input: "what are Arijit Singh's best songs"
            Output:
            {{
                "intent": "list",
                "songs": [
                    {{"title": "Tum Hi Ho", "artist": "Arijit Singh"}},
                    {{"title": "Channa Mereya", "artist": "Arijit Singh"}},
                    {{"title": "Ae Dil Hai Mushkil", "artist": "Arijit Singh"}},
                    {{"title": "Kesariya", "artist": "Arijit Singh"}},
                    {{"title": "Satranga", "artist": "Arijit Singh"}},
                    {{"title": "Apna Bana Le", "artist": "Arijit Singh"}}
                ],
                "suggestion": "Say 'download these' when you're ready!"
            }}
            
            Input: "popular taylor swift songs"
            Output:
            {{
                "intent": "list",
                "songs": [
                    {{"title": "Shake It Off", "artist": "Taylor Swift"}},
                    {{"title": "Blank Space", "artist": "Taylor Swift"}},
                    {{"title": "Love Story", "artist": "Taylor Swift"}},
                    {{"title": "Anti-Hero", "artist": "Taylor Swift"}},
                    {{"title": "Cruel Summer", "artist": "Taylor Swift"}}
                ],
                "suggestion": "Type 'download these songs' to get them!"
            }}
            
            RULES:
            1. ALWAYS return valid JSON (no extra text before or after)
            2. For "list" queries: provide 5-8 popular songs by that artist
            3. For "download" queries: extract specific songs mentioned
            4. If query is vague but mentions an artist, assume "list" intent and show their hits
            5. Include full artist name with each song
            6. Never return plain text - ONLY JSON
            """),
            ("user", "{query}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"query": query})
        
        try:
            # Parse the JSON response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            print(f"GPT-4 Response: {content[:200]}...")  # Debug log
            
            result = json.loads(content)
            
            # Ensure it's a dict, not a list
            if isinstance(result, list):
                # If GPT returned a list, wrap it
                result = {
                    "intent": "download",
                    "songs": result,
                    "suggestion": None
                }
            
            # Convert songs to Song objects
            songs = [Song(**song_data) for song_data in result.get('songs', [])]
            
            return {
                'songs': songs,
                'intent': result.get('intent', 'list'),
                'suggestion': result.get('suggestion')
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response content: {response.content}")
            
            # Fallback: try to extract intent from the text
            content_lower = response.content.lower()
            if any(word in content_lower for word in ['download', 'get me', 'i want']):
                intent = 'download'
            else:
                intent = 'list'
            
            return {
                'songs': [],
                'intent': intent,
                'suggestion': "Sorry, I couldn't understand that. Try: 'list famous songs by [artist]' or 'download [song] by [artist]'"
            }
            
        except Exception as e:
            print(f"Error parsing songs: {e}")
            print(f"Response content: {response.content}")
            return {
                'songs': [],
                'intent': 'list',
                'suggestion': None
            }


class DownloadAgent:
    """Agent 2: Handles YouTube search and download coordination using GPT-3.5-turbo"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def generate_search_query(self, song: Song) -> str:
        """Generate optimized YouTube search query"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a YouTube search optimization expert.
            Generate the best search query to find the official or high-quality audio version of a song.
            Return ONLY the search query text, nothing else.
            
            Tips:
            - Include song title and artist
            - Add keywords like "official audio" or "official video" for better results
            - Keep it concise"""),
            ("user", "Song: {title} by {artist}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"title": song.title, "artist": song.artist})
        
        return response.content.strip()
    
    def validate_download(self, song: Song) -> dict:
        """Validate if song is ready for download"""
        
        return {
            "ready": bool(song.youtube_url),
            "song_title": song.title,
            "artist": song.artist,
            "url": song.youtube_url
        }