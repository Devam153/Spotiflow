from django.urls import path
from . import views

app_name = 'spotify_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('step1/', views.step1, name='step1'),
    path('step2/', views.step2, name='step2'),
    path('spotify-auth/', views.spotify_auth, name='spotify_auth'),
    path('completion/', views.completion, name='completion'),
    path('process-image/', views.process_image, name='process_image'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    
    # API endpoints for React app
    path('api/playlists/', views.get_playlists, name='get_playlists'),
    path('api/create-playlist/', views.create_playlist, name='create_playlist'),
]
