from datetime import timedelta

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


def thirty_day_hence():
    return timezone.now() + timezone.timedelta(days=30)


class MovieNight(models.Model):
    title = models.CharField(max_length=100)
    creation_date = models.DateTimeField(default=timezone.now)
    date = models.DateTimeField(default=thirty_day_hence)
    location = models.CharField(max_length=100, default="Home")
    description = models.CharField(max_length=1000, default="This is the description for this MovieNight event, it can be edited by the creator of the event.")
    decoration_url = models.CharField(max_length=1000, default="https://cdn.makeuseof.com/wp-content/uploads/2015/04/movie-theater-revival-setup.jpg")
    list_size = models.IntegerField()
    creator = models.ForeignKey(User)
    users = models.ManyToManyField(User, related_name="participants")
    invited_users = models.ManyToManyField(User, related_name="invited_users", blank=True, null=True)
    declined_users = models.ManyToManyField(User, related_name="declined_users", blank=True, null=True)
    active = models.BooleanField(default=True)
    editable = models.BooleanField(default=True)
    result_viewable = models.BooleanField(default=False)
    result_viewed_users = models.ManyToManyField(User, related_name="result_viewed_users", blank=True, null=True)

    def __str__(self):
        return self.title + ' created by ' + self.creator.username


class ChatMessage(models.Model):
    movienight = models.ForeignKey(MovieNight)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    text = models.CharField(max_length=300)

    def __str__(self):
        return self.author.username + ' - ' + self.movienight.title + '(' + str(self.timestamp) + ')'


class MovieNightList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    users_voted = models.ManyToManyField(User, related_name="users_voted", blank=True, null=True)
    movienight = models.ForeignKey(MovieNight, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie)
    editable = models.BooleanField(default=True)

    def __str__(self):
        return self.movienight.title + ' - ' + self.user.username


class Vote(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    movie_night = models.ForeignKey(MovieNight, on_delete=models.CASCADE)
    movie_list = models.ForeignKey(MovieNightList, on_delete=models.CASCADE)
    points = models.IntegerField()

    def __str__(self):
        return self.user.username + ': ' + self.movie.title + "(" + str(self.points) + " p) - " + self.movie_night.title \
               + "(" + self.movie_list.user.username + ")"