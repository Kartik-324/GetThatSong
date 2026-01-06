import streamlit as st
import requests
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="GetThatSong",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🎨 ULTRA-DARK NEON AESTHETIC CSS ---
st.markdown("""
    <style>
    /* 1. CORE DARK THEME */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(at 50% 0%, #1a1a2e 0%, #000000 80%);
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }

    /* 2. HIDE DEFAULTS */
    header, footer { visibility: hidden !important; }
    
    /* 3. GEMINI-STYLE AUTO-EXPANDING INPUT */
    .stTextArea textarea {
        background-color: #13131a !important; 
        color: #ffffff !important;            
        caret-color: #a855f7 !important;      
        border: 1px solid #2d2d3b !important;
        border-radius: 24px !important;
        padding: 14px 22px !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
        
        /* THE MAGIC SAUCE FOR AUTO-EXPANDING */
        min-height: 50px !important;
        height: auto !important;
        field-sizing: content !important;
        max-height: 300px !important;
        overflow-y: hidden !important;
    }
    
    /* Input Focus State */
    .stTextArea textarea:focus {
        background-color: #1a1a24 !important;
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3) !important;
    }
    
    /* Placeholder Visibility */
    .stTextArea textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
        font-weight: 400 !important;
    }

    /* Instructions (Press Ctrl+Enter) Visibility */
    [data-testid="InputInstructions"] {
        display: flex !important;
        color: #64748b !important;
        font-size: 0.75rem !important;
        margin-top: 6px !important;
        font-weight: 500 !important;
        justify-content: flex-end;
    }

    /* Remove Form Border */
    [data-testid="stForm"] { border: none; padding: 0; }

    /* 4. BUTTON STYLING */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0 2rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.4) !important;
        height: 50px !important;
        width: 100%; 
        margin-top: 0px !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.6) !important;
    }
    
    /* Small download button styling */
    div.stButton > button[kind="secondary"] {
        background: linear-gradient(90deg, #06b6d4, #3b82f6) !important;
        height: 45px !important;
        border-radius: 30px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 0 1.5rem !important;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4) !important;
        color: white !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        filter: brightness(1.2) !important;
        box-shadow: 0 0 25px rgba(6, 182, 212, 0.6) !important;
    }

    /* 5. CUSTOM LOADER */
    .loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 40px;
        padding: 30px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    .wave { display: flex; gap: 6px; height: 40px; align-items: center; }
    .bar {
        width: 6px;
        background: linear-gradient(to top, #3b82f6, #06b6d4);
        border-radius: 99px;
        animation: equalizer 0.8s ease-in-out infinite;
        box-shadow: 0 0 8px rgba(6, 182, 212, 0.6);
    }
    @keyframes equalizer {
        0%, 100% { height: 10px; opacity: 0.5; }
        50% { height: 35px; opacity: 1; }
    }
    .bar:nth-child(1) { animation-delay: 0.0s; }
    .bar:nth-child(2) { animation-delay: 0.1s; }
    .bar:nth-child(3) { animation-delay: 0.2s; }
    .bar:nth-child(4) { animation-delay: 0.1s; }
    .bar:nth-child(5) { animation-delay: 0.0s; }

    .loading-text {
        margin-top: 20px;
        font-size: 15px;
        color: #e2e8f0 !important;
        font-weight: 500;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* 6. RESULT CARDS */
    .result-card {
        background: rgba(20, 20, 25, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #06b6d4;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .result-card:hover {
        background: rgba(20, 20, 25, 0.8);
        border-color: #06b6d4;
        box-shadow: 0 0 30px rgba(6, 182, 212, 0.15);
        transform: translateY(-2px);
    }
    .song-title {
        color: #ffffff;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 4px;
        text-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    .song-artist { color: #94a3b8; font-size: 14px; font-weight: 400; }
    
    /* 7. DOWNLOAD & PLAY BUTTONS */
    .download-pill {
        background: linear-gradient(90deg, #06b6d4, #3b82f6);
        color: white;
        text-decoration: none;
        padding: 10px 25px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
    }
    .download-pill:hover {
        filter: brightness(1.2);
        box-shadow: 0 0 25px rgba(6, 182, 212, 0.6);
        color: white;
        text-decoration: none;
    }
    
    .play-pill {
        background: linear-gradient(90deg, #10b981, #059669);
        color: white;
        text-decoration: none;
        padding: 10px 25px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        cursor: pointer;
        border: none;
    }
    .play-pill:hover {
        filter: brightness(1.2);
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.6);
        color: white;
        text-decoration: none;
    }
    
    .button-group {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    /* Custom Audio Player Styling */
    .custom-audio-player {
        background: rgba(30, 30, 35, 0.8);
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
        backdrop-filter: blur(10px);
    }
    
    .audio-controls {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .play-button {
        width: 45px;
        height: 45px;
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
        flex-shrink: 0;
    }
    
    .play-button:hover {
        background: linear-gradient(135deg, #0891b2, #06b6d4);
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
    }
    
    .play-button:active {
        transform: scale(0.95);
    }
    
    /* Triangle Play Icon */
    .play-icon {
        width: 0;
        height: 0;
        border-left: 12px solid white;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
        margin-left: 3px;
    }
    
    /* Pause Icon */
    .pause-icon {
        display: flex;
        gap: 4px;
    }
    
    .pause-bar {
        width: 4px;
        height: 16px;
        background: white;
        border-radius: 2px;
    }
    
    .timeline-container {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .time-display {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 500;
        min-width: 45px;
    }
    
    .progress-bar {
        flex: 1;
        height: 6px;
        background: rgba(148, 163, 184, 0.3);
        border-radius: 3px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar:hover {
        height: 8px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #06b6d4, #3b82f6);
        border-radius: 3px;
        width: 0%;
        transition: width 0.1s linear;
        position: relative;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        right: -6px;
        top: 50%;
        transform: translateY(-50%);
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .volume-control {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .volume-icon {
        color: #94a3b8;
        cursor: pointer;
        font-size: 18px;
    }
    
    .volume-slider {
        width: 80px;
        height: 4px;
        background: rgba(148, 163, 184, 0.3);
        border-radius: 2px;
        cursor: pointer;
        position: relative;
    }
    
    .volume-fill {
        height: 100%;
        background: #06b6d4;
        border-radius: 2px;
        width: 70%;
    }
    
    /* 8. SUGGESTION BOX */
    .suggestion-box {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 16px;
        padding: 20px 25px;
        margin: 20px 0;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .suggestion-text {
        color: #c084fc;
        font-size: 16px;
        font-weight: 600;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper for Loader HTML
def render_loader(text):
    return f"""
    <div class="loader-container">
        <div class="wave">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </div>
        <div class="loading-text">{text}</div>
    </div>
    """

# --- HEADER ---
col_spacer, col_main, col_spacer2 = st.columns([1, 6, 1])
with col_main:
    st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>GetThatSong</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 40px;'>AI-Powered Audio Extraction Engine</p>", unsafe_allow_html=True)

    # --- INPUT FORM ---
    with st.form(key='search_form'):
        c1, c2 = st.columns([5, 1], vertical_alignment="top")
        
        with c1:
            query = st.text_area(
                "Search", 
                placeholder="Ask for song lists or download directly...", 
                label_visibility="collapsed"
            )
        
        with c2:
            submit = st.form_submit_button("Generate ✨", type="primary")

    # --- LOGIC ---
    if submit and query:
        loader = st.empty()
        final_area = st.container()

        try:
            # 1. Extraction with Intent Detection
            loader.markdown(render_loader("Analyzing Intent & Extracting Songs..."), unsafe_allow_html=True)
            
            extract_res = requests.post(f"{API_BASE_URL}/api/extract-songs", json={"query": query})
            if extract_res.status_code != 200:
                loader.empty()
                st.error(f"Error: {extract_res.text}")
                st.stop()
            
            data = extract_res.json()
            songs = data.get('songs', [])
            intent = data.get('intent', 'list')
            suggestion = data.get('suggestion')
            
            if not songs:
                loader.empty()
                st.warning("No songs found. Try being more specific!")
                st.stop()
            
            # --- LIST MODE: Show songs with individual download options ---
            if intent == "list":
                # Search YouTube for all songs first
                loader.markdown(render_loader("Finding Songs on YouTube..."), unsafe_allow_html=True)
                search_res = requests.post(f"{API_BASE_URL}/api/search-youtube", json=songs)
                
                if search_res.status_code != 200:
                    loader.empty()
                    st.error("Failed to search YouTube")
                    st.stop()
                
                songs_with_links = search_res.json().get('songs', [])
                
                # Download all songs automatically
                loader.markdown(render_loader("Preparing Downloads..."), unsafe_allow_html=True)
                valid_songs = [s for s in songs_with_links if s.get('youtube_url')]
                
                if valid_songs:
                    dl_res = requests.post(
                        f"{API_BASE_URL}/api/download-songs",
                        json={"songs": valid_songs}
                    )
                    
                    if dl_res.status_code == 200:
                        results = dl_res.json().get('songs', [])
                        loader.empty()
                        
                        with final_area:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown(f"### 🎵 Found {len(results)} Songs")
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Display each song with download link
                            for idx, song in enumerate(results):
                                if song['download_status'] == 'completed':
                                    fname = Path(song['file_path']).name
                                    stream_link = f"{API_BASE_URL}/api/stream-file/{fname}"
                                    dl_link = f"{API_BASE_URL}/api/download-file/{fname}"
                                    audio_id = f"audio_{idx}"
                                    
                                    # Use components.html for proper rendering
                                    import streamlit.components.v1 as components
                                    
                                    html_content = f"""
                                    <div class="result-card" style="background: rgba(20, 20, 25, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #06b6d4; border-radius: 12px; padding: 20px 25px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; backdrop-filter: blur(10px);">
                                        <div style="flex: 1;">
                                            <div style="color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 4px;">{song['title']}</div>
                                            <div style="color: #94a3b8; font-size: 14px; font-weight: 400;">{song['artist']}</div>
                                            
                                            <div style="background: rgba(30, 30, 35, 0.8); border-radius: 12px; padding: 15px; margin-top: 10px;">
                                                <audio id="{audio_id}" preload="metadata" style="display: none;">
                                                    <source src="{stream_link}" type="audio/mp4">
                                                    <source src="{stream_link}" type="audio/mpeg">
                                                </audio>
                                                
                                                <div style="display: flex; align-items: center; gap: 15px;">
                                                    <button id="btn_{audio_id}" style="width: 45px; height: 45px; background: linear-gradient(135deg, #06b6d4, #0891b2); border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);" onclick="togglePlay_{audio_id}()">
                                                        <div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>
                                                    </button>
                                                    
                                                    <div style="flex: 1; display: flex; align-items: center; gap: 10px;">
                                                        <span id="current_{audio_id}" style="color: #94a3b8; font-size: 12px; min-width: 45px;">0:00</span>
                                                        <div id="progressBar_{audio_id}" style="flex: 1; height: 6px; background: rgba(148, 163, 184, 0.3); border-radius: 3px; cursor: pointer; position: relative;" onclick="seek_{audio_id}(event)">
                                                            <div id="progress_{audio_id}" style="height: 100%; background: linear-gradient(90deg, #06b6d4, #3b82f6); border-radius: 3px; width: 0%; position: relative;">
                                                                <div style="position: absolute; right: -6px; top: 50%; transform: translateY(-50%); width: 12px; height: 12px; background: white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);"></div>
                                                            </div>
                                                        </div>
                                                        <span id="duration_{audio_id}" style="color: #94a3b8; font-size: 12px; min-width: 45px;">0:00</span>
                                                    </div>
                                                    
                                                    <span style="color: #94a3b8; cursor: pointer; font-size: 18px;" onclick="toggleMute_{audio_id}()">🔊</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div style="display: flex; gap: 10px; align-items: center; margin-left: 20px;">
                                            <a href="{dl_link}" download="{fname}" style="background: linear-gradient(90deg, #06b6d4, #3b82f6); color: white; text-decoration: none; padding: 10px 25px; border-radius: 30px; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);">
                                                ⬇ Download MP3
                                            </a>
                                        </div>
                                    </div>
                                    
                                    <script>
                                    (function() {{
                                        const audio = document.getElementById('{audio_id}');
                                        const btn = document.getElementById('btn_{audio_id}');
                                        const progressBar = document.getElementById('progress_{audio_id}');
                                        const currentTime = document.getElementById('current_{audio_id}');
                                        const duration = document.getElementById('duration_{audio_id}');
                                        
                                        function formatTime(seconds) {{
                                            const mins = Math.floor(seconds / 60);
                                            const secs = Math.floor(seconds % 60);
                                            return mins + ':' + (secs < 10 ? '0' : '') + secs;
                                        }}
                                        
                                        window.togglePlay_{audio_id} = function() {{
                                            // Pause all other audios
                                            document.querySelectorAll('audio').forEach(a => {{
                                                if (a.id !== '{audio_id}' && !a.paused) {{
                                                    a.pause();
                                                    const otherBtn = document.getElementById('btn_' + a.id);
                                                    if (otherBtn) {{
                                                        otherBtn.innerHTML = '<div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>';
                                                    }}
                                                }}
                                            }});
                                            
                                            if (audio.paused) {{
                                                audio.play();
                                                btn.innerHTML = '<div style="display: flex; gap: 4px;"><div style="width: 4px; height: 16px; background: white; border-radius: 2px;"></div><div style="width: 4px; height: 16px; background: white; border-radius: 2px;"></div></div>';
                                            }} else {{
                                                audio.pause();
                                                btn.innerHTML = '<div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>';
                                            }}
                                        }};
                                        
                                        window.seek_{audio_id} = function(e) {{
                                            const bar = document.getElementById('progressBar_{audio_id}');
                                            const rect = bar.getBoundingClientRect();
                                            const pos = (e.clientX - rect.left) / rect.width;
                                            audio.currentTime = pos * audio.duration;
                                        }};
                                        
                                        window.toggleMute_{audio_id} = function() {{
                                            audio.muted = !audio.muted;
                                        }};
                                        
                                        audio.addEventListener('loadedmetadata', function() {{
                                            duration.textContent = formatTime(audio.duration);
                                        }});
                                        
                                        audio.addEventListener('timeupdate', function() {{
                                            const progress = (audio.currentTime / audio.duration) * 100;
                                            progressBar.style.width = progress + '%';
                                            currentTime.textContent = formatTime(audio.currentTime);
                                        }});
                                        
                                        audio.addEventListener('ended', function() {{
                                            btn.innerHTML = '<div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>';
                                        }});
                                    }})();
                                    </script>
                                    """
                                    
                                    components.html(html_content, height=180)
                                else:
                                    st.markdown(f"""
                                    <div class="result-card" style="border-left-color: #ef4444;">
                                        <div>
                                            <div class="song-title" style="color: #ef4444;">{song['title']}</div>
                                            <div class="song-artist">{song['artist']}</div>
                                        </div>
                                        <div style="color: #64748b; font-size: 14px;">Download Failed</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        loader.empty()
                        st.error("Download failed.")
                else:
                    loader.empty()
                    st.warning("No songs found on YouTube.")
            
            # --- DOWNLOAD MODE: Process and download all ---
            else:  # intent == "download"
                # 2. Searching
                loader.markdown(render_loader("Scanning Global Audio Databases..."), unsafe_allow_html=True)
                search_res = requests.post(f"{API_BASE_URL}/api/search-youtube", json=songs)
                
                if search_res.status_code == 200:
                    songs_with_links = search_res.json().get('songs', [])
                    valid_songs = [s for s in songs_with_links if s.get('youtube_url')]
                else:
                    loader.empty()
                    st.error("Search failed.")
                    st.stop()

                # 3. Downloading
                if valid_songs:
                    loader.markdown(render_loader("Converting High-Fidelity Audio..."), unsafe_allow_html=True)
                    dl_res = requests.post(f"{API_BASE_URL}/api/download-songs", json={"songs": valid_songs})
                    
                    if dl_res.status_code == 200:
                        results = dl_res.json().get('songs', [])
                        loader.empty() 
                        
                        with final_area:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("### ☁️ Ready for Export")
                            
                            for idx, song in enumerate(results):
                                if song['download_status'] == 'completed':
                                    fname = Path(song['file_path']).name
                                    stream_link = f"{API_BASE_URL}/api/stream-file/{fname}"
                                    dl_link = f"{API_BASE_URL}/api/download-file/{fname}"
                                    audio_id = f"audio_dl_{idx}"
                                    
                                    import streamlit.components.v1 as components
                                    
                                    html_content = f"""
                                    <div style="background: rgba(20, 20, 25, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #06b6d4; border-radius: 12px; padding: 20px 25px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between;">
                                        <div style="flex: 1;">
                                            <div style="color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 4px;">{song['title']}</div>
                                            <div style="color: #94a3b8; font-size: 14px;">{song['artist']}</div>
                                            
                                            <div style="background: rgba(30, 30, 35, 0.8); border-radius: 12px; padding: 15px; margin-top: 10px;">
                                                <audio id="{audio_id}" preload="metadata" style="display: none;">
                                                    <source src="{stream_link}" type="audio/mp4">
                                                    <source src="{stream_link}" type="audio/mpeg">
                                                </audio>
                                                
                                                <div style="display: flex; align-items: center; gap: 15px;">
                                                    <button id="btn_{audio_id}" style="width: 45px; height: 45px; background: linear-gradient(135deg, #06b6d4, #0891b2); border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);" onclick="togglePlay_{audio_id}()">
                                                        <div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>
                                                    </button>
                                                    
                                                    <div style="flex: 1; display: flex; align-items: center; gap: 10px;">
                                                        <span id="current_{audio_id}" style="color: #94a3b8; font-size: 12px; min-width: 45px;">0:00</span>
                                                        <div id="progressBar_{audio_id}" style="flex: 1; height: 6px; background: rgba(148, 163, 184, 0.3); border-radius: 3px; cursor: pointer; position: relative;" onclick="seek_{audio_id}(event)">
                                                            <div id="progress_{audio_id}" style="height: 100%; background: linear-gradient(90deg, #06b6d4, #3b82f6); border-radius: 3px; width: 0%; position: relative;">
                                                                <div style="position: absolute; right: -6px; top: 50%; transform: translateY(-50%); width: 12px; height: 12px; background: white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);"></div>
                                                            </div>
                                                        </div>
                                                        <span id="duration_{audio_id}" style="color: #94a3b8; font-size: 12px; min-width: 45px;">0:00</span>
                                                    </div>
                                                    
                                                    <span style="color: #94a3b8; cursor: pointer; font-size: 18px;" onclick="toggleMute_{audio_id}()">🔊</span>
                                                </div>
                                            </div>
                                        </div>
                                        <a href="{dl_link}" download="{fname}" style="background: linear-gradient(90deg, #06b6d4, #3b82f6); color: white; text-decoration: none; padding: 10px 25px; border-radius: 30px; font-size: 14px; font-weight: 600; margin-left: 20px; box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);">
                                            ⬇ Download MP3
                                        </a>
                                    </div>
                                    
                                    <script>
                                    (function() {{
                                        const audio = document.getElementById('{audio_id}');
                                        const btn = document.getElementById('btn_{audio_id}');
                                        const progressBar = document.getElementById('progress_{audio_id}');
                                        const currentTime = document.getElementById('current_{audio_id}');
                                        const duration = document.getElementById('duration_{audio_id}');
                                        
                                        function formatTime(seconds) {{
                                            const mins = Math.floor(seconds / 60);
                                            const secs = Math.floor(seconds % 60);
                                            return mins + ':' + (secs < 10 ? '0' : '') + secs;
                                        }}
                                        
                                        window.togglePlay_{audio_id} = function() {{
                                            document.querySelectorAll('audio').forEach(a => {{
                                                if (a.id !== '{audio_id}' && !a.paused) {{
                                                    a.pause();
                                                    const otherBtn = document.getElementById('btn_' + a.id);
                                                    if (otherBtn) otherBtn.innerHTML = '<div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>';
                                                }}
                                            }});
                                            
                                            if (audio.paused) {{
                                                audio.play();
                                                btn.innerHTML = '<div style="display: flex; gap: 4px;"><div style="width: 4px; height: 16px; background: white; border-radius: 2px;"></div><div style="width: 4px; height: 16px; background: white; border-radius: 2px;"></div></div>';
                                            }} else {{
                                                audio.pause();
                                                btn.innerHTML = '<div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>';
                                            }}
                                        }};
                                        
                                        window.seek_{audio_id} = function(e) {{
                                            const bar = document.getElementById('progressBar_{audio_id}');
                                            const rect = bar.getBoundingClientRect();
                                            audio.currentTime = ((e.clientX - rect.left) / rect.width) * audio.duration;
                                        }};
                                        
                                        window.toggleMute_{audio_id} = function() {{ audio.muted = !audio.muted; }};
                                        
                                        audio.addEventListener('loadedmetadata', () => duration.textContent = formatTime(audio.duration));
                                        audio.addEventListener('timeupdate', () => {{
                                            progressBar.style.width = (audio.currentTime / audio.duration * 100) + '%';
                                            currentTime.textContent = formatTime(audio.currentTime);
                                        }});
                                        audio.addEventListener('ended', () => btn.innerHTML = '<div style="width: 0; height: 0; border-left: 12px solid white; border-top: 8px solid transparent; border-bottom: 8px solid transparent; margin-left: 3px;"></div>');
                                    }})();
                                    </script>
                                    """
                                    
                                    components.html(html_content, height=180)
                                else:
                                    st.markdown(f"""
                                    <div class="result-card" style="border-left-color: #ef4444;">
                                        <div>
                                            <div class="song-title" style="color: #ef4444;">{song['title']}</div>
                                            <div class="song-artist">Download Failed</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        loader.empty()
                        st.error("Download failed.")
                else:
                    loader.empty()
                    st.warning("No valid sources found.")

        except Exception as e:
            loader.empty()
            st.error(f"System Error: {str(e)}")

# --- FOOTER ---
st.markdown("<div style='text-align: center; margin-top: 50px; color: #334155; font-size: 12px;'>SYSTEM v2.1 • INTELLIGENT MUSIC DISCOVERY</div>", unsafe_allow_html=True)

# Add JavaScript for custom audio controls
st.markdown("""
<script>
let currentlyPlaying = null;

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins + ':' + (secs < 10 ? '0' : '') + secs;
}

function togglePlay(audioId, button) {
    const audio = document.getElementById(audioId);
    
    if (audio.paused) {
        // Pause all other audios
        document.querySelectorAll('audio').forEach(a => {
            if (a.id !== audioId && !a.paused) {
                a.pause();
                // Reset other buttons to play icon
                const otherButton = document.querySelector(`button[onclick*="${a.id}"]`);
                if (otherButton) {
                    otherButton.innerHTML = '<div class="play-icon"></div>';
                }
            }
        });
        
        audio.play();
        button.innerHTML = '<div class="pause-icon"><div class="pause-bar"></div><div class="pause-bar"></div></div>';
        currentlyPlaying = audioId;
    } else {
        audio.pause();
        button.innerHTML = '<div class="play-icon"></div>';
        currentlyPlaying = null;
    }
}

function seek(event, audioId) {
    const audio = document.getElementById(audioId);
    const progressBar = event.currentTarget;
    const rect = progressBar.getBoundingClientRect();
    const pos = (event.clientX - rect.left) / rect.width;
    audio.currentTime = pos * audio.duration;
}

function toggleMute(audioId) {
    const audio = document.getElementById(audioId);
    audio.muted = !audio.muted;
}

// Update progress and time for all audio elements
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.querySelectorAll('audio').forEach(audio => {
            const audioId = audio.id;
            
            // Update duration when loaded
            audio.addEventListener('loadedmetadata', function() {
                const durationEl = document.getElementById('duration-' + audioId);
                if (durationEl) {
                    durationEl.textContent = formatTime(audio.duration);
                }
            });
            
            // Update progress and current time
            audio.addEventListener('timeupdate', function() {
                const progress = (audio.currentTime / audio.duration) * 100;
                const progressFill = document.getElementById('progress-' + audioId);
                const currentEl = document.getElementById('current-' + audioId);
                
                if (progressFill) {
                    progressFill.style.width = progress + '%';
                }
                if (currentEl) {
                    currentEl.textContent = formatTime(audio.currentTime);
                }
            });
            
            // Reset button when audio ends
            audio.addEventListener('ended', function() {
                const button = document.querySelector(`button[onclick*="${audioId}"]`);
                if (button) {
                    button.innerHTML = '<div class="play-icon"></div>';
                }
                currentlyPlaying = null;
            });
        });
        
        // Spacebar control
        document.addEventListener('keydown', function(e) {
            if (e.code === 'Space' && currentlyPlaying) {
                e.preventDefault();
                const audio = document.getElementById(currentlyPlaying);
                const button = document.querySelector(`button[onclick*="${currentlyPlaying}"]`);
                if (audio && button) {
                    togglePlay(currentlyPlaying, button);
                }
            }
        });
    }, 1000);
});
</script>
""", unsafe_allow_html=True)