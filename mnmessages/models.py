from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    recipient = models.ForeignKey(User, related_name='receiver')
    title = models.CharField(max_length=50)
    message = models.CharField(max_length=10000)
    date = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.sender.username + ' -> ' + self.recipient.username + ' (' + str(self.date) + ')'
