import logging

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from .utils.spotify_handler import SpotifyHandler, build_oauth
from .utils.ocr_handler import OCRHandler

logger = logging.getLogger(__name__)

SPOTIFY_SESSION_KEYS = (
    'spotify_token_info',
    'spotify_username',
    'spotify_user_id',
)


def _clear_spotify_session(request):
    for key in SPOTIFY_SESSION_KEYS:
        request.session.pop(key, None)


def index(request):
    """Home page view. Clears any prior Spotify auth state."""
    _clear_spotify_session(request)
    return render(request, 'index.html')


def process_image(request):
    """Process uploaded image with OCR"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            songs = OCRHandler().process_image(image)
            request.session['songs'] = songs
            return JsonResponse({'success': True, 'songs': songs})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'No image uploaded'})


def spotify_auth(request):
    """Kick off the Spotify OAuth flow by redirecting to the authorize URL."""
    songs = request.session.get('songs', {})
    if not songs:
        messages.error(request, "No songs found. Please upload an image or enter songs manually.")
        return redirect('spotify_app:step1')

    try:
        auth_url = build_oauth().get_authorize_url()
    except Exception as e:
        logger.error(f"Error generating Spotify auth URL: {e}")
        auth_url = None

    if not auth_url:
        messages.error(request, "Failed to get Spotify authentication URL. Please try again.")
        return redirect('spotify_app:step1')

    logger.info(f"Redirecting user to Spotify auth: {auth_url}")
    return redirect(auth_url)


def spotify_callback(request):
    """Handle Spotify OAuth callback.

    Exchanges the auth code for tokens exactly once with check_cache=False
    so spotipy cannot short-circuit to a cached token. The resulting
    token_info is stored in the user's Django session and the auth code
    is discarded.
    """
    code = request.GET.get('code')
    if not code:
        messages.error(request, "Authorization failed. Please try again.")
        return redirect('spotify_app:step1')

    try:
        token_info = build_oauth().get_access_token(code, check_cache=False)
    except Exception as e:
        logger.error(f"Error exchanging Spotify auth code: {e}")
        messages.error(request, "Failed to complete Spotify authentication. Please try again.")
        return redirect('spotify_app:step1')

    request.session['spotify_token_info'] = token_info

    spotify = SpotifyHandler(token_info)
    user_profile = spotify.get_user_profile()
    if not user_profile:
        messages.error(request, "Failed to retrieve user profile. Please try again.")
        return redirect('spotify_app:step1')

    request.session['spotify_username'] = (
        user_profile.get('display_name') or user_profile.get('id')
    )
    request.session['spotify_user_id'] = user_profile.get('id')

    messages.success(
        request,
        f"Successfully authenticated as {request.session['spotify_username']}!"
    )
    return redirect('spotify_app:step2')


def step1(request):
    """Step 1: Upload image or manually enter songs"""
    if request.method == 'POST' and 'manual_songs' in request.POST:
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
                songs[line.strip()] = None

        request.session['songs'] = songs
        return redirect('spotify_app:spotify_auth')

    return render(request, 'step1.html')


def step2(request):
    """Step 2: Select what to do with the songs"""
    spotify = SpotifyHandler.from_session(request)
    if not spotify:
        messages.warning(request, "Please authenticate with Spotify first.")
        return redirect('spotify_app:spotify_auth')

    songs = request.session.get('songs', {})
    if not songs:
        messages.error(request, "No songs found. Please upload an image or enter songs manually.")
        return redirect('spotify_app:step1')

    if request.method == 'POST':
        action = request.POST.get('action')
        track_ids = spotify.search_for_songs(songs)

        if not track_ids:
            messages.warning(request, "No songs were found on Spotify.")
            return render(request, 'step2.html', {'songs': songs})

        request.session['track_ids'] = track_ids

        if request.POST.get('like_songs') == 'on':
            if spotify.like_songs(track_ids):
                messages.success(request, "Songs have been added to your Liked Songs.")
            else:
                messages.error(request, "Failed to add songs to your Liked Songs.")

        if action == 'existing_playlist':
            playlist_id = request.POST.get('playlist_id')
            if playlist_id and spotify.add_to_playlist(playlist_id, track_ids):
                messages.success(request, "Songs have been added to the selected playlist.")
                return redirect('spotify_app:completion')
            else:
                messages.error(request, "Failed to add songs to the playlist.")

        elif action == 'new_playlist':
            playlist_name = request.POST.get('playlist_name')
            playlist_description = request.POST.get('playlist_description', '')

            if playlist_name:
                new_playlist = spotify.create_playlist(
                    playlist_name, playlist_description, track_ids
                )
                if new_playlist:
                    messages.success(
                        request, f"Created new playlist '{playlist_name}' with your songs."
                    )
                    return redirect('spotify_app:completion')
                else:
                    messages.error(request, "Failed to create the playlist.")
            else:
                messages.error(request, "Please provide a name for your playlist.")

    try:
        spotify_username = request.session.get('spotify_username', 'Spotify User')
        playlists = spotify.get_user_playlists()
        return render(request, 'step2.html', {
            'songs': songs,
            'playlists': playlists['items'] if playlists and 'items' in playlists else [],
            'username': spotify_username,
        })
    except Exception as e:
        logger.error(f"Failed to load Spotify playlists: {e}")
        messages.error(request, f"Failed to load playlists: {e}")
        return render(request, 'step2.html', {'songs': songs})


def completion(request):
    """Completion page after successful operation. Clears Spotify auth state."""
    _clear_spotify_session(request)
    return render(request, 'completion.html')
