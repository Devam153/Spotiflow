
from django.urls import path
from . import views

app_name = 'spotify_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('process-image/', views.process_image, name='process_image'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
]
