from django.contrib import admin
from .models import Movie
from .models import MovieBacklog
from .models import MovieNight

admin.site.register(Movie)
admin.site.register(MovieBacklog)
admin.site.register(MovieNight)
