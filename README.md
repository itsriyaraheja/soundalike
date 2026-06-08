# 🎵 Soundalike

> Discover artists that match your taste — powered by Spotify data and collaborative filtering.

**[Live Demo →](https://soundalike.streamlit.app)**

---

## What it does

Soundalike connects to your Spotify account, fetches your top artists, and recommends new artists you haven't heard yet — based on the listening patterns of users with similar taste.

The more people use it, the smarter it gets.

---

## How it works

Soundalike uses **user-based collaborative filtering**:

1. **Fetch** — pulls your top 20 artists from Spotify via OAuth
2. **Matrix** — adds you to a user-artist interaction matrix (rows = users, cols = artists, values = listening rank)
3. **Similarity** — computes cosine similarity between your listening profile and all other users
4. **Recommend** — finds artists loved by your taste-twins that you haven't heard yet
5. **Score** — ranks them by weighted similarity score

```
Your Spotify data → User-Artist Matrix → Cosine Similarity → Recommendations
```

---

## Tech stack

| Tool | Purpose |
|---|---|
| Spotipy | Spotify OAuth + fetching artist data |
| Pandas | Building and updating the user-artist matrix |
| Scikit-learn | Cosine similarity computation |
| Streamlit | Frontend UI |
| Streamlit Cloud | Free deployment |
| GitHub | Version control |

---

## Run it locally

**1. Clone the repo**
```bash
git clone https://github.com/itsriyaraheja/soundalike.git
cd soundalike
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up Spotify credentials**

Create a Spotify app at [developer.spotify.com](https://developer.spotify.com) and add `http://127.0.0.1:8501/callback` as a redirect URI.

Then add your credentials to `app.py`:
```python
client_id="7305b01715294b76a94c1f86b3f8460c"
client_secret="7305b01715294b76a94c1f86b3f8460c"
```

**4. Run the app**
```bash
streamlit run app.py
```

---

## Project structure

```
soundalike/
├── app.py                    # main Streamlit app
├── data/
│   └── user_artist_matrix.csv  # user-artist interaction matrix
├── notebooks/
│   └── 01_explore.ipynb      # data exploration + algorithm dev
├── requirements.txt
└── README.md
```

---

## Algorithm deep dive

The core of Soundalike is **cosine similarity** between user vectors:

```
sim(u, v) = (u · v) / (‖u‖ × ‖v‖)
```

For each unheard artist, a weighted score is computed across the top-K most similar users:

```
score(artist) = Σ sim(u, neighbor) × play_count(neighbor, artist)
```

Artists are then ranked by score and filtered to remove ones the user already knows.

---

Built by [Riya Raheja](https://github.com/itsriyaraheja)