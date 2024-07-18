from django.shortcuts import render

# Create your views here.
def start(request):
    return render(request, 'spotiflowapp/start.html')

def step1(request):
    return render(request, 'spotiflowapp/step1.html')

def step2(request):
    return render(request, 'spotiflowapp/step2.html')

def end(request):
    return render(request, 'spotiflowapp/end.html')