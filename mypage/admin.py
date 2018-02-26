from django.contrib import admin
from .models import Movie, MovieBacklog, MovieNight, MovieNightList, Friends, Vote, ChatMessage, BlogPost, \
    BlogPostComment

admin.site.register(Movie)
admin.site.register(MovieBacklog)
admin.site.register(MovieNight)
admin.site.register(MovieNightList)
admin.site.register(Friends)
admin.site.register(Vote)
admin.site.register(ChatMessage)
admin.site.register(BlogPost)
admin.site.register(BlogPostComment)
