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
    shown_to_sender = models.BooleanField(default=True)
    shown_to_recipient = models.BooleanField(default=True)

    def __str__(self):
        return self.sender.username + ' -> ' + self.recipient.username + ' (' + str(self.date) + ')'
