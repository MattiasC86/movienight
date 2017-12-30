from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Message

# Create your views here.


def messages(request):
    unread_messages = Message.objects.filter(recipient=request.user, read=False)
    all_messages = Message.objects.filter(sender=request.user).order_by('-date') | Message.objects.filter(recipient=request.user).order_by('-date')
    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(recipient=request.user)
    return render(request, 'mnmessages/mnmessages.html', {'all_messages': all_messages, 'unread': unread_messages,
                                                          'outbox': sent_messages, 'inbox': received_messages})

# TODO add error message in html file for wrong username
def send_message(request):
    if request.method == "POST":
        recipient = request.POST['recipient']
        subject = request.POST['subject']
        content = request.POST['content']

        try:
            new_recipient = User.objects.get(username=recipient)
        except User.DoesNotExist:
            return render(request, 'mnmessages/mnmessages.html', {
                'error_message': 'Username does not exist', })

        new_message = Message(sender=request.user, recipient=new_recipient, title=subject, message=content)
        new_message.save()
        return redirect('messages:messages')


def read_message(request):
    message_pk = request.POST.get('messageToUpdate', None)
    message_update = Message.objects.get(pk=message_pk)
    message_update.read = True
    message_update.save()
    return HttpResponse('Read!')
    #return redirect('messages:messages')