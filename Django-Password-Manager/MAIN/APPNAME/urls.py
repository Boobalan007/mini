from unicodedata import name
from django.urls import path
from .views import github, gmail, home, linkedin, maps, youtube
urlpatterns = [
    path("", home, name="home"),
    path("youtube.com",youtube),
    path("github.com",github),
    path("linkedin.com",linkedin),
    path("gmail.com",gmail),
    path("maps.com",maps)

]