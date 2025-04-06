import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

class SpotifyHandler:
    def __init__(self):
        # Configure detailed logging
        logger.info(f"Initializing SpotifyHandler")
        logger.info(f"SPOTIFY_CLIENT_ID: {settings.SPOTIFY_CLIENT_ID}")
        logger.info(f"SPOTIFY_REDIRECT_URI: {settings.SPOTIFY_REDIRECT_URI}")
        logger.info(f"SPOTIFY_SCOPE: {settings.SPOTIFY_SCOPE}")
        
        try:
            # Initialize the Spotify client with the correct settings
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                scope=settings.SPOTIFY_SCOPE,
                open_browser=False,  # Prevent browser opening in server environment
                cache_path=None  # Don't cache tokens in production
            ))
            logger.info("SpotifyOAuth initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SpotifyOAuth: {str(e)}")
            raise

    def search_for_songs(self, songs_dict):
        """Search for songs and their artists on Spotify"""
        track_ids = []
        for song, artist in songs_dict.items():
            try:
                if artist:  # If we have both song and artist
                    results = self.sp.search(f'track:{song} artist:{artist}', type='track', limit=1)
                else:  # If we only have song title
                    results = self.sp.search(f'track:{song}', type='track', limit=1)
                
                tracks = results['tracks']
                if tracks['total'] > 0:
                    track_id = tracks['items'][0]['id']
                    track_ids.append(track_id)
                    logger.info(f'{song} by {artist} found on Spotify.')
                else:
                    logger.info(f'{song} by {artist} NOT found on Spotify.')
            except Exception as e:
                logger.error(f"Error searching for song {song}: {str(e)}")
        
        return track_ids

    def like_songs(self, track_ids):
        """Like songs in the user's Spotify account"""
        try:
            self.sp.current_user_saved_tracks_add(track_ids)
            return True
        except Exception as e:
            logger.error(f"Error liking songs: {str(e)}")
            return False

    def get_user_playlists(self):
        """Get only playlists created by the current user"""
        try:
            # Get current user's ID
            user_data = self.sp.me()
            user_id = user_data['id']
            logger.info(f"Retrieved user ID: {user_id}")
            
            # Get all playlists
            all_playlists = self.sp.current_user_playlists()
            logger.info(f"Retrieved {len(all_playlists.get('items', []))} playlists")
            
            # Filter to only include playlists owned by the current user
            if all_playlists and 'items' in all_playlists:
                all_playlists['items'] = [
                    playlist for playlist in all_playlists['items'] 
                    if playlist['owner']['id'] == user_id
                ]
                logger.info(f"Filtered to {len(all_playlists['items'])} user-owned playlists")
            
            return all_playlists
        except Exception as e:
            logger.error(f"Error getting playlists: {str(e)}")
            return {"items": []}

    def add_to_playlist(self, playlist_id, track_ids):
        """Add tracks to an existing playlist"""
        try:
            self.sp.playlist_add_items(playlist_id, track_ids)
            return True
        except Exception as e:
            logger.error(f"Error adding tracks to playlist: {str(e)}")
            return False

    def create_playlist(self, name, description, track_ids):
        """Create a new playlist and add tracks to it"""
        try:
            user_id = self.sp.me()['id']
            new_playlist = self.sp.user_playlist_create(
                user=user_id, 
                name=name, 
                public=True, 
                description=description
            )
            if track_ids:
                self.sp.playlist_add_items(new_playlist['id'], track_ids)
            return new_playlist
        except Exception as e:
            logger.error(f"Error creating playlist: {str(e)}")
            return None
