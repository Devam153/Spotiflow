from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name = 'start'),
    path('1', views.step1, name = 'step1'),
    path('2', views.step2, name = 'step2'),
    path('3', views.end, name = 'end')
    
]