import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyOAuth

st.set_page_config(page_title="Soundalike", page_icon="🎵", layout="centered")

# css
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0a;
    color: #ffffff;
}

.header {
    text-align: center;
    padding: 2rem 0 1rem;
}

.header h1 {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -2px;
    color: #ffffff;
    margin: 0;
}

.header p {
    color: #888;
    font-size: 1rem;
    margin-top: 6px;
}

.artist-card {
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 12px;
    background: #1a1a1a;
    display: flex;
    align-items: center;
    height: 90px;
}

.artist-image {
    width: 90px;
    height: 90px;
    object-fit: cover;
    flex-shrink: 0;
}

.artist-image-placeholder {
    width: 90px;
    height: 90px;
    background: #7F77DD;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    flex-shrink: 0;
}

.artist-info {
    flex: 1;
    padding: 0 16px;
}

.artist-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}

.score-bar-wrap {
    background: #333;
    border-radius: 6px;
    height: 4px;
    width: 100%;
}

.score-bar {
    background: #7F77DD;
    border-radius: 6px;
    height: 4px;
}

.artist-rank {
    font-size: 2rem;
    font-weight: 900;
    color: #333;
    padding: 0 20px 0 16px;
    min-width: 60px;
    text-align: right;
}

.match-pill {
    display: inline-block;
    background: #1a1a2e;
    border: 1px solid #7F77DD;
    color: #AFA9EC;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.8rem;
    margin: 4px 4px 4px 0;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 2rem 0 1rem;
}

.divider {
    border: none;
    border-top: 1px solid #222;
    margin: 1.5rem 0;
}

.login-box {
    text-align: center;
    padding: 3rem 0;
}

.login-box p {
    color: #888;
    margin-bottom: 2rem;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

# spotify auth
def get_spotify_oauth():
    return SpotifyOAuth(
        client_id="7305b01715294b76a94c1f86b3f8460c",
        client_secret="0eddc25b8e0f4521a8532292c42ce60e",
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

# header
st.markdown("""
<div class="header">
    <h1>🎵 Soundalike</h1>
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

    # fetch user info
    user_info = sp.current_user()
    username = user_info["display_name"] or "You"

    st.markdown(f'<div class="section-title">Welcome, {username} 👋</div>', unsafe_allow_html=True)

    # fetch top artists
    with st.spinner("Fetching your top artists..."):
        results = sp.current_user_top_artists(limit=20, time_range="medium_term")
        user_artists = {}

        if not results["items"]:
    # medium_term has no data, try short_term
            results = sp.current_user_top_artists(limit=20, time_range="short_term")

        if not results["items"]:
    # try long_term as last resort
            results = sp.current_user_top_artists(limit=20, time_range="long_term")

        for i, artist in enumerate(results["items"]):
            name = artist.get("name", "Unknown")
            user_artists[name] = 20 - i

    
    # show their top artists
    st.markdown('<div class="section-title">Your top artists</div>', unsafe_allow_html=True)
    top_names = list(user_artists.keys())[:5]
    pills_html = "".join([f'<span class="match-pill">🎵 {a}</span>' for a in top_names])
    st.markdown(pills_html, unsafe_allow_html=True)

    # add to matrix and get recommendations
    base_df = load_base_matrix()
    new_row = pd.Series(user_artists, name=username)
    new_row = pd.Series(user_artists, name=username)
    
    
    df = pd.concat([base_df, new_row.to_frame().T]).fillna(0)

    similarity = cosine_similarity(df)
    similarity_df = pd.DataFrame(similarity, index=df.index, columns=df.index)

    if st.button("Get Recommendations →", type="primary", use_container_width=True):
        recs = get_recommendations(username, df, similarity_df)
        max_score = recs[0][1] if recs and recs[0][1] > 0 else 1
    
        similar_users = similarity_df[username].drop(username).nlargest(3)
        st.markdown('<div class="section-title">Taste matches</div>', unsafe_allow_html=True)
        pills_html = "".join([f'<span class="match-pill">👤 {u} — {score:.0%}</span>' for u, score in similar_users.items()])
        st.markdown(pills_html, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Recommended for you</div>', unsafe_allow_html=True)
        for i, (artist, score) in enumerate(recs, start=1):
            pct = int((score / max_score) * 100)
            st.markdown(f"""
            <div class="artist-card">
                <div class="artist-image-placeholder">🎵</div>
                <div class="artist-info">
                    <div class="artist-name">{artist}</div>
                    <div class="score-bar-wrap">
                        <div class="score-bar" style="width:{pct}%"></div>
                    </div>
                </div>
                <div class="artist-rank">{i}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True):
        st.session_state.token_info = None
        st.rerun()

# logged out flow
else:
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    st.markdown(f"""
    <div class="login-box">
        <p>Connect your Spotify account to get personalised artist recommendations</p>
        <a href="{auth_url}" target="_self">
            <button style="background:#1DB954; color:white; border:none; padding:14px 32px; 
            border-radius:30px; font-size:1rem; font-weight:700; cursor:pointer; letter-spacing:0.5px;">
                Login with Spotify
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
