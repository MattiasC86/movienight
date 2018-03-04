from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend')

    def __str__(self):
        return self.user.username + ' - ' + self.friend.username


class FriendRequest(models.Model):
    date = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_of_request')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_of_request')



class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    recipient = models.ForeignKey(User, related_name='recipient')
    title = models.CharField(max_length=50)
    message = models.CharField(max_length=10000)
    date = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    shown_to_sender = models.BooleanField(default=True)
    shown_to_recipient = models.BooleanField(default=True)

    def __str__(self):
        return self.sender.username + ' -> ' + self.recipient.username + ' (' + str(self.date) + ')'