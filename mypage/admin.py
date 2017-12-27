from django.contrib import admin
from .models import Movie, MovieBacklog, MovieNight, MovieNightList

admin.site.register(Movie)
admin.site.register(MovieBacklog)
admin.site.register(MovieNight)
admin.site.register(MovieNightList)
