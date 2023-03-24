from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("upload/", views.upload),
    path("show/<int:pk>/", views.show),
    path("get-page/<int:pk>/<int:page_number>/", views.get_page),
    # path("room/<str:token>/", views.room),
]
