print(">>> RUNNING CLEAN FINAL APP.PY <<<")

"""
Spotify Artist Analytics Flask API

A Flask web application that provides analytics for any artist using
the Spotify Web API, including artist info, top tracks, latest album,
popular artists, random trending artists, and related artists.
"""

import os
import random
from typing import Dict, List, Any
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from spotify_client import SpotifyClient

load_dotenv()

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------
# Extract popular artists from new releases
# ---------------------------------------------------------
def extract_popular_artists_from_releases(
    new_releases: List[Dict[str, Any]], exclude_name: str = "", limit: int = 10
) -> List[Dict[str, str]]:
    popular = []
    seen = set()

    for album in new_releases:
        for a in album.get("artists", []):
            name = a["name"]
            if name != exclude_name and name not in seen:
                popular.append({"name": name, "id": a["id"]})
                seen.add(name)
                if len(popular) >= limit:
                    return popular

    return popular


# ---------------------------------------------------------
# Main Page (with optional pre-filled credentials)
# ---------------------------------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        default_client_id=os.getenv("SPOTIFY_CLIENT_ID", ""),
        default_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", "")
    )


# ---------------------------------------------------------
# Main Analytics Endpoint
# ---------------------------------------------------------
@app.route("/api/analytics", methods=["POST"])
def get_analytics():
    data = request.json

    artist_name = data.get("artist_name")
    if not artist_name:
        return jsonify({"error": "Artist name is required"}), 400

    # Credentials: user input > env
    client_id = data.get("client_id") or os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = data.get("client_secret") or os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return jsonify({"error": "Missing Spotify API credentials"}), 400

    try:
        # Authenticate
        client = SpotifyClient(client_id, client_secret)
        if not client.authenticate():
            return jsonify({"error": "Invalid Spotify credentials"}), 401

        # -------------------------
        # Artist Info
        # -------------------------
        artist = client.search_artist(artist_name)
        if not artist:
            return jsonify({"error": f'Artist "{artist_name}" not found'}), 404

        # -------------------------
        # Top Tracks (no audio stats since Spotify removed features API)
        # -------------------------
        top_tracks = client.get_artist_top_tracks(artist.id)
        top_tracks_list = [
            {
                "name": t.name,
                "duration": t.duration_formatted
            }
            for t in top_tracks[:5]
        ]

        # -------------------------
        # Latest Album
        # -------------------------
        albums = client.get_artist_albums(artist.id, limit=1)
        if not albums:
            return jsonify({"error": "This artist has no albums"}), 404

        latest_album = albums[0]
        album_tracks = client.get_album_tracks(latest_album.id, limit=5)

        # -------------------------
        # Popular Artists (based on New Releases)
        # -------------------------
        new_releases = client.get_new_releases(limit=20)
        popular_artists = extract_popular_artists_from_releases(
            new_releases, exclude_name=artist.name
        )

        # -------------------------
        # Random Trending Artist
        # -------------------------
        random_artist = None
        if popular_artists:
            choice = random.choice(popular_artists)
            rand = client.get_artist(choice["id"])
            if rand:
                rand_top = client.get_artist_top_tracks(rand.id)
                random_artist = {
                    "name": rand.name,
                    "followers": rand.followers,
                    "popularity": rand.popularity,
                    "image": rand.image_url,
                    "top_tracks": [t.name for t in rand_top[:3]]
                }

        # -------------------------
        # Final JSON
        # -------------------------
        return jsonify({
            "artist": {
                "name": artist.name,
                "followers": artist.followers,
                "popularity": artist.popularity,
                "image": artist.image_url,
                "genres": artist.genres or []
            },
            "top_tracks": top_tracks_list,
            "latest_album": {
                "name": latest_album.name,
                "release_date": latest_album.release_date,
                "image": latest_album.image_url,
                "tracks": [
                    {"name": t.name, "duration": t.duration_formatted}
                    for t in album_tracks
                ]
            },
            "popular_artists": [p["name"] for p in popular_artists],
            "random_artist": random_artist,
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ---------------------------------------------------------
# Run Server
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
