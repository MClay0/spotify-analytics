import os
import base64
import random
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_access_token(client_id, client_secret):
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def make_spotify_request(endpoint, access_token):
    url = f"https://api.spotify.com/v1{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analytics', methods=['POST'])
def get_analytics():
    data = request.json
    client_id = data.get('client_id') or os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = data.get('client_secret') or os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or not client_secret:
        return jsonify({'error': 'Missing credentials'}), 400

    try:
        access_token = get_access_token(client_id, client_secret)
        if not access_token:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Get Mt. Joy stats
        search_results = make_spotify_request("/search?q=Mt%20Joy&type=artist&limit=1", access_token)
        artist = search_results['artists']['items'][0]
        mt_joy_id = artist['id']

        # Top tracks
        top_tracks = make_spotify_request(f"/artists/{mt_joy_id}/top-tracks?market=US", access_token)

        # Latest album
        albums = make_spotify_request(f"/artists/{mt_joy_id}/albums?include_groups=album&market=US&limit=1", access_token)
        latest_album = albums['items'][0]

        # Album tracks
        album_tracks = make_spotify_request(f"/albums/{latest_album['id']}/tracks?limit=5", access_token)

        # Get popular artists from new releases
        new_releases = make_spotify_request("/browse/new-releases?limit=20", access_token)
        popular_artists = []

        if 'albums' in new_releases:
            for album in new_releases['albums']['items']:
                for artist_item in album['artists']:
                    if artist_item['name'] != 'Mt. Joy' and artist_item['name'] not in [a['name'] for a in popular_artists]:
                        popular_artists.append({'name': artist_item['name'], 'id': artist_item['id']})
                    if len(popular_artists) >= 10:
                        break
                if len(popular_artists) >= 10:
                    break

        # Random artist info
        random_artist = random.choice(popular_artists) if popular_artists else None
        random_artist_details = None

        if random_artist:
            artist_info = make_spotify_request(f"/artists/{random_artist['id']}", access_token)
            random_top_tracks = make_spotify_request(f"/artists/{random_artist['id']}/top-tracks?market=US", access_token)
            random_artist_details = {
                'name': artist_info['name'],
                'followers': artist_info['followers']['total'],
                'popularity': artist_info['popularity'],
                'top_tracks': [track['name'] for track in random_top_tracks['tracks'][:3]],
                'image': artist_info['images'][0]['url'] if artist_info.get('images') else None
            }

        return jsonify({
            'mt_joy': {
                'name': artist['name'],
                'followers': artist['followers']['total'],
                'popularity': artist['popularity'],
                'top_tracks': [track['name'] for track in top_tracks['tracks'][:5]],
                'image': artist['images'][0]['url'] if artist.get('images') else None
            },
            'latest_album': {
                'name': latest_album['name'],
                'release_date': latest_album.get('release_date', 'Unknown'),
                'image': latest_album['images'][0]['url'] if latest_album.get('images') else None,
                'tracks': [
                    {
                        'name': track['name'],
                        'duration': f"{track['duration_ms'] // 60000}:{(track['duration_ms'] % 60000) // 1000:02d}"
                    }
                    for track in album_tracks['items']
                ]
            },
            'popular_artists': [artist['name'] for artist in popular_artists],
            'random_artist': random_artist_details
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
