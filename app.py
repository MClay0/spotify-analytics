"""
Mt. Joy Spotify Analytics Flask API

A Flask web application that provides a REST API for retrieving
Mt. Joy analytics and information about popular artists.
"""

import os
import random
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from spotify_client import SpotifyClient

load_dotenv()

app = Flask(__name__)
CORS(app)


def extract_popular_artists_from_releases(new_releases: List[Dict[str, Any]], exclude_name: str = 'Mt. Joy', limit: int = 10) -> List[Dict[str, str]]:
    """
    Extract unique popular artists from new releases.

    Args:
        new_releases: List of album data from Spotify's new releases
        exclude_name: Artist name to exclude from results
        limit: Maximum number of artists to return

    Returns:
        List of dictionaries containing artist name and ID
    """
    popular_artists = []
    seen_names = set()

    for album in new_releases:
        for artist_item in album.get('artists', []):
            artist_name = artist_item['name']
            if artist_name != exclude_name and artist_name not in seen_names:
                popular_artists.append({'name': artist_name, 'id': artist_item['id']})
                seen_names.add(artist_name)
                if len(popular_artists) >= limit:
                    return popular_artists

    return popular_artists


@app.route('/')
def index() -> str:
    """Render the main HTML page."""
    return render_template('index.html')


@app.route('/api/analytics', methods=['POST'])
def get_analytics() -> tuple:
    """
    API endpoint to retrieve Mt. Joy analytics and popular artists.

    Expects JSON payload with optional client_id and client_secret.
    Falls back to environment variables if not provided.

    Returns:
        JSON response with analytics data or error message
    """
    data = request.json
    client_id = data.get('client_id') or os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = data.get('client_secret') or os.getenv('SPOTIFY_CLIENT_SECRET')

    # Validate credentials are provided
    if not client_id or not client_secret:
        return jsonify({'error': 'Missing credentials'}), 400

    try:
        # Initialize and authenticate Spotify client
        client = SpotifyClient(client_id, client_secret)
        if not client.authenticate():
            return jsonify({'error': 'Invalid credentials'}), 401

        # Get Mt. Joy artist information
        mt_joy = client.search_artist("Mt Joy")
        if not mt_joy:
            return jsonify({'error': 'Could not find Mt. Joy'}), 404

        # Get Mt. Joy top tracks
        top_tracks = client.get_artist_top_tracks(mt_joy.id)

        # Get latest album
        albums = client.get_artist_albums(mt_joy.id)
        if not albums:
            return jsonify({'error': 'Could not find albums'}), 404

        latest_album = albums[0]
        album_tracks = client.get_album_tracks(latest_album.id, limit=5)

        # Get popular artists from new releases
        new_releases = client.get_new_releases(limit=20)
        popular_artists = extract_popular_artists_from_releases(new_releases, exclude_name='Mt. Joy', limit=10)

        # Select and get details for a random artist
        random_artist_details: Optional[Dict[str, Any]] = None
        if popular_artists:
            random_artist_data = random.choice(popular_artists)
            random_artist = client.get_artist(random_artist_data['id'])

            if random_artist:
                random_top_tracks = client.get_artist_top_tracks(random_artist.id)
                random_artist_details = {
                    'name': random_artist.name,
                    'followers': random_artist.followers,
                    'popularity': random_artist.popularity,
                    'top_tracks': [track.name for track in random_top_tracks[:3]],
                    'image': random_artist.image_url
                }

        # Build response JSON
        return jsonify({
            'mt_joy': {
                'name': mt_joy.name,
                'followers': mt_joy.followers,
                'popularity': mt_joy.popularity,
                'top_tracks': [track.name for track in top_tracks[:5]],
                'image': mt_joy.image_url
            },
            'latest_album': {
                'name': latest_album.name,
                'release_date': latest_album.release_date,
                'image': latest_album.image_url,
                'tracks': [
                    {
                        'name': track.name,
                        'duration': track.duration_formatted
                    }
                    for track in album_tracks
                ]
            },
            'popular_artists': [artist['name'] for artist in popular_artists],
            'random_artist': random_artist_details
        })

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
