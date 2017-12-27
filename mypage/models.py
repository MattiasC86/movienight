from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


#class User(AbstractUser):
#    name = models.CharField(max_length=100, blank=True, null=True)
#
#    def __str__(self):
#        return self.username + ' (' + self.email + ')'
from django.db.models.functions import datetime


class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='first_user')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')

    def __str__(self):
        return self.user.username + ' - ' + self.user2.username


class Movie(models.Model):
    title = models.CharField(max_length=100)
    release_year = models.CharField(max_length=4)
    director = models.CharField(max_length=100)
    plot = models.CharField(max_length=1500)
    poster = models.CharField(max_length=1000)

    def __str__(self):
        return self.title + ' (' + self.release_year + ')'


class MovieBacklog(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ' - ' + self.movie.title


class MovieNight(models.Model):
    title = models.CharField(max_length=100)
    creation_date = models.DateTimeField(default=timezone.now)
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=1000, default="This is the description for this MovieNight event, it can be edited by the creator of the event.")
    decoration_url = models.CharField(max_length=1000, default="https://cdn.makeuseof.com/wp-content/uploads/2015/04/movie-theater-revival-setup.jpg")
    list_size = models.IntegerField()
    creator = models.ForeignKey(User)
    users = models.ManyToManyField(User, related_name="participants")

    def __str__(self):
        return self.title + ' created by ' + self.creator.username


class MovieNightList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movienight = models.ForeignKey(MovieNight, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie)

    def __str__(self):
        return self.movienight.title + ' - ' + self.user.username

