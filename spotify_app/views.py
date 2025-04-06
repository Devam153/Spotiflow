from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .utils.spotify_handler import SpotifyHandler
from .utils.ocr_handler import OCRHandler
import json
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Home page view"""
    return render(request, 'spotify_app/index.html')

def process_image(request):
    """Process uploaded image with OCR"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            ocr_handler = OCRHandler()
            songs = ocr_handler.process_image(image)
            
            # Store songs in session for later use
            request.session['songs'] = songs
            
            return JsonResponse({
                'success': True,
                'songs': songs
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({
        'success': False,
        'error': 'No image uploaded'
    })

def spotify_callback(request):
    """Handle Spotify OAuth callback"""
    # Extract the authorization code from the request
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, "Authorization failed. Please try again.")
        return redirect('spotify_app:index')
    
    messages.success(request, "Successfully authenticated with Spotify!")
    return redirect('spotify_app:step2')

def step1(request):
    """Step 1: Upload image or manually enter songs"""
    if request.method == 'POST':
        if 'manual_songs' in request.POST:
            # Handle manually entered songs
            manual_input = request.POST.get('manual_songs', '')
            songs = {}
            separators = [' - ', '-', '- ', ' -', ' ~ ', '~', ' ~', '~ ']
            
            for line in manual_input.splitlines():
                if not line.strip():
                    continue
                    
                for separator in separators:
                    if separator in line:
                        song, artist = line.split(separator)
                        songs[song.strip()] = artist.strip()
                        break
                else:
                    # If no separator found, assume it's just a song title
                    songs[line.strip()] = None
            
            request.session['songs'] = songs
            return redirect('spotify_app:step2')
            
    return render(request, 'spotify_app/step1.html')

def step2(request):
    """Step 2: Select what to do with the songs"""
    songs = request.session.get('songs', {})
    
    if not songs:
        messages.error(request, "No songs found. Please upload an image or enter songs manually.")
        return redirect('spotify_app:step1')
    
    # Initialize Spotify handler
    spotify = SpotifyHandler()
    
    # Process form submission
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Search for songs on Spotify
        track_ids = spotify.search_for_songs(songs)
        
        if not track_ids:
            messages.warning(request, "No songs were found on Spotify.")
            return render(request, 'spotify_app/step2.html', {'songs': songs})
        
        # Store track IDs in session
        request.session['track_ids'] = track_ids
        
        # Like songs if requested
        if request.POST.get('like_songs') == 'on':
            if spotify.like_songs(track_ids):
                messages.success(request, "Songs have been added to your Liked Songs.")
            else:
                messages.error(request, "Failed to add songs to your Liked Songs.")
        
        # Add to existing playlist
        if action == 'existing_playlist':
            playlist_id = request.POST.get('playlist_id')
            if playlist_id and spotify.add_to_playlist(playlist_id, track_ids):
                messages.success(request, "Songs have been added to the selected playlist.")
                return redirect('spotify_app:completion')
            else:
                messages.error(request, "Failed to add songs to the playlist.")
        
        # Create new playlist
        elif action == 'new_playlist':
            playlist_name = request.POST.get('playlist_name')
            playlist_description = request.POST.get('playlist_description', '')
            
            if playlist_name:
                new_playlist = spotify.create_playlist(playlist_name, playlist_description, track_ids)
                if new_playlist:
                    messages.success(request, f"Created new playlist '{playlist_name}' with your songs.")
                    return redirect('spotify_app:completion')
                else:
                    messages.error(request, "Failed to create the playlist.")
            else:
                messages.error(request, "Please provide a name for your playlist.")
    
    # Get user playlists for display
    try:
        playlists = spotify.get_user_playlists()
        return render(request, 'spotify_app/step2.html', {
            'songs': songs,
            'playlists': playlists['items'] if playlists and 'items' in playlists else []
        })
    except Exception as e:
        logger.error(f"Failed to load Spotify playlists: {str(e)}")
        return render(request, 'spotify_app/step2.html', {'songs': songs})

def completion(request):
    """Completion page after successful operation"""
    return render(request, 'spotify_app/completion.html')

# API endpoints for React app
def get_playlists(request):
    try:
        # Initialize Spotify handler
        spotify = SpotifyHandler()
        playlists = spotify.get_user_playlists()
        
        if playlists and 'items' in playlists:
            formatted_playlists = [
                {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': f"{playlist.get('tracks', {}).get('total', 0)} songs"
                }
                for playlist in playlists['items']
            ]
            return JsonResponse({'playlists': formatted_playlists})
        else:
            return JsonResponse({'playlists': []})
    except Exception as e:
        logger.error(f"Error in get_playlists: {str(e)}")
        return JsonResponse({'playlists': []})

def create_playlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            playlist_name = data.get('name')
            track_ids = data.get('songs', [])
            description = data.get('description', '')
            
            if not playlist_name:
                return JsonResponse({'success': False, 'error': 'Playlist name is required'}, status=400)
                
            # Initialize Spotify handler
            spotify = SpotifyHandler()
            new_playlist = spotify.create_playlist(playlist_name, description, track_ids)
            
            if new_playlist:
                return JsonResponse({'success': True, 'message': 'Playlist created successfully', 'playlist': new_playlist})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to create playlist'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
