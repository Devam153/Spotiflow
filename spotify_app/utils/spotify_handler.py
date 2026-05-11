import time
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from django.conf import settings

logger = logging.getLogger(__name__)


def build_oauth():
    """Build a SpotifyOAuth that never touches disk.

    MemoryCacheHandler keeps the token only on this instance, so the cache
    cannot leak between users. We persist tokens ourselves via the Django
    session — this object is only used for URL generation, code exchange,
    and refresh.
    """
    return SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        open_browser=False,
        cache_handler=MemoryCacheHandler(),
        show_dialog=True,
    )


class SpotifyHandler:
    """Per-user Spotify Web API wrapper.

    The handler is built from a token_info dict that lives in the user's
    Django session. The handler itself does not own token storage; callers
    pass the token in and (via from_session) write refreshed tokens back.
    """

    def __init__(self, token_info):
        if not token_info or 'access_token' not in token_info:
            raise ValueError("token_info with access_token required")
        self.token_info = token_info
        self.sp = spotipy.Spotify(auth=token_info['access_token'])

    @staticmethod
    def is_token_expired(token_info):
        # Refresh 60s before actual expiry to avoid mid-request 401s.
        return token_info.get('expires_at', 0) - int(time.time()) < 60

    @classmethod
    def from_session(cls, request):
        """Build a handler from request.session, refreshing if needed.

        Returns None if the user has no stored token (i.e. not authenticated)
        or if refresh fails.
        """
        token_info = request.session.get('spotify_token_info')
        if not token_info:
            return None

        if cls.is_token_expired(token_info):
            try:
                token_info = build_oauth().refresh_access_token(
                    token_info['refresh_token']
                )
                request.session['spotify_token_info'] = token_info
                logger.info("Refreshed expired Spotify access token")
            except Exception as e:
                logger.error(f"Error refreshing Spotify token: {e}")
                return None

        return cls(token_info)

    def get_user_profile(self):
        try:
            return self.sp.me()
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    def search_for_songs(self, songs_dict):
        track_ids = []
        for song, artist in songs_dict.items():
            try:
                if artist:
                    results = self.sp.search(
                        f'track:{song} artist:{artist}', type='track', limit=1
                    )
                else:
                    results = self.sp.search(
                        f'track:{song}', type='track', limit=1
                    )

                tracks = results['tracks']
                if tracks['total'] > 0:
                    track_ids.append(tracks['items'][0]['id'])
                    logger.info(f'{song} by {artist} found on Spotify.')
                else:
                    logger.info(f'{song} by {artist} NOT found on Spotify.')
            except Exception as e:
                logger.error(f"Error searching for song {song}: {e}")
        return track_ids

    def like_songs(self, track_ids):
        try:
            self.sp.current_user_saved_tracks_add(track_ids)
            return True
        except Exception as e:
            logger.error(f"Error liking songs: {e}")
            return False

    def get_user_playlists(self):
        try:
            user_id = self.sp.me()['id']
            all_playlists = self.sp.current_user_playlists()
            if all_playlists and 'items' in all_playlists:
                all_playlists['items'] = [
                    p for p in all_playlists['items']
                    if p['owner']['id'] == user_id
                ]
            return all_playlists
        except Exception as e:
            logger.error(f"Error getting playlists: {e}")
            return {"items": []}

    def add_to_playlist(self, playlist_id, track_ids):
        try:
            self.sp.playlist_add_items(playlist_id, track_ids)
            return True
        except Exception as e:
            logger.error(f"Error adding tracks to playlist: {e}")
            return False

    def create_playlist(self, name, description, track_ids):
        try:
            user_id = self.sp.me()['id']
            new_playlist = self.sp.user_playlist_create(
                user=user_id, name=name, public=True, description=description
            )
            if track_ids:
                self.sp.playlist_add_items(new_playlist['id'], track_ids)
            return new_playlist
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return None
