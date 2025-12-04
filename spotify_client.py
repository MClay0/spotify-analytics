"""
Spotify API Client Module

This module provides classes for interacting with the Spotify Web API,
including authentication, data retrieval, and data modeling.
"""

import base64
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class Artist:
    id: str
    name: str
    followers: int
    popularity: int
    image_url: Optional[str] = None
    genres: Optional[List[str]] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Artist':
        return cls(
            id=data['id'],
            name=data['name'],
            followers=data['followers']['total'],
            popularity=data['popularity'],
            image_url=data['images'][0]['url'] if data.get('images') else None,
            genres=data.get('genres', [])
        )


@dataclass
class Album:
    """
    Represents a Spotify album with its metadata.

    Attributes:
        id: Spotify album ID
        name: Album name
        release_date: Album release date
        image_url: URL to album cover art
    """
    id: str
    name: str
    release_date: str
    image_url: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Album':
        """
        Create an Album instance from Spotify API response data.

        Args:
            data: Raw JSON response from Spotify API

        Returns:
            Album instance populated with data from the API response
        """
        return cls(
            id=data['id'],
            name=data['name'],
            release_date=data.get('release_date', 'Unknown'),
            image_url=data['images'][0]['url'] if data.get('images') else None
        )


@dataclass
class Track:
    """
    Represents a Spotify track.

    Attributes:
        id: Spotify track ID
        name: Track name
        duration_ms: Track duration in milliseconds
    """
    id: str
    name: str
    duration_ms: int

    @property
    def duration_formatted(self) -> str:
        minutes = self.duration_ms // 60000
        seconds = (self.duration_ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Track':
        """
        Create a Track instance from Spotify API response data.

        Args:
            data: Raw JSON response from Spotify API

        Returns:
            Track instance populated with data from the API response
        """
        return cls(
            id=data['id'],
            name=data['name'],
            duration_ms=data['duration_ms']
        )


class SpotifyClient:
    """
    Client for interacting with the Spotify Web API.

    This class handles authentication and provides methods for
    retrieving artist, album, and track information from Spotify.

    Attributes:
        client_id: Spotify application client ID
        client_secret: Spotify application client secret
        access_token: OAuth access token (obtained after authentication)
    """

    BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the Spotify client with credentials.

        Args:
            client_id: Spotify application client ID
            client_secret: Spotify application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None

    def authenticate(self) -> bool:
        """
        Authenticate with Spotify API using client credentials flow.

        Returns:
            True if authentication successful, False otherwise
        """
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            return True
        except requests.RequestException:
            return False

    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        if not self.access_token:
            raise ValueError("Client not authenticated. Call authenticate() first.")

        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(url, headers=headers)
            return response.json() if response.status_code == 200 else {}
        except requests.RequestException:
            return {}

    def search_artist(self, artist_name: str) -> Optional[Artist]:
        # Search for artist
        endpoint = (
            f"/search?q={requests.utils.quote(artist_name)}"
            f"&type=artist&limit=5"
        )
        data = self._make_request(endpoint)

        items = data.get("artists", {}).get("items", [])
        if not items:
            return None

        # Strict name matching (case-insensitive)
        for item in items:
            if item["name"].lower() == artist_name.lower():
                return Artist.from_api_response(item)

        # Fallback: return best match (highest popularity)
        items.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        return Artist.from_api_response(items[0])
    

    def get_artist(self, artist_id: str) -> Optional[Artist]:
        """
        Get detailed artist information by ID.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Artist object if found, None otherwise
        """
        data = self._make_request(f"/artists/{artist_id}")
        return Artist.from_api_response(data) if data else None

    def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> List[Track]:
        """
        Get an artist's top tracks.

        Args:
            artist_id: Spotify artist ID
            market: ISO 3166-1 alpha-2 country code (default: "US")

        Returns:
            List of Track objects
        """
        data = self._make_request(f"/artists/{artist_id}/top-tracks?market={market}")
        tracks = data.get('tracks', [])
        return [Track.from_api_response(track) for track in tracks]
    
    def get_artist_albums(
        self,
        artist_id: str,
        include_groups: str = "album",
        market: str = "US",
        limit: int = 1
    ) -> List[Album]:
        """
        Get an artist's albums.

        Args:
            artist_id: Spotify artist ID
            include_groups: Comma-separated list of album types (album, single, compilation)
            market: ISO 3166-1 alpha-2 country code (default: "US")
            limit: Maximum number of albums to return

        Returns:
            List of Album objects
        """
        endpoint = f"/artists/{artist_id}/albums?include_groups={include_groups}&market={market}&limit={limit}"
        data = self._make_request(endpoint)
        albums = data.get('items', [])
        return [Album.from_api_response(album) for album in albums]

    def get_album_tracks(self, album_id: str, limit: int = 50) -> List[Track]:
        """
        Get tracks from an album.

        Args:
            album_id: Spotify album ID
            limit: Maximum number of tracks to return

        Returns:
            List of Track objects
        """
        data = self._make_request(f"/albums/{album_id}/tracks?limit={limit}")
        tracks = data.get('items', [])
        return [Track.from_api_response(track) for track in tracks]

    def get_new_releases(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get new album releases featured in Spotify.

        Args:
            limit: Maximum number of albums to return

        Returns:
            List of album dictionaries with artist information
        """
        data = self._make_request(f"/browse/new-releases?limit={limit}")
        return data.get('albums', {}).get('items', [])
        
        

