import os
import base64
import random
import requests
from dotenv import load_dotenv

load_dotenv()

def setup_spotify_credentials():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if client_id and client_secret:
        return client_id, client_secret
    
    client_id = input("Enter your Spotify Client ID: ").strip()
    client_secret = input("Enter your Spotify Client Secret: ").strip()
    return client_id, client_secret
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
    return response.json()["access_token"]

def make_spotify_request(endpoint, access_token):
    url = f"https://api.spotify.com/v1{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else {}

def main():
    client_id, client_secret = setup_spotify_credentials()
    access_token = get_access_token(client_id, client_secret)
    
    print("MT. JOY ANALYTICS")
    print("=" * 40)

    # 1. Get Mt. Joy stats
    print("\n1. Mt. Joy Stats:")
    search_results = make_spotify_request("/search?q=Mt%20Joy&type=artist&limit=1", access_token)
    artist = search_results['artists']['items'][0]
    mt_joy_id = artist['id']
    
    print(f"   {artist['name']}")
    print(f"   Followers: {artist['followers']['total']:,}")
    print(f"   Popularity: {artist['popularity']}/100")
    
    # Top tracks
    top_tracks = make_spotify_request(f"/artists/{mt_joy_id}/top-tracks?market=US", access_token)
    print(f"\n   Top Tracks:")
    for i, track in enumerate(top_tracks['tracks'][:5], 1):
        print(f"     {i}. {track['name']}")

    # 2. Latest album
    print(f"\n2. Latest Album:")
    albums = make_spotify_request(f"/artists/{mt_joy_id}/albums?include_groups=album&market=US&limit=1", access_token)
    latest_album = albums['items'][0]
    print(f"   {latest_album['name']} ({latest_album.get('release_date', 'Unknown')})")
    
    # Album tracks
    album_tracks = make_spotify_request(f"/albums/{latest_album['id']}/tracks?limit=5", access_token)
    for i, track in enumerate(album_tracks['items'], 1):
        duration_min = track['duration_ms'] // 60000
        duration_sec = (track['duration_ms'] % 60000) // 1000
        print(f"     {i}. {track['name']} ({duration_min}:{duration_sec:02d})")

    # 3. Get popular artists from new releases
    print(f"\n3. Finding Popular Artists:")
    new_releases = make_spotify_request("/browse/new-releases?limit=20", access_token)
    popular_artists = []
    
    if 'albums' in new_releases:
        for album in new_releases['albums']['items']:
            for artist in album['artists']:
                if artist['name'] != 'Mt. Joy' and artist['name'] not in [a['name'] for a in popular_artists]:
                    popular_artists.append({'name': artist['name'], 'id': artist['id']})
                if len(popular_artists) >= 10:
                    break
            if len(popular_artists) >= 10:
                break

    for i, artist in enumerate(popular_artists, 1):
        print(f"     {i}. {artist['name']}")

    # 4. Random artist info
    print(f"\n4. Random Artist Details:")
    random_artist = random.choice(popular_artists)
    print(f"  {random_artist['name']}")
    
    artist_info = make_spotify_request(f"/artists/{random_artist['id']}", access_token)
    print(f"   Followers: {artist_info['followers']['total']:,}")
    print(f"   Popularity: {artist_info['popularity']}/100")
    
    top_tracks = make_spotify_request(f"/artists/{random_artist['id']}/top-tracks?market=US", access_token)
    print(f"   Top tracks:")
    for i, track in enumerate(top_tracks['tracks'][:3], 1):
        print(f"     {i}. {track['name']}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()