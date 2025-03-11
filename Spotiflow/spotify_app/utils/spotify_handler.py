import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings

class SpotifyHandler:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPE
        ))

    def get_user_playlists(self):
        return self.sp.current_user_playlists()

    def add_to_playlist(self, playlist_id, track_ids):
        return self.sp.playlist_add_items(playlist_id, track_ids)

    def create_playlist(self, name, description):
        user_id = self.sp.me()['id']
        return self.sp.user_playlist_create(
            user_id, 
            name, 
            public=True, 
            description=description
        )
