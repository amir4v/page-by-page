from django.shortcuts import render

# Create your views here.
# chat/views.py
from django.shortcuts import render


def index(request):
    return render(request, "room/index.html")
# chat/views.py
from django.shortcuts import render



def room(request, room_name):
    return render(request, "room/room.html", {"room_name": room_name})

