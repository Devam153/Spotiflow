import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings

class SpotifyHandler:
    def __init__(self):
        # Use a comprehensive scope that includes all required permissions        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPE,
            cache_path=None  # Don't cache tokens to prevent stale credentials
        ))

    def search_for_songs(self, songs_dict):
        """Search for songs and their artists on Spotify"""
        track_ids = []
        for song, artist in songs_dict.items():
            if artist:  # If we have both song and artist
                results = self.sp.search(f'track:{song} artist:{artist}', type='track', limit=1)
            else:  # If we only have song title
                results = self.sp.search(f'track:{song}', type='track', limit=1)
            
            tracks = results['tracks']
            if tracks['total'] > 0:
                track_id = tracks['items'][0]['id']
                track_ids.append(track_id)
                print(f'{song} by {artist} found on Spotify.')
            else:
                print(f'{song} by {artist} NOT found on Spotify.')
        
        return track_ids

    def like_songs(self, track_ids):
        """Like songs in the user's Spotify account"""
        try:
            self.sp.current_user_saved_tracks_add(track_ids)
            return True
        except Exception as e:
            print(f"Error liking songs: {str(e)}")
            return False

    def get_user_playlists(self):
        """Get only playlists created by the current user"""
        try:
            # Get current user's ID
            user_id = self.sp.me()['id']
            
            # Get all playlists
            all_playlists = self.sp.current_user_playlists()
            
            # Filter to only include playlists owned by the current user
            if all_playlists and 'items' in all_playlists:
                all_playlists['items'] = [
                    playlist for playlist in all_playlists['items'] 
                    if playlist['owner']['id'] == user_id
                ]
            
            return all_playlists
        except Exception as e:
            print(f"Error getting playlists: {str(e)}")
            return None

    def add_to_playlist(self, playlist_id, track_ids):
        """Add tracks to an existing playlist"""
        try:
            self.sp.playlist_add_items(playlist_id, track_ids)
            return True
        except Exception as e:
            print(f"Error adding tracks to playlist: {str(e)}")
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
            print(f"Error creating playlist: {str(e)}")
            return None
