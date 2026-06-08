
import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64

st.set_page_config(page_title="Soundalike", page_icon="🎵", layout="centered")

def load_font(font_path):
    with open(font_path, "rb") as f:
        font_data = base64.b64encode(f.read()).decode()
    return font_data

try:
    font_data = load_font("1 Punk.ttf")
    font_face = f"@font-face {{ font-family: 'Punk'; src: url('data:font/truetype;base64,{font_data}') format('truetype'); }}"
except:
    font_face = "@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');"
    font_face += " .punk { font-family: 'Bebas Neue', sans-serif; }"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

{font_face}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: #ffffff;
}}

.stApp {{
    background-image: url('https://i.ibb.co/LdjFNMRN/wow.jpg');
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
}}

.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(10, 4, 8, 0.82);
    z-index: 0;
}}

.stApp > * {{
    position: relative;
    z-index: 1;
}}

.header {{
    text-align: center;
    padding: 3rem 0 1rem;
}}

.header h1 {{
    font-family: 'Punk', sans-serif;
    font-size: 5rem;
    letter-spacing: 4px;
    color: #ffffff;
    margin: 0;
    line-height: 1;
}}

.header p {{
    color: rgba(255,255,255,0.5);
    font-size: 0.95rem;
    margin-top: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}

.artist-card {{
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(210, 50, 100, 0.2);
    display: flex;
    align-items: center;
    height: 80px;
}}

.artist-image-placeholder {{
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #C2185B, #880E4F);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    flex-shrink: 0;
}}

.artist-info {{
    flex: 1;
    padding: 0 16px;
}}

.artist-name {{
    font-family: 'Punk', sans-serif;
    font-size: 1.3rem;
    letter-spacing: 1.5px;
    color: #ffffff;
}}

.artist-rank {{
    font-family: 'Punk', sans-serif;
    font-size: 2rem;
    color: rgba(255,255,255,0.12);
    padding: 0 20px;
    min-width: 60px;
    text-align: right;
}}

.match-pill {{
    display: inline-block;
    background: rgba(194, 24, 91, 0.15);
    border: 1px solid rgba(194, 24, 91, 0.4);
    color: #F48FB1;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    margin: 4px 4px 4px 0;
}}

.section-title {{
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 2rem 0 0.75rem;
}}

.welcome-name {{
    font-family: 'Punk', sans-serif;
    font-size: 2.5rem;
    letter-spacing: 3px;
    color: #ffffff;
    margin: 0 0 1.5rem;
}}

.divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1.5rem 0;
}}

.login-box {{
    text-align: center;
    padding: 4rem 0;
}}

.login-box p {{
    color: rgba(255,255,255,0.5);
    margin-bottom: 2.5rem;
    font-size: 0.95rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

div.stButton > button {{
    background: linear-gradient(135deg, #C2185B, #880E4F) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Punk', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    padding: 0.6rem 1rem !important;
}}

div.stButton > button:hover {{
    background: linear-gradient(135deg, #D81B60, #AD1457) !important;
}}

div[data-testid="stSuccess"] {{
    background: rgba(194, 24, 91, 0.1) !important;
    border: 1px solid rgba(194, 24, 91, 0.3) !important;
    color: #F48FB1 !important;
    border-radius: 10px !important;
}}
</style>
""", unsafe_allow_html=True)


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id="7305b01715294b76a94c1f86b3f8460c",
        client_secret="7305b01715294b76a94c1f86b3f8460c",
        redirect_uri="http://127.0.0.1:8501/callback",
        scope="user-top-read",
        cache_path=None,
        show_dialog=True
    )


@st.cache_data
def load_base_matrix():
    df = pd.read_csv("data/user_artist_matrix.csv", index_col=0)
    return df


def get_recommendations(user, df, similarity_df, top_k=3, top_n=5):
    similar_users = similarity_df[user].drop(user).nlargest(top_k)
    already_listened = set(df.loc[user][df.loc[user] > 0].index)
    scores = {}
    for similar_user, sim_score in similar_users.items():
        for artist, play_count in df.loc[similar_user].items():
            if artist not in already_listened and play_count > 0:
                scores[artist] = scores.get(artist, 0) + sim_score * play_count
    recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return recommendations


@st.cache_data
def get_artist_image(artist_name, token):
    try:
        sp = spotipy.Spotify(auth=token)
        results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        items = results["artists"]["items"]
        if items and items[0]["name"].lower() == artist_name.lower() and items[0]["images"]:
            return items[0]["images"][0]["url"]
    except:
        pass
    return None


# header
st.markdown("""
<div class="header">
    <h1>SOUNDALIKE</h1>
    <p>Discover artists that match your taste</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# handle spotify callback
if "token_info" not in st.session_state:
    st.session_state.token_info = None

params = st.query_params
if "code" in params and st.session_state.token_info is None:
    try:
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.get_access_token(params["code"])
        st.session_state.token_info = token_info
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

# logged in flow
if st.session_state.token_info:
    sp = spotipy.Spotify(auth=st.session_state.token_info["access_token"])

    user_info = sp.current_user()
    username = user_info["display_name"] or "You"

    st.markdown('<div class="section-title">Welcome back</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-name">{username}</div>', unsafe_allow_html=True)

    with st.spinner("Fetching your top artists..."):
        results = sp.current_user_top_artists(limit=20, time_range="medium_term")

        if not results["items"]:
            results = sp.current_user_top_artists(limit=20, time_range="short_term")

        if not results["items"]:
            results = sp.current_user_top_artists(limit=20, time_range="long_term")

        user_artists = {}
        for i, artist in enumerate(results["items"]):
            name = artist.get("name", "Unknown")
            user_artists[name] = 20 - i

    st.markdown('<div class="section-title">Your top artists</div>', unsafe_allow_html=True)
    top_names = list(user_artists.keys())[:5]
    pills_html = "".join([f'<span class="match-pill">🎵 {a}</span>' for a in top_names])
    st.markdown(pills_html, unsafe_allow_html=True)

    base_df = load_base_matrix()

    if username in base_df.index:
        for artist, score in user_artists.items():
            base_df.loc[username, artist] = score
        df = base_df.fillna(0)
    else:
        new_row = pd.Series(user_artists, name=username)
        df = pd.concat([base_df, new_row.to_frame().T]).fillna(0)

    df.to_csv("data/user_artist_matrix.csv")
    load_base_matrix.clear()
    st.success("Your taste has been added to Soundalike 🎵")

    similarity = cosine_similarity(df)
    similarity_df = pd.DataFrame(similarity, index=df.index, columns=df.index)

    if st.button("GET RECOMMENDATIONS →", type="primary", use_container_width=True):
        recs = get_recommendations(username, df, similarity_df)
        max_score = recs[0][1] if recs and recs[0][1] > 0 else 1

        similar_users = similarity_df[username].drop(username).nlargest(3)
        st.markdown('<div class="section-title">Taste matches</div>', unsafe_allow_html=True)
        pills_html = "".join([f'<span class="match-pill">👤 {u} — {score:.0%}</span>' for u, score in similar_users.items()])
        st.markdown(pills_html, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Recommended for you</div>', unsafe_allow_html=True)
        for i, (artist, score) in enumerate(recs, start=1):
            image_url = get_artist_image(artist, st.session_state.token_info["access_token"])

            if image_url:
                image_html = f'<img src="{image_url}" alt="{artist}" style="width:80px;height:80px;object-fit:cover;flex-shrink:0;"/>'
            else:
                image_html = '<div class="artist-image-placeholder">🎵</div>'

            st.markdown(f"""
            <div class="artist-card">
                {image_html}
                <div class="artist-info">
                    <div class="artist-name">{artist}</div>
                </div>
                <div class="artist-rank">{i}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("LOGOUT", use_container_width=True):
        st.session_state.token_info = None
        st.rerun()

else:
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    st.markdown(f"""
    <div class="login-box">
        <p>Connect your Spotify account to get personalised artist recommendations</p>
        <a href="{auth_url}" target="_self">
            <button style="background:linear-gradient(135deg,#C2185B,#880E4F);color:white;border:none;
            padding:16px 48px;border-radius:10px;font-size:1.1rem;font-weight:600;cursor:pointer;
            font-family:'Inter',sans-serif;letter-spacing:1px;">
            Login with Spotify
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)