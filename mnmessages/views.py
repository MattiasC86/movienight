from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Message, Friend


# Create your views here.


def messages(request):
    friends = Friend.objects.filter(user=request.user)
    unread_messages = Message.objects.filter(recipient=request.user, read=False)
    all_messages = Message.objects.filter(sender=request.user).order_by('-date') | Message.objects.filter(recipient=request.user).order_by('-date')
    sent_messages = Message.objects.filter(sender=request.user, shown_to_sender=True)
    received_messages = Message.objects.filter(recipient=request.user, shown_to_recipient=True)

    if request.method == 'POST':
        print(request.POST)
        if request.POST['action'] == 'delete_msgs':
            in_msgs_to_delete = request.POST.getlist('in_msgs[]')
            out_msgs_to_delete = request.POST.getlist('out_msgs[]')

            for m in in_msgs_to_delete:
                message = Message.objects.get(pk=m)
                message.shown_to_recipient = False
                message.save()
                if not message.shown_to_sender:
                    message.delete()

            for m in out_msgs_to_delete:
                message = Message.objects.get(pk=m)
                message.shown_to_sender = False
                message.save()
                if not message.shown_to_recipient:
                    message.delete()


            #for m in msgs_to_delete:
            #    Message.objects.get(pk=m).delete()
            #return HttpResponse("Deletion complete")

    return render(request, 'mnmessages/mnmessages.html', {'all_messages': all_messages, 'unread': unread_messages,
                                                          'outbox': sent_messages, 'inbox': received_messages,
                                                          'friends': friends})


# TODO add error message in html file for wrong username
def send_message(request):
    if request.method == "POST":
        recipient = request.POST['recipient']
        subject = request.POST['subject']
        content = request.POST['content']

        try:
            new_recipient = User.objects.get(username__iexact=recipient)
        except User.DoesNotExist:
            return JsonResponse({'error': 'UserDoesNotExist'})

        new_message = Message(sender=request.user, recipient=new_recipient, title=subject, message=content)
        new_message.save()
        return redirect('interaction:messages')


def read_message(request):
    message_pk = request.POST.get('messageToUpdate', None)
    message_update = Message.objects.get(pk=message_pk)
    message_update.read = True
    message_update.save()
    return HttpResponse('Read!')
    #return redirect('messages:messages')


def friends_list(request):

    friends = Friend.objects.filter(user=request.user)

    if request.method == 'POST':
        if request.POST['action'] == 'return_user':
            username = request.POST['username']
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                user = None

            if user:
                user_json = {'pk': user.pk, 'username': user.username}
                return JsonResponse(user_json, safe=False)
            else:
                return JsonResponse({'error': 'noUserFound'})
        elif request.POST['action'] == 'add_friend':
            user_pk = request.POST['user_pk']
            other_user = User.objects.get(pk=user_pk)
            try:
                friend = Friend.objects.get(user=request.user, friend=other_user)
            except Friend.DoesNotExist:
                friend = None

            if friend:
                return JsonResponse({'error': 'alreadyFriend'})
            else:
                new_friend = Friend(user=request.user, friend=other_user)
                new_friend.save()
                new_friend_json = {'pk': new_friend.friend.pk, 'username': new_friend.friend.username}
                return JsonResponse(new_friend_json)
        elif request.POST['action'] == 'delete_friend':
            friend_user_to_delete = User.objects.get(username__iexact=request.POST['username'])
            friend_to_delete = Friend.objects.get(user=request.user, friend=friend_user_to_delete)
            friend_to_delete.delete()
            friends = Friend.objects.filter(user=request.user)
            if friends.count() == 0:
                return HttpResponse("zeroFriends")

    return render(request, 'mnmessages/friendslist.html', {'friends': friends})
