# 🎵 GetThatSong - AI-Powered Music Downloader

GetThatSong is an intelligent AI-powered music downloader that understands natural language queries.
Users can simply describe the song or artist they want, and the system automatically finds the best match on YouTube.
It extracts and downloads high-quality audio without requiring video downloads.
The project offers a fast, simple, and user-friendly experience with built-in playback support.
Designed for personal use, it makes discovering and downloading music effortless.


![image alt](https://github.com/Kartik-324/GetThatSong/blob/44c8fefc0c80f2c41217dbea09876c3fb655748e/Screenshot%202026-01-03%20192449.png)


![GetThatSong – Song results list interface](https://github.com/Kartik-324/GetThatSong/blob/718fe245a6aef3a6615a70d48229c434ed1c6aeb/Screenshot%202026-01-03%20192541.png)


![GetThatSong – Song download options and playback UI](https://github.com/Kartik-324/GetThatSong/blob/718fe245a6aef3a6615a70d48229c434ed1c6aeb/Screenshot%202026-01-03%20192603.png)



---
## ✨ Features

- 🤖 **Dual AI Architecture**: GPT-4 for song extraction + GPT-3.5 for search optimization
- 🎯 **Natural Language Processing**: Just describe what you want in plain English
- 🎵 **Smart Search**: Automatically finds the best YouTube matches
- ⚡ **Fast Downloads**: Direct audio extraction without video (no FFmpeg required!)
- 🎨 **Beautiful UI**: Dark-themed, modern interface with custom audio player
- 📱 **Two Modes**: 
  - **List Mode**: Discover popular songs by artist
  - **Download Mode**: Direct download specific songs
- 🎧 **Built-in Player**: Preview songs before downloading with seekable timeline
- 💾 **Multiple Formats**: M4A (native), MP3 (with FFmpeg)

---

## 🎬 Demo

### Natural Language Queries
```
"show me hits of ed sheeran"
"download shape of you by ed sheeran"
"give me list of famous songs of arijit singh"
"get me some taylor swift songs"
```

### UI Preview

**Search & Discovery**

![Demo](https://via.placeholder.com/800x400/0a0a0a/06b6d4?text=GetThatSong+Demo)

*Custom audio player with play/pause, seek controls, and download buttons*

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- FFmpeg (optional, for MP3 conversion)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/ai-playlist-downloader.git
cd ai-playlist-downloader
```

2. **Set up Backend**
```bash
cd backend
pip install -r requirements.txt
```

3. **Set up Frontend**
```bash
cd ../frontend
pip install -r requirements.txt
```

4. **Configure API Key**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

5. **Run the Application**

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

6. **Open in Browser**
```
http://localhost:8501
```

---

## 📖 Usage

### Basic Examples

**1. Discover Songs by Artist:**
```
Input: "show me hits of justin bieber"
Result: Lists 5-8 popular songs with play & download options
```

**2. Download Specific Songs:**
```
Input: "download baby by justin bieber"
Result: Directly downloads the song
```

**3. Multiple Songs:**
```
Input: "download shape of you, perfect, and thinking out loud"
Result: Downloads all 3 songs
```

### Audio Player Controls

- **▶️ Play/Pause**: Click the triangle button
- **Seek**: Click anywhere on the progress bar
- **Volume**: Click speaker icon to mute/unmute
- **Download**: Click the blue download button

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance web framework
- **LangChain** - LLM orchestration framework
- **OpenAI GPT-4** - Song extraction and understanding
- **OpenAI GPT-3.5-turbo** - Search query optimization
- **yt-dlp** - YouTube search and audio download
- **Pydantic** - Data validation

### Frontend
- **Streamlit** - Interactive web UI
- **Custom HTML/CSS/JS** - Audio player components
- **Responsive Design** - Works on desktop and mobile

### Key Libraries
```
fastapi==0.115.0
langchain==0.3.13
openai==1.58.1
yt-dlp==2024.12.23
streamlit==1.29.0
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │ Natural Language Query
       ▼
┌─────────────────────────────────────┐
│   Frontend (Streamlit)              │
│   - Input handling                  │
│   - UI rendering                    │
│   - Audio player                    │
└──────┬──────────────────────────────┘
       │ HTTP REST API
       ▼
┌─────────────────────────────────────┐
│   Backend (FastAPI)                 │
│   ┌───────────────────────────────┐ │
│   │ Agent 1: GPT-4                │ │
│   │ - Extract songs from query    │ │
│   │ - Detect user intent          │ │
│   └───────────────────────────────┘ │
│   ┌───────────────────────────────┐ │
│   │ Agent 2: GPT-3.5              │ │
│   │ - Optimize search queries     │ │
│   └───────────────────────────────┘ │
│   ┌───────────────────────────────┐ │
│   │ YouTube Service (yt-dlp)      │ │
│   │ - Search YouTube              │ │
│   │ - Download audio              │ │
│   └───────────────────────────────┘ │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   External Services                 │
│   - OpenAI API                      │
│   - YouTube                         │
└─────────────────────────────────────┘
```

---

## 📂 Project Structure

```
ai-playlist-downloader/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Pydantic models
│   ├── llm_agents.py        # GPT-4 & GPT-3.5 agents
│   ├── youtube_service.py   # YouTube search
│   ├── downloader.py        # Audio download logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app.py              # Streamlit UI
│   └── requirements.txt    # Frontend dependencies
├── downloads/              # Downloaded audio files (gitignored)
├── .env                    # API keys (gitignored)
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Optional: Install FFmpeg for MP3 Conversion

**Without FFmpeg:** Downloads in M4A format (works everywhere!)

**With FFmpeg:** Automatically converts to MP3

**Installation:**
- **Mac:** `brew install ffmpeg`
- **Ubuntu:** `sudo apt install ffmpeg`
- **Windows:** [Download from ffmpeg.org](https://ffmpeg.org/download.html)

---

## 🔧 API Endpoints

### Backend API (FastAPI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/extract-songs` | Extract songs from query |
| POST | `/api/search-youtube` | Search YouTube for songs |
| POST | `/api/download-songs` | Download audio files |
| GET | `/api/stream-file/{id}` | Stream audio (for player) |
| GET | `/api/download-file/{id}` | Download audio file |
| GET | `/api/list-downloads` | List downloaded files |

---

## 🎯 How It Works

### 1. Query Processing
```
User Input: "show me hits of ed sheeran"
    ↓
GPT-4 Analyzes & Extracts:
- Intent: "list"
- Songs: ["Shape of You", "Perfect", "Thinking Out Loud", ...]
- Artist: "Ed Sheeran"
```

### 2. Search Optimization
```
For each song:
GPT-3.5 Optimizes Query:
"Shape of You" → "Shape of You Ed Sheeran official audio"
    ↓
yt-dlp Searches YouTube:
Returns: https://youtube.com/watch?v=ABC123
```

### 3. Audio Download
```
yt-dlp Downloads:
- Format: Best audio (M4A/WebM)
- Quality: 128-192 kbps
- Size: ~3-5 MB per song
- Location: downloads/ folder
```

### 4. Playback & Download
```
Two endpoints:
- /api/stream-file → Browser plays audio
- /api/download-file → Browser downloads file
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "OpenAI API Error"**
- Check if your API key is correct in `.env`
- Verify you have credits in your OpenAI account

**2. "YouTube Download Failed"**
- Some videos may be region-locked
- Try a different song or artist

**3. "FFmpeg Not Found"**
- This is optional! M4A files work fine
- Install FFmpeg if you specifically want MP3

**4. "Port Already in Use"**
- Backend default: Port 8000
- Frontend default: Port 8501
- Change ports if needed: `uvicorn main:app --port 8001`

---

## 📝 Notes

### Legal Disclaimer

This tool is for **personal use only**. Please respect:
- Copyright laws in your country
- YouTube's Terms of Service
- Artists' intellectual property rights

Consider supporting artists by:
- Streaming on official platforms (Spotify, Apple Music)
- Buying their music
- Attending concerts

### Cost Information

- OpenAI API usage incurs costs
- GPT-4: ~$0.03 per request
- GPT-3.5: ~$0.002 per request
- Monitor usage in [OpenAI Dashboard](https://platform.openai.com/usage)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Fork the repo
git clone https://github.com/YOUR_USERNAME/ai-playlist-downloader.git

# Create a branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

---


## 🙏 Acknowledgments

- **OpenAI** - For GPT-4 and GPT-3.5 APIs
- **yt-dlp** - For excellent YouTube download capabilities
- **FastAPI** - For the amazing web framework
- **Streamlit** - For rapid UI development

---


Made with ❤️ and 🎵

**If you found this helpful, please ⭐ star the repo!**

</div>
