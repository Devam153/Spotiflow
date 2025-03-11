from django.shortcuts import render, redirect
from .utils.spotify_handler import SpotifyHandler
from .utils.ocr_handler import OCRHandler

def index(request):
    return render(request, 'index.html')

def step1(request):
    if request.method == 'POST':
        if 'image' in request.FILES:
            image = request.FILES['image']
            ocr_handler = OCRHandler()
            songs = ocr_handler.process_image(image)
            request.session['songs'] = songs
            return redirect('step2')
    return render(request, 'step1.html')

def step2(request):
    spotify = SpotifyHandler()
    playlists = spotify.get_user_playlists()
    songs = request.session.get('songs', [])
    return render(request, 'step2.html', {
        'playlists': playlists,
        'songs': songs
    })
