import streamlit as st
import pandas as pd
import time
import base64

st.set_page_config(
    page_title="Serenity - Music Recommendation",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CLUSTER_COLUMN = "cluster"
DATA_PATH = "data/clustered_df.pkl"

MOOD_MAP = {
    "Happy": {"id": 0, "emoji": "☀️"},
    "Sad": {"id": 1, "emoji": "🌧️"},
    "Calm": {"id": 2, "emoji": "🌊"},
    "Angry": {"id": 3, "emoji": "🔥"},
}

MOOD_GRADIENTS = {
    "Happy": "linear-gradient(135deg, #fbbf24, #f59e0b, #ea580c)",
    "Sad": "linear-gradient(135deg, #2563eb, #4338ca, #1e293b)",
    "Calm": "linear-gradient(135deg, #34d399, #14b8a6, #0891b2)",
    "Angry": "linear-gradient(135deg, #e11d48, #dc2626, #ea580c)",
}

MOOD_COLORS = {
    "Happy": ("#fbbf24", "#f59e0b", "#ea580c"),
    "Sad": ("#2563eb", "#4338ca", "#1e293b"),
    "Calm": ("#34d399", "#14b8a6", "#0891b2"),
    "Angry": ("#e11d48", "#dc2626", "#ea580c"),
}

MOOD_QUOTES = {
    "Happy": "Feel the sunshine through the sound",
    "Sad": "Even the blues sing beautifully",
    "Calm": "Breathe in the rhythm of peace",
    "Angry": "Turn your fire into rhythm",
}

if "page" not in st.session_state:
    st.session_state.page = "home"
if "mood" not in st.session_state:
    st.session_state.mood = None
if "songs" not in st.session_state:
    st.session_state.songs = []
if "loading" not in st.session_state:
    st.session_state.loading = False


@st.cache_data
def load_data():
    try:
        df = pd.read_pickle(DATA_PATH)
        return df
    except FileNotFoundError:
        st.error("Data file not found. Check your data/ directory.")
        return pd.DataFrame()


def get_songs(mood_id):
    df = load_data()
    if df.empty:
        return []
    songs_in_mood = df[df[CLUSTER_COLUMN] == mood_id]
    if songs_in_mood.empty:
        return []
    recommended = songs_in_mood.sample(5)[["song_name", "uri"]]
    return recommended.to_dict("records")


def get_spotify_embed_url(uri):
    if not uri:
        return None
    track_id = uri.split(":").pop()
    return f"https://open.spotify.com/embed/track/{track_id}"


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        * {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: #0a0a0a;
        }

        .stApp > header {
            background-color: transparent;
        }

        div[data-testid="stToolbar"] {
            display: none;
        }

        div[data-testid="stDecoration"] {
            display: none;
        }

        #MainMenu {display: none;}
        footer {display: none !important;}

        .header {
            padding: 2rem 4rem;
            border-bottom: 1px solid #27272a;
            background: rgba(10, 10, 10, 0.5);
            backdrop-filter: blur(12px);
        }

        .header-content {
            max-width: 1280px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand {
            font-size: 1.875rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            color: white;
        }

        .brand-dot {
            color: #0097b2;
        }

        .hero {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 0 1.5rem;
            min-height: 70vh;
        }

        .hero-title {
            font-size: 4.5rem;
            font-weight: 900;
            letter-spacing: -0.025em;
            color: white;
            margin-bottom: 1.5rem;
            line-height: 1.1;
        }

        .hero-emotion {
            color: #0097b2;
        }

        .hero-subtitle {
            color: #a1a1aa;
            font-size: 1.25rem;
            max-width: 32rem;
            margin: 0 auto 2.5rem;
            line-height: 1.625;
        }

        .cta-button {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            background: #0097b2;
            color: white;
            padding: 1rem 2rem;
            border-radius: 16px;
            font-size: 1.125rem;
            font-weight: 700;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }

        .cta-button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 151, 178, 0.4);
        }

        .footer {
            width: 100%;
            padding: 2.5rem 1.5rem;
            border-top: 1px solid #27272a;
            background: #09090b;
            text-align: center;
        }

        .footer-brand {
            font-weight: 700;
            color: #0097b2;
            font-size: 1.125rem;
            margin-bottom: 0.25rem;
        }

        .footer-text {
            color: #71717a;
            font-size: 0.875rem;
        }

        .footer-links {
            margin-top: 1rem;
            display: flex;
            justify-content: center;
            gap: 1rem;
            font-size: 0.75rem;
            font-weight: 500;
            color: #71717a;
        }

        .footer-links a {
            color: #a1a1aa;
            text-decoration: none;
            transition: color 0.2s;
        }

        .footer-links a:hover {
            color: #0097b2;
        }

        .mood-section {
            max-width: 1280px;
            margin: 0 auto;
            width: 100%;
            text-align: center;
            padding: 3rem 1.5rem;
        }

        .mood-heading {
            font-size: 3rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
        }

        .mood-subtitle {
            color: #a1a1aa;
            font-size: 1.125rem;
            margin-bottom: 3rem;
        }

        .mood-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2rem;
            max-width: 1024px;
            margin: 0 auto;
        }

        .mood-card {
            aspect-ratio: 1;
            border-radius: 24px;
            overflow: hidden;
            cursor: pointer;
            position: relative;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            transition: all 0.3s;
            border: none;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .mood-card:hover {
            transform: scale(1.05) translateY(-5px);
        }

        .mood-card-overlay {
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.1);
            transition: background 0.3s;
        }

        .mood-card:hover .mood-card-overlay {
            background: transparent;
        }

        .mood-card-content {
            position: relative;
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .mood-icon {
            font-size: 3rem;
            margin-bottom: 0.75rem;
            filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
        }

        .mood-name {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .results-container {
            position: relative;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 5rem 1.5rem;
            overflow: hidden;
        }

        .results-gradient {
            position: absolute;
            inset: 0;
            opacity: 0.4;
            filter: blur(64px);
            z-index: 0;
        }

        .results-header {
            position: relative;
            text-align: center;
            margin-bottom: 2.5rem;
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .results-aura {
            position: absolute;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            filter: blur(80px);
            animation: pulse-aura 5s ease-in-out infinite;
        }

        @keyframes pulse-aura {
            0%, 100% { transform: scale(1); opacity: 0.4; }
            50% { transform: scale(1.3); opacity: 0.8; }
        }

        .results-title {
            font-size: 3.75rem;
            font-weight: 800;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 25px rgba(0, 255, 200, 0.3));
        }

        .results-quote {
            margin-top: 1rem;
            font-size: 1.25rem;
            font-style: italic;
            font-weight: 300;
        }

        .loader-container {
            position: relative;
            z-index: 20;
            margin-top: 5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .loader-bars {
            display: flex;
            gap: 0.75rem;
        }

        .loader-bar {
            width: 8px;
            border-radius: 999px;
            animation: bar-loading 0.9s ease-in-out infinite;
        }

        @keyframes bar-loading {
            0%, 100% { transform: scaleY(1); opacity: 0.5; }
            50% { transform: scaleY(2); opacity: 1; }
        }

        .loader-text {
            margin-top: 1.5rem;
            color: #9ca3af;
            font-size: 0.875rem;
            letter-spacing: 0.05em;
            animation: pulse-text 2s ease-in-out infinite;
        }

        @keyframes pulse-text {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        .songs-grid {
            position: relative;
            z-index: 10;
            width: 100%;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2.5rem;
            margin-top: 2.5rem;
            max-width: 1200px;
        }

        .song-card {
            border-radius: 24px;
            overflow: hidden;
            background: rgba(24, 24, 27, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(24px);
            box-shadow: 0 0 40px rgba(0, 255, 180, 0.15);
            transition: all 0.7s;
            position: relative;
        }

        .song-card:hover {
            box-shadow: 0 0 60px rgba(0, 255, 200, 0.25);
        }

        .song-card-gradient {
            position: absolute;
            inset: 0;
            opacity: 0.1;
        }

        .song-card-content {
            position: relative;
            z-index: 10;
            padding: 1.5rem;
        }

        .song-card iframe {
            border-radius: 16px;
            box-shadow: 0 0 30px rgba(0, 255, 150, 0.1);
            transition: all 0.7s;
        }

        .song-card:hover iframe {
            box-shadow: 0 0 40px rgba(0, 255, 200, 0.3);
        }

        .back-button {
            position: absolute;
            top: 1.5rem;
            left: 1.5rem;
            background: rgba(31, 41, 55, 0.7);
            color: white;
            font-size: 0.875rem;
            padding: 0.5rem 1rem;
            border-radius: 999px;
            border: none;
            cursor: pointer;
            backdrop-filter: blur(12px);
            z-index: 20;
            transition: all 0.2s;
        }

        .back-button:hover {
            background: rgba(5, 150, 105, 0.8);
        }

        .recommend-more-btn {
            margin-top: 4rem;
            padding: 0.75rem 1.5rem;
            border-radius: 999px;
            background: #0097b2;
            color: white;
            font-weight: 600;
            font-size: 0.875rem;
            letter-spacing: 0.025em;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 0 20px rgba(0, 151, 178, 0.3);
            z-index: 20;
            position: relative;
        }

        .recommend-more-btn:hover {
            background: #007a93;
            box-shadow: 0 0 30px rgba(0, 151, 178, 0.5);
        }

        .recommend-more-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .no-songs {
            color: #6b7280;
            text-align: center;
            margin-top: 2.5rem;
            z-index: 10;
            position: relative;
        }

        .stButton > button {
            width: 100%;
            border: none;
        }

        @media (max-width: 768px) {
            .hero-title { font-size: 2.5rem; }
            .mood-grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
            .songs-grid { grid-template-columns: 1fr; }
            .header { padding: 1.5rem; }
            .mood-heading { font-size: 2rem; }
            .results-title { font-size: 2.25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def home_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-title">
                    Music for every<br><span class="hero-emotion">emotion.</span>
                </div>
                <div class="hero-subtitle">
                    Experience a personalized journey through sound tailored to your current mood and vibe.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🎵  Go to Recommendation Page", use_container_width=True, type="primary"):
            st.session_state.page = "recommend"
            st.rerun()


def recommend_page():
    st.markdown(
        """
        <div class="mood-section">
            <div class="mood-heading">
                How are you feeling? 🎧
            </div>
            <div class="mood-subtitle">
                Select a mood to start your personalized radio
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for i, (mood_name, mood_info) in enumerate(MOOD_MAP.items()):
        with cols[i]:
            gradient = MOOD_GRADIENTS[mood_name]
            card_html = f"""
            <div class="mood-card" style="background: {gradient};">
                <div class="mood-card-overlay"></div>
                <div class="mood-card-content">
                    <div class="mood-icon">{mood_info["emoji"]}</div>
                    <div class="mood-name">{mood_name}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(mood_name, key=f"mood_{mood_name}", use_container_width=True):
                st.session_state.mood = mood_name
                st.session_state.page = "results"
                st.session_state.songs = []
                st.rerun()


def results_page():
    mood_name = st.session_state.mood
    mood_info = MOOD_MAP[mood_name]
    colors = MOOD_COLORS[mood_name]
    quote = MOOD_QUOTES[mood_name]
    gradient = MOOD_GRADIENTS[mood_name]

    back_clicked = st.button("← Back to Dashboard", key="back_btn")
    if back_clicked:
        st.session_state.page = "recommend"
        st.session_state.songs = []
        st.rerun()

    aura_color = colors[0]
    title_gradient = gradient

    st.markdown(
        f"""
        <div class="results-header">
            <div class="results-aura" style="background: {aura_color}; opacity: 0.2;"></div>
            <h1 class="results-title" style="background-image: {title_gradient};">
                {mood_name} Vibes
            </h1>
            <p class="results-quote" style="color: {colors[0]};">
                {quote}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.songs:
        placeholder = st.empty()
        with placeholder.container():
            bar_delays = [f"animation-delay: {i * 0.1}s" for i in range(5)]
            bars_html = "".join(
                f'<div class="loader-bar" style="height: 2.5rem; background: {colors[0]}; {bar_delays[i]};"></div>'
                for i in range(5)
            )
            st.markdown(
                f"""
                <div class="loader-container">
                    <div class="loader-bars">{bars_html}</div>
                    <div class="loader-text">Syncing your {mood_name.lower()} energy...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(1.5)

        songs_data = get_songs(mood_info["id"])
        st.session_state.songs = songs_data
        placeholder.empty()
        st.rerun()
    else:
        display_songs(mood_name, gradient, colors[0])


def display_songs(mood_name, gradient, accent_color):
    songs = st.session_state.songs

    if songs:
        cols = st.columns(3)
        for i, song in enumerate(songs):
            with cols[i % 3]:
                embed_url = get_spotify_embed_url(song.get("uri"))
                if embed_url:
                    card_html = f"""
                    <div class="song-card">
                        <div class="song-card-gradient" style="background: {gradient};"></div>
                        <div class="song-card-content">
                            <iframe src="{embed_url}" width="100%" height="152" frameborder="0" 
                                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                                loading="lazy">
                            </iframe>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.caption("No Spotify preview available")

        more_disabled = st.session_state.get("loading_more", False)
        if st.button(
            "🔄  Recommend More Songs" if not more_disabled else "⏳  Fetching more...",
            key="recommend_more",
            use_container_width=True,
            disabled=more_disabled,
        ):
            st.session_state.loading_more = True
            new_songs = get_songs(MOOD_MAP[mood_name]["id"])
            st.session_state.songs.extend(new_songs)
            st.session_state.loading_more = False
            st.rerun()
    else:
        st.markdown(
            f'<p class="no-songs">No songs found for {mood_name.lower()} mood 😕</p>',
            unsafe_allow_html=True,
        )


def main():
    inject_css()

    if st.session_state.page == "results":
        st.markdown(
            f"""
            <div class="results-container">
                <div class="results-gradient" style="background: {MOOD_GRADIENTS.get(st.session_state.mood, 'linear-gradient(135deg, #0a0a0a, #0a0a0a)')};"></div>
            """,
            unsafe_allow_html=True,
        )
        results_page()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="header">
                <div class="header-content">
                    <div class="brand">Serenity<span class="brand-dot">.</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.page == "home":
            home_page()
        elif st.session_state.page == "recommend":
            recommend_page()

        st.markdown(
            """
            <div class="footer">
                <div class="footer-brand">Serenity</div>
                <div class="footer-text">Tailoring your sonic experience since 2024</div>
                <div class="footer-links">
                    <span>Made with ❤️</span>
                    <span>•</span>
                    <a href="https://github.com/MrityunjayRoy/serenity">Github</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
