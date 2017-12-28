from django.shortcuts import render
from .models import Message

# Create your views here.


def messages(request):
    current_user = request.user
    all_messages = Message.objects.filter(sender=current_user) | Message.objects.filter(recipient=current_user)
    sent_messages = Message.objects.filter(sender=current_user)
    received_messages = Message.objects.filter(recipient=current_user)
    return render(request, 'mnmessages/mnmessages.html', {'all_messages': all_messages,
                                                          'outbox': sent_messages, 'inbox': received_messages})
