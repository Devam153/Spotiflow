from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .utils.spotify_handler import SpotifyHandler
from .utils.ocr_handler import OCRHandler
import os
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Home page view"""
    # Clear any existing Spotify auth data when returning to home
    if 'spotify_auth_code' in request.session:
        del request.session['spotify_auth_code']
    if 'spotify_auth_started' in request.session:
        del request.session['spotify_auth_started']
    if 'spotify_username' in request.session:
        del request.session['spotify_username']
    if 'spotify_user_id' in request.session:
        del request.session['spotify_user_id']
    if 'spotify_cache_path' in request.session:
        del request.session['spotify_cache_path']
    
    return render(request, 'index.html')

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

def spotify_auth(request):
    """Authenticate with Spotify"""
    # Get songs from session
    songs = request.session.get('songs', {})
    if not songs:
        messages.error(request, "No songs found. Please upload an image or enter songs manually.")
        return redirect('spotify_app:step1')
    
    # Ensure session key exists
    request.session.save()
    
    # Create a unique cache path for this user session
    cache_path = os.path.join(settings.BASE_DIR, f".spotify-cache-{request.session.session_key}.json")
    request.session['spotify_cache_path'] = cache_path
    
    # Initialize Spotify handler with the unique cache path
    spotify = SpotifyHandler(cache_path=cache_path)
    auth_url = spotify.get_auth_url()
    
    if not auth_url:
        messages.error(request, "Failed to get Spotify authentication URL. Please try again.")
        return redirect('spotify_app:step1')
    
    # Store the auth started flag in the session
    request.session['spotify_auth_started'] = True
    
    # Redirect to Spotify authorization page
    logger.info(f"Redirecting user to Spotify auth: {auth_url}")
    return redirect(auth_url)

def spotify_callback(request):
    """Handle Spotify OAuth callback"""
    # Extract the authorization code from the request
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, "Authorization failed. Please try again.")
        return redirect('spotify_app:step1')
    
    # Get the cache path from the session
    cache_path = request.session.get('spotify_cache_path')
    
    # Store the authorization code in the session for user-specific authentication
    request.session['spotify_auth_code'] = code
    request.session['spotify_auth_started'] = True
    
    # Complete authentication and get user profile
    spotify = SpotifyHandler(auth_code=code, cache_path=cache_path)
    user_profile = spotify.get_user_profile()
    
    if user_profile:
        # Store user-specific information in session
        request.session['spotify_username'] = user_profile.get('display_name') or user_profile.get('id')
        request.session['spotify_user_id'] = user_profile.get('id')
        
        messages.success(request, f"Successfully authenticated as {request.session['spotify_username']}!")
        return redirect('spotify_app:step2')
    else:
        messages.error(request, "Failed to retrieve user profile. Please try again.")
        return redirect('spotify_app:step1')

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
            # After processing songs, redirect to Spotify auth instead of step2
            return redirect('spotify_app:spotify_auth')
            
    return render(request, 'step1.html')

def step2(request):
    """Step 2: Select what to do with the songs"""
    # Check if user is authenticated with Spotify
    if not request.session.get('spotify_auth_code'):
        messages.warning(request, "Please authenticate with Spotify first.")
        return redirect('spotify_app:spotify_auth')
    
    # Get songs from session
    songs = request.session.get('songs', {})
    if not songs:
        messages.error(request, "No songs found. Please upload an image or enter songs manually.")
        return redirect('spotify_app:step1')
    
    # Get the cache path from the session
    cache_path = request.session.get('spotify_cache_path')
    
    # Initialize Spotify handler with user's specific auth code and cache path
    spotify = SpotifyHandler(
        auth_code=request.session.get('spotify_auth_code'),
        cache_path=cache_path
    )
    
    # Process form submission
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Search for songs on Spotify
        track_ids = spotify.search_for_songs(songs)
        
        if not track_ids:
            messages.warning(request, "No songs were found on Spotify.")
            return render(request, 'step2.html', {'songs': songs})
        
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
        spotify_username = request.session.get('spotify_username', 'Spotify User')
        playlists = spotify.get_user_playlists()
        return render(request, 'step2.html', {
            'songs': songs,
            'playlists': playlists['items'] if playlists and 'items' in playlists else [],
            'username': spotify_username
        })
    except Exception as e:
        logger.error(f"Failed to load Spotify playlists: {str(e)}")
        messages.error(request, f"Failed to load playlists: {str(e)}")
        return render(request, 'step2.html', {'songs': songs})

def completion(request):
    """Completion page after successful operation"""
    # Clear auth data on completion
    if 'spotify_auth_code' in request.session:
        del request.session['spotify_auth_code']
    if 'spotify_auth_started' in request.session:
        del request.session['spotify_auth_started']
    if 'spotify_cache_path' in request.session:
        # Consider deleting the cache file here as well for cleanup
        cache_path = request.session.get('spotify_cache_path')
        if cache_path and os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except Exception as e:
                logger.error(f"Error removing cache file: {str(e)}")
        del request.session['spotify_cache_path']
    
    return render(request, 'completion.html')