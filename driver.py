"""
Mt. Joy Spotify Analytics CLI

A command-line tool to display analytics and information about Mt. Joy
and other popular artists using the Spotify Web API.
"""

import os
import random
from typing import Tuple, List, Dict
from dotenv import load_dotenv
from spotify_client import SpotifyClient, Artist

load_dotenv()


def setup_spotify_credentials() -> Tuple[str, str]:
    """
    Get Spotify API credentials from environment or user input.

    Returns:
        Tuple containing (client_id, client_secret)
    """
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if client_id and client_secret:
        return client_id, client_secret

    client_id = input("Enter your Spotify Client ID: ").strip()
    client_secret = input("Enter your Spotify Client Secret: ").strip()
    return client_id, client_secret


def extract_popular_artists(new_releases: List[Dict], exclude_name: str = 'Mt. Joy', limit: int = 10) -> List[Dict[str, str]]:
    """
    Extract unique popular artists from new releases.

    Args:
        new_releases: List of album data from Spotify's new releases
        exclude_name: Artist name to exclude from results (default: 'Mt. Joy')
        limit: Maximum number of artists to return

    Returns:
        List of dictionaries containing artist name and ID
    """
    popular_artists = []
    seen_names = set()

    for album in new_releases:
        for artist in album.get('artists', []):
            artist_name = artist['name']
            if artist_name != exclude_name and artist_name not in seen_names:
                popular_artists.append({'name': artist_name, 'id': artist['id']})
                seen_names.add(artist_name)
                if len(popular_artists) >= limit:
                    return popular_artists

    return popular_artists


def main() -> None:
    """Main entry point for the Mt. Joy analytics CLI."""
    # Initialize Spotify client
    client_id, client_secret = setup_spotify_credentials()
    client = SpotifyClient(client_id, client_secret)

    # Authenticate with Spotify API
    if not client.authenticate():
        print("Error: Failed to authenticate with Spotify API")
        return

    print("MT. JOY ANALYTICS")
    print("=" * 40)

    # 1. Get Mt. Joy stats
    print("\n1. Mt. Joy Stats:")
    mt_joy = client.search_artist("Mt Joy")

    if not mt_joy:
        print("Error: Could not find Mt. Joy")
        return

    print(f"   {mt_joy.name}")
    print(f"   Followers: {mt_joy.followers:,}")
    print(f"   Popularity: {mt_joy.popularity}/100")

    # Display top tracks
    top_tracks = client.get_artist_top_tracks(mt_joy.id)
    print(f"\n   Top Tracks:")
    for i, track in enumerate(top_tracks[:5], 1):
        print(f"     {i}. {track.name}")

    # 2. Latest album
    print(f"\n2. Latest Album:")
    albums = client.get_artist_albums(mt_joy.id)

    if albums:
        latest_album = albums[0]
        print(f"   {latest_album.name} ({latest_album.release_date})")

        # Display album tracks
        album_tracks = client.get_album_tracks(latest_album.id, limit=5)
        for i, track in enumerate(album_tracks, 1):
            print(f"     {i}. {track.name} ({track.duration_formatted})")

    # 3. Get popular artists from new releases
    print(f"\n3. Finding Popular Artists:")
    new_releases = client.get_new_releases(limit=20)
    popular_artists = extract_popular_artists(new_releases, exclude_name='Mt. Joy', limit=10)

    for i, artist in enumerate(popular_artists, 1):
        print(f"     {i}. {artist['name']}")

    # 4. Random artist info
    if popular_artists:
        print(f"\n4. Random Artist Details:")
        random_artist_data = random.choice(popular_artists)
        print(f"  {random_artist_data['name']}")

        # Fetch detailed artist information
        random_artist = client.get_artist(random_artist_data['id'])

        if random_artist:
            print(f"   Followers: {random_artist.followers:,}")
            print(f"   Popularity: {random_artist.popularity}/100")

            # Display top tracks for the random artist
            random_top_tracks = client.get_artist_top_tracks(random_artist_data['id'])
            print(f"   Top tracks:")
            for i, track in enumerate(random_top_tracks[:3], 1):
                print(f"     {i}. {track.name}")

    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()